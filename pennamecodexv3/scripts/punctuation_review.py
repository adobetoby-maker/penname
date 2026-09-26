#!/usr/bin/env python3
"""Create resumable, word-locked punctuation reviews for fiction manuscripts."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import subprocess
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORD_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", re.UNICODE)
PARAGRAPH_SPLIT_RE = re.compile(r"(\n[ \t]*\n)")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])(?:[\"”’')\]]*)\s+")
EM_DASH_WITH_SPACING_RE = re.compile(r"([ \t]*)—([ \t]*)")

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["chapterAssessment", "edits"],
    "properties": {
        "chapterAssessment": {"type": "string"},
        "edits": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["paragraphIndex", "editedParagraph", "reason"],
                "properties": {
                    "paragraphIndex": {"type": "integer", "minimum": 1},
                    "editedParagraph": {"type": "string"},
                    "reason": {"type": "string"},
                },
            },
        },
    },
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def words(value: str) -> list[str]:
    return [match.group(0).casefold().replace("’", "'") for match in WORD_RE.finditer(value)]


DROPPABLE_CONJUNCTIONS = {"and", "but", "or", "so", "yet", "nor", "for"}


def punctuation_only(original: str, edited: str) -> tuple[bool, str]:
    before = words(original)
    after = words(edited)
    if before != after:
        # Narrow, auditable exception: splitting a run-on into two sentences
        # often reads better with the leading coordinating conjunction dropped
        # ("X, and Y." -> "X. Y." rather than "X. And Y."). Allow ONLY single-
        # word deletions of a closed set of coordinating conjunctions; no word
        # may ever be added, replaced, or reordered.
        matcher = difflib.SequenceMatcher(a=before, b=after, autojunk=False)
        dropped_conjunctions = 0
        violation = None
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            if tag == "delete" and (i2 - i1) == 1 and before[i1] in DROPPABLE_CONJUNCTIONS:
                dropped_conjunctions += 1
                continue
            violation = (tag, i1, i2, j1, j2)
            break
        if violation is not None:
            tag, i1, i2, j1, j2 = violation
            return False, (
                f"word sequence changed ({tag} at original token {i1 + 1}); "
                f"original={len(before)} words edited={len(after)} words"
            )
        if dropped_conjunctions == 0:
            # before != after but no diff found a real change (shouldn't happen)
            return False, (
                f"word sequence changed; original={len(before)} words "
                f"edited={len(after)} words"
            )
    for marker in ("*", "_", "`", "#"):
        if original.count(marker) != edited.count(marker):
            return False, f"Markdown marker count changed for {marker!r}"
    original_breaks = sum(line.strip() == "---" for line in original.splitlines())
    edited_breaks = sum(line.strip() == "---" for line in edited.splitlines())
    if original_breaks != edited_breaks:
        return False, "Markdown scene-break count changed"
    return True, "word sequence and Markdown emphasis preserved"


def preserve_existing_em_dash_spacing(original: str, edited: str) -> str:
    """Keep the source spacing around existing em dashes in a word-locked edit."""
    original_words = list(WORD_RE.finditer(original))
    edited_words = list(WORD_RE.finditer(edited))
    if len(original_words) != len(edited_words):
        return edited

    def gaps(value: str, matches: list[re.Match[str]]) -> list[str]:
        if not matches:
            return [value]
        return [value[: matches[0].start()]] + [
            value[left.end() : right.start()]
            for left, right in zip(matches, matches[1:])
        ] + [value[matches[-1].end() :]]

    source_gaps = gaps(original, original_words)
    candidate_gaps = gaps(edited, edited_words)
    repaired_gaps: list[str] = []
    for source_gap, candidate_gap in zip(source_gaps, candidate_gaps):
        source_dashes = list(EM_DASH_WITH_SPACING_RE.finditer(source_gap))
        candidate_dashes = list(EM_DASH_WITH_SPACING_RE.finditer(candidate_gap))
        if not source_dashes or len(source_dashes) != len(candidate_dashes):
            repaired_gaps.append(candidate_gap)
            continue
        styles = [(match.group(1), match.group(2)) for match in source_dashes]
        style_index = 0

        def restore(match: re.Match[str]) -> str:
            nonlocal style_index
            left, right = styles[style_index]
            style_index += 1
            return f"{left}—{right}"

        repaired_gaps.append(EM_DASH_WITH_SPACING_RE.sub(restore, candidate_gap))

    output = [repaired_gaps[0]]
    for index, match in enumerate(edited_words):
        output.append(match.group(0))
        output.append(repaired_gaps[index + 1])
    return "".join(output)


def chapter_metrics(value: str) -> dict[str, Any]:
    body = "\n".join(line for line in value.splitlines() if not line.startswith("#"))
    sentence_lengths = [
        len(words(sentence))
        for sentence in SENTENCE_SPLIT_RE.split(body)
        if words(sentence)
    ]
    paragraph_lengths = [
        len(words(part))
        for part in re.split(r"\n\s*\n", body)
        if words(part) and part.strip() != "---"
    ]
    ordered = sorted(sentence_lengths)
    p90 = ordered[round(0.9 * (len(ordered) - 1))] if ordered else 0
    return {
        "words": len(words(body)),
        "sentences": len(sentence_lengths),
        "sentenceMedianWords": ordered[len(ordered) // 2] if ordered else 0,
        "sentenceP90Words": p90,
        "sentencesOver45Words": sum(length > 45 for length in sentence_lengths),
        "longestSentenceWords": max(sentence_lengths, default=0),
        "paragraphsOver100Words": sum(length > 100 for length in paragraph_lengths),
    }


def split_document(raw: str) -> tuple[list[str], list[str]]:
    parts = PARAGRAPH_SPLIT_RE.split(raw)
    paragraphs = parts[0::2]
    separators = parts[1::2]
    return paragraphs, separators


def join_document(paragraphs: list[str], separators: list[str]) -> str:
    output: list[str] = []
    for index, paragraph in enumerate(paragraphs):
        output.append(paragraph)
        if index < len(separators):
            output.append(separators[index])
    return "".join(output)


def make_prompt(raw: str) -> str:
    paragraphs, _ = split_document(raw)
    metrics = chapter_metrics(raw)
    numbered = "\n\n".join(
        f"P{index:04d}\n{paragraph}"
        for index, paragraph in enumerate(paragraphs, start=1)
    )
    return f"""You are the punctuation editor for a finished fiction manuscript that will be
narrated by a text-to-speech reader for an audiobook. Read the entire chapter before
proposing edits. Your primary job is pacing for a listener, not silent-reading
grammar: a listener cannot re-read a sentence that ran past them, and every comma,
semicolon, period, and em dash you place or leave in the text is read by the narrator
as an actual pause of a different length. Punctuation choice IS pacing direction.
Judge each sentence by whether its punctuation marks the real boundaries a listener
needs — a new independent clause, a subordinate aside, a returned thought — with a
pause of the right weight, not by whether a silent reader could eventually untangle it
with effort.

NON-NEGOTIABLE WORD LOCK
- Keep every word in exactly the same order within its numbered paragraph.
- Do not add, replace, or move a word.
- The one exception: when you split a run-on into two sentences, you may drop the
  leading coordinating conjunction (and, but, or, so, yet, nor, for) that would
  otherwise awkwardly start the second sentence — "X, and Y." may become "X. Y.",
  not just "X. And Y." Do not drop any other word for any other reason.
- You may change punctuation, quotation punctuation, capitalization, and paragraph breaks.
- Preserve Markdown headings, italics, bold, and scene-break markers.
- Do not modernize spelling or replace a writer's vocabulary.

EDITORIAL STANDARD
Add punctuation so each paragraph reads clearly and paces naturally when read aloud
by the narrator. Preserve the original wording, meaning, and literary tone completely
— you are punctuating, not rewriting. You may split run-on sentences and add commas,
semicolons, periods, or em dashes wherever they would help a listener follow the
sentence's structure at listening speed. Identify the sentence's main ideas and
separate them into readable units; use punctuation to preserve its deliberate rhythm,
not flatten it into uniform short sentences.

One thing to hold onto while you do this: preserve the manuscript's established
spaced-em-dash typography — don't close up an existing spaced em dash or normalize
its surrounding spaces. Otherwise, punctuate decisively. The word lock guarantees
nothing about meaning or wording can be lost here — only pacing changes — so there is
no cost to being thorough. This chapter contains {metrics['sentencesOver45Words']}
detected sentences over 45 words and {metrics['paragraphsOver100Words']} paragraphs
over 100 words; every one of them should very likely be repunctuated for a listener.

If one source paragraph needs a paragraph break, place a blank line inside
editedParagraph while preserving its complete word sequence.

Return each changed paragraph with its integer paragraphIndex, the complete revised text
in editedParagraph, and one concise reason. Never return a sentence fragment or excerpt.
An empty edits array is correct for a clean chapter.

CHAPTER

{numbered}
"""


def ollama_review(
    raw: str,
    model: str,
    url: str,
    retries: int,
) -> dict[str, Any]:
    prompt = make_prompt(raw)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return only data matching the JSON schema. Be a conservative fiction "
                    "punctuation editor. The exact word lock is mandatory."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "format": OUTPUT_SCHEMA,
        "think": False,
        "keep_alive": "45m",
        "options": {"temperature": 0.05, "num_ctx": 32768},
    }
    endpoint = url.rstrip("/") + "/api/chat"
    for attempt in range(1, retries + 1):
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=900) as response:
                result = json.loads(response.read().decode("utf-8"))
            return json.loads(result["message"]["content"])
        except (urllib.error.URLError, KeyError, json.JSONDecodeError) as error:
            if attempt >= retries:
                raise RuntimeError(f"Ollama review failed after {attempt} attempts: {error}") from error
            time.sleep(attempt * 3)
    raise AssertionError("unreachable")


def codex_review(
    raw: str,
    model: str,
    retries: int,
    reasoning_effort: str,
) -> dict[str, Any]:
    prompt = make_prompt(raw)
    for attempt in range(1, retries + 1):
        try:
            with tempfile.TemporaryDirectory(prefix="monroe-punctuation-") as temp_dir:
                schema_path = Path(temp_dir) / "schema.json"
                result_path = Path(temp_dir) / "result.json"
                schema_path.write_text(json.dumps(OUTPUT_SCHEMA), encoding="utf-8")
                command = [
                    "codex",
                    "exec",
                    "--model",
                    model,
                    "--ephemeral",
                    "--sandbox",
                    "read-only",
                    "--skip-git-repo-check",
                    "--output-schema",
                    str(schema_path),
                    "--output-last-message",
                    str(result_path),
                    "-c",
                    f'model_reasoning_effort="{reasoning_effort}"',
                    "-",
                ]
                completed = subprocess.run(
                    command,
                    input=prompt,
                    text=True,
                    capture_output=True,
                    timeout=900,
                )
                if completed.returncode:
                    raise RuntimeError(
                        f"Codex exited {completed.returncode}: {completed.stderr.strip()}"
                    )
                return json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError, RuntimeError) as error:
            if attempt >= retries:
                raise RuntimeError(f"Codex review failed after {attempt} attempts: {error}") from error
            time.sleep(attempt * 3)
    raise AssertionError("unreachable")


def review_file(
    source: Path,
    output_root: Path,
    repo_root: Path,
    repo_id: str,
    model: str,
    backend: str,
    url: str,
    retries: int,
    reasoning_effort: str,
    force: bool,
) -> dict[str, Any]:
    relative = source.resolve().relative_to(repo_root.resolve())
    destination_base = output_root / repo_id / relative
    candidate_path = destination_base.with_suffix(".punctuation-review.md")
    diff_path = destination_base.with_suffix(".punctuation-review.diff")
    report_path = destination_base.with_suffix(".punctuation-review.json")
    source_bytes = source.read_bytes()
    source_hash = sha256_bytes(source_bytes)
    if report_path.exists() and not force:
        existing = json.loads(report_path.read_text(encoding="utf-8"))
        if existing.get("sourceSha256") == source_hash:
            print(f"resume {repo_id}:{relative}", flush=True)
            return existing

    raw = source_bytes.decode("utf-8")
    print(f"review {repo_id}:{relative}", flush=True)
    directed = (
        codex_review(raw, model, retries, reasoning_effort)
        if backend == "codex"
        else ollama_review(raw, model, url, retries)
    )
    paragraphs, separators = split_document(raw)
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    seen: set[int] = set()
    for edit in directed.get("edits", []):
        index = int(edit.get("paragraphIndex", 0))
        edited = str(edit.get("editedParagraph", ""))
        edited_words = words(edited)
        index_matches_words = (
            1 <= index <= len(paragraphs)
            and words(paragraphs[index - 1]) == edited_words
        )
        if not index_matches_words:
            matches = [
                candidate_index
                for candidate_index, paragraph in enumerate(paragraphs, start=1)
                if words(paragraph) == edited_words
            ]
            if len(matches) == 1:
                index = matches[0]
        if index in seen or not 1 <= index <= len(paragraphs):
            rejected.append({**edit, "rejection": "duplicate or invalid paragraph index"})
            continue
        if words(paragraphs[index - 1]) != edited_words:
            rejected.append(
                {
                    **edit,
                    "rejection": (
                        "editedParagraph is not a complete source paragraph with the "
                        "same word sequence"
                    ),
                }
            )
            continue
        seen.add(index)
        original = paragraphs[index - 1]
        valid, validation = punctuation_only(original, edited)
        if not valid:
            rejected.append({**edit, "rejection": validation})
            continue
        edited = preserve_existing_em_dash_spacing(original, edited)
        if edited == original:
            continue
        paragraphs[index - 1] = edited
        accepted.append(
            {
                "paragraphIndex": index,
                "originalParagraph": original,
                "editedParagraph": edited,
                "reason": str(edit.get("reason", "")),
                "validation": validation,
            }
        )

    candidate = join_document(paragraphs, separators)
    whole_valid, whole_validation = punctuation_only(raw, candidate)
    if not whole_valid:
        raise RuntimeError(f"Whole-chapter word lock failed: {whole_validation}")
    before_metrics = chapter_metrics(raw)
    after_metrics = chapter_metrics(candidate)
    unified = "".join(
        difflib.unified_diff(
            raw.splitlines(keepends=True),
            candidate.splitlines(keepends=True),
            fromfile=str(source),
            tofile=str(candidate_path),
        )
    )
    report = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "repoId": repo_id,
        "repoRoot": str(repo_root.resolve()),
        "source": str(source.resolve()),
        "relativeSource": str(relative),
        "sourceSha256": source_hash,
        "candidateSha256": sha256_bytes(candidate.encode("utf-8")),
        "model": model,
        "backend": backend,
        "reasoningEffort": reasoning_effort if backend == "codex" else None,
        "chapterAssessment": str(directed.get("chapterAssessment", "")),
        "acceptedEditCount": len(accepted),
        "rejectedEditCount": len(rejected),
        "acceptedEdits": accepted,
        "rejectedEdits": rejected,
        "wholeChapterValidation": whole_validation,
        "beforeMetrics": before_metrics,
        "afterMetrics": after_metrics,
        "candidate": str(candidate_path),
        "diff": str(diff_path),
        "status": "changed" if accepted else "clean-or-no-safe-change",
    }
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_text(candidate, encoding="utf-8")
    diff_path.write_text(unified, encoding="utf-8")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"  accepted={len(accepted)} rejected={len(rejected)} "
        f">45w {before_metrics['sentencesOver45Words']}→{after_metrics['sentencesOver45Words']}",
        flush=True,
    )
    return report


def load_manifest(path: Path) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("chapters")
    if not isinstance(entries, list):
        raise RuntimeError("Manifest needs a chapters array")
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--backend", choices=["ollama", "codex"], default="ollama")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument(
        "--reasoning-effort",
        choices=["low", "medium", "high", "xhigh", "max", "ultra"],
        default="high",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    if args.model is None:
        # Backend-specific defaults: an Ollama model tag is rejected outright
        # by the Codex CLI (and vice versa), so there is no safe single default.
        args.model = "qwen3.5:9b" if args.backend == "ollama" else "gpt-5.6-sol"

    entries = load_manifest(args.manifest)
    if args.limit is not None:
        entries = entries[: args.limit]
    summary = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "manifest": str(args.manifest.resolve()),
        "model": args.model,
        "backend": args.backend,
        "reasoningEffort": args.reasoning_effort if args.backend == "codex" else None,
        "chapters": 0,
        "changed": 0,
        "cleanOrNoSafeChange": 0,
        "acceptedEdits": 0,
        "rejectedEdits": 0,
        "failures": [],
    }
    for entry in entries:
        try:
            report = review_file(
                Path(entry["source"]),
                args.output_root,
                Path(entry["repoRoot"]),
                entry["repoId"],
                args.model,
                args.backend,
                args.ollama_url,
                args.retries,
                args.reasoning_effort,
                args.force,
            )
        except Exception as error:  # continue a library-sized resumable run
            print(f"FAILED {entry.get('source')}: {error}", file=sys.stderr, flush=True)
            summary["failures"].append({"source": entry.get("source"), "error": str(error)})
            continue
        summary["chapters"] += 1
        summary["acceptedEdits"] += int(report["acceptedEditCount"])
        summary["rejectedEdits"] += int(report["rejectedEditCount"])
        if report["status"] == "changed":
            summary["changed"] += 1
        else:
            summary["cleanOrNoSafeChange"] += 1

    args.output_root.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_root / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(summary_path)
    return 1 if summary["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

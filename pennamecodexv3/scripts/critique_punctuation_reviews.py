#!/usr/bin/env python3
"""Run a conservative second-pass critic over word-locked punctuation proposals."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REVIEW_SCRIPT = Path(__file__).with_name("punctuation_review.py")
SPEC = importlib.util.spec_from_file_location("punctuation_review", REVIEW_SCRIPT)
assert SPEC and SPEC.loader
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)

CRITIC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["batchAssessment", "decisions"],
    "properties": {
        "batchAssessment": {"type": "string"},
        "decisions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["editId", "accept", "reason"],
                "properties": {
                    "editId": {"type": "string"},
                    "accept": {"type": "boolean"},
                    "reason": {"type": "string"},
                },
            },
        },
    },
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def collect_reports(roots: list[Path]) -> list[Path]:
    reports: list[Path] = []
    for root in roots:
        reports.extend(root.rglob("*.punctuation-review.json"))
    return sorted(set(reports))


def candidate_paragraph_for_source(
    source_raw: str,
    candidate_raw: str,
    paragraph_index: int,
) -> tuple[str, str, str]:
    source_paragraphs, source_separators = REVIEW.split_document(source_raw)
    if not 1 <= paragraph_index <= len(source_paragraphs):
        raise RuntimeError(f"invalid source paragraph {paragraph_index}")
    original = source_paragraphs[paragraph_index - 1]
    source_matches = list(REVIEW.WORD_RE.finditer(source_raw))
    candidate_matches = list(REVIEW.WORD_RE.finditer(candidate_raw))
    original_matches = list(REVIEW.WORD_RE.finditer(original))
    if not original_matches:
        raise RuntimeError(f"paragraph {paragraph_index} has no words")

    # Count through the actual source document so headings and separators remain aligned.
    paragraph_start = sum(
        len(source_paragraphs[index]) + len(source_separators[index])
        for index in range(paragraph_index - 1)
    )
    start_word = sum(match.start() < paragraph_start for match in source_matches)
    end_word = start_word + len(original_matches) - 1
    if end_word >= len(candidate_matches):
        raise RuntimeError("candidate word alignment is incomplete")

    first = candidate_matches[start_word]
    last = candidate_matches[end_word]
    start = candidate_raw.rfind("\n\n", 0, first.start())
    start = 0 if start < 0 else start + 2
    end = candidate_raw.find("\n\n", last.end())
    end = len(candidate_raw) if end < 0 else end
    revised = candidate_raw[start:end]
    if REVIEW.words(original) != REVIEW.words(revised):
        raise RuntimeError(f"could not recover candidate paragraph {paragraph_index}")

    previous = source_paragraphs[paragraph_index - 2] if paragraph_index > 1 else ""
    following = (
        source_paragraphs[paragraph_index]
        if paragraph_index < len(source_paragraphs)
        else ""
    )
    return original, revised, f"BEFORE: {previous}\nAFTER: {following}"


def make_items(
    report_paths: list[Path],
    allowed_sources: set[str] | None = None,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    item_number = 0
    reports_by_source: dict[str, tuple[Path, dict[str, Any]]] = {}
    for report_path in report_paths:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        source = str(report["source"])
        if allowed_sources is not None and source not in allowed_sources:
            continue
        current = reports_by_source.get(source)
        if current is None or str(report.get("generatedAt", "")) > str(
            current[1].get("generatedAt", "")
        ):
            reports_by_source[source] = (report_path, report)

    for report_path, report in sorted(
        reports_by_source.values(),
        key=lambda pair: str(pair[1]["source"]),
    ):
        if not int(report.get("acceptedEditCount", 0)):
            continue
        source_path = Path(report["source"])
        candidate_path = Path(report["candidate"])
        source_raw = source_path.read_text(encoding="utf-8")
        candidate_raw = candidate_path.read_text(encoding="utf-8")
        if sha256_text(source_raw) != report["sourceSha256"]:
            raise RuntimeError(f"source changed after review: {source_path}")
        if sha256_text(candidate_raw) != report["candidateSha256"]:
            raise RuntimeError(f"candidate hash mismatch: {candidate_path}")
        for edit in report.get("acceptedEdits", []):
            item_number += 1
            index = int(edit["paragraphIndex"])
            original = edit.get("originalParagraph")
            revised = edit.get("editedParagraph")
            if original is None or revised is None:
                original, revised, context = candidate_paragraph_for_source(
                    source_raw,
                    candidate_raw,
                    index,
                )
            else:
                source_paragraphs, _ = REVIEW.split_document(source_raw)
                previous = source_paragraphs[index - 2] if index > 1 else ""
                following = source_paragraphs[index] if index < len(source_paragraphs) else ""
                context = f"BEFORE: {previous}\nAFTER: {following}"
            items.append(
                {
                    "editId": f"E{item_number:06d}",
                    "report": str(report_path),
                    "source": str(source_path),
                    "paragraphIndex": index,
                    "originalParagraph": original,
                    "editedParagraph": revised,
                    "proposerReason": edit.get("reason", ""),
                    "context": context,
                }
            )
    return items


def critic_prompt(items: list[dict[str, Any]]) -> str:
    rendered = []
    for item in items:
        rendered.append(
            "\n".join(
                [
                    f"EDIT {item['editId']}",
                    f"SOURCE {item['source']}",
                    f"PROPOSER REASON: {item['proposerReason']}",
                    "ORIGINAL:",
                    item["originalParagraph"],
                    "REVISED:",
                    item["editedParagraph"],
                    "NEIGHBOR CONTEXT:",
                    item["context"],
                ]
            )
        )
    return """You are the final senior copy editor for finished commercial fiction.
Evaluate each proposed punctuation-only revision independently. Accept only when the
revision is clearly better for meaning, grammar, silent reading, and expressive narration.

Reject a proposal when it:
- changes or muddies the intended meaning or attachment;
- inserts a comma, semicolon, colon, or sentence break that is merely optional or awkward;
- flattens an intentional fragment, repetition, accumulation, dry beat, or character voice;
- changes established spaced-em-dash typography or manufactures dramatic emphasis;
- treats every long sentence as a fault rather than judging its controlled cadence.

Accept genuine missing question marks, dialogue punctuation, true run-on repairs,
necessary attachment commas, and breath points that make the passage unambiguously
clearer. When uncertain, reject. Return exactly one decision for every editId and do not
rewrite the prose.

PROPOSALS

""" + "\n\n---\n\n".join(rendered)


def run_codex(items: list[dict[str, Any]], model: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="monroe-punctuation-critic-") as temp_dir:
        schema = Path(temp_dir) / "schema.json"
        result = Path(temp_dir) / "result.json"
        schema.write_text(json.dumps(CRITIC_SCHEMA), encoding="utf-8")
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
            str(schema),
            "--output-last-message",
            str(result),
            "-c",
            'model_reasoning_effort="high"',
            "-",
        ]
        completed = subprocess.run(
            command,
            input=critic_prompt(items),
            text=True,
            capture_output=True,
            timeout=1200,
        )
        if completed.returncode:
            raise RuntimeError(f"Codex critic failed: {completed.stderr.strip()}")
        return json.loads(result.read_text(encoding="utf-8"))


def write_approved_artifacts(
    items: list[dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
    output_root: Path,
    model: str,
) -> dict[str, Any]:
    by_report: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        by_report.setdefault(item["report"], []).append(item)
    summary: dict[str, Any] = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "criticModel": model,
        "chapters": 0,
        "proposedEdits": len(items),
        "approvedEdits": 0,
        "rejectedEdits": 0,
        "reports": [],
    }
    for report_name, report_items in by_report.items():
        report = json.loads(Path(report_name).read_text(encoding="utf-8"))
        source_raw = Path(report["source"]).read_text(encoding="utf-8")
        paragraphs, separators = REVIEW.split_document(source_raw)
        approved = []
        rejected = []
        for item in report_items:
            decision = decisions[item["editId"]]
            record = {
                "editId": item["editId"],
                "paragraphIndex": item["paragraphIndex"],
                "reason": decision["reason"],
            }
            if decision["accept"]:
                paragraphs[item["paragraphIndex"] - 1] = (
                    REVIEW.preserve_existing_em_dash_spacing(
                        item["originalParagraph"],
                        item["editedParagraph"],
                    )
                )
                approved.append(record)
            else:
                rejected.append(record)
        approved_raw = REVIEW.join_document(paragraphs, separators)
        valid, validation = REVIEW.punctuation_only(source_raw, approved_raw)
        if not valid:
            raise RuntimeError(f"approved word lock failed for {report['source']}: {validation}")
        relative = Path(report["repoId"]) / Path(report["relativeSource"])
        base = output_root / relative
        approved_path = base.with_suffix(".punctuation-approved.md")
        diff_path = base.with_suffix(".punctuation-approved.diff")
        approval_path = base.with_suffix(".punctuation-approval.json")
        approved_path.parent.mkdir(parents=True, exist_ok=True)
        approved_path.write_text(approved_raw, encoding="utf-8")
        diff_path.write_text(
            "".join(
                difflib.unified_diff(
                    source_raw.splitlines(keepends=True),
                    approved_raw.splitlines(keepends=True),
                    fromfile=report["source"],
                    tofile=str(approved_path),
                )
            ),
            encoding="utf-8",
        )
        approval = {
            "schemaVersion": 1,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "criticModel": model,
            "source": report["source"],
            "repoRoot": report["repoRoot"],
            "repoId": report["repoId"],
            "relativeSource": report["relativeSource"],
            "sourceSha256": report["sourceSha256"],
            "approvedSha256": sha256_text(approved_raw),
            "approved": approved,
            "rejected": rejected,
            "wordLockValidation": validation,
            "approvedCandidate": str(approved_path),
            "diff": str(diff_path),
            "status": "changed" if approved else "clean-after-critic",
        }
        approval_path.write_text(
            json.dumps(approval, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        summary["chapters"] += 1
        summary["approvedEdits"] += len(approved)
        summary["rejectedEdits"] += len(rejected)
        summary["reports"].append(str(approval_path))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_root", nargs="+", type=Path)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--model", default="gpt-5.6-terra")
    parser.add_argument("--batch-size", type=int, default=40)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    reports = collect_reports(args.result_root)
    allowed_sources = None
    if args.inventory:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
        allowed_sources = {str(item["source"]) for item in inventory["chapters"]}
    items = make_items(reports, allowed_sources)
    if args.limit is not None:
        items = items[: args.limit]
    args.output_root.mkdir(parents=True, exist_ok=True)
    all_decisions: dict[str, dict[str, Any]] = {}
    raw_batches = args.output_root / "critic-batches"
    raw_batches.mkdir(parents=True, exist_ok=True)
    for offset in range(0, len(items), args.batch_size):
        batch = items[offset : offset + args.batch_size]
        batch_number = offset // args.batch_size + 1
        print(f"critic batch {batch_number}: {len(batch)} edits", flush=True)
        result = run_codex(batch, args.model)
        returned = {decision["editId"]: decision for decision in result["decisions"]}
        expected = {item["editId"] for item in batch}
        if set(returned) != expected:
            missing = sorted(expected - set(returned))
            extra = sorted(set(returned) - expected)
            raise RuntimeError(f"critic decision mismatch missing={missing} extra={extra}")
        all_decisions.update(returned)
        (raw_batches / f"batch-{batch_number:04}.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    summary = write_approved_artifacts(items, all_decisions, args.output_root, args.model)
    (args.output_root / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"chapters={summary['chapters']} proposed={summary['proposedEdits']} "
        f"approved={summary['approvedEdits']} rejected={summary['rejectedEdits']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Ingest owner edits and compile safe Monroe style memory.

The archive is immutable evidence. Derived example views are rebuilt from the
event lifecycle and may be deleted/recreated. This script never promotes a voice
candidate over the approved OWNER_VOICE.md.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

from validate import load_json, validate_instance


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = PACKAGE_ROOT / "owner-style"
SCHEMA_PATH = PACKAGE_ROOT / "contracts" / "owner-edit-event.schema.json"
LIBRARIAN_PATH = PACKAGE_ROOT / "agents" / "owner-voice-librarian.md"

POSITIVE_EVENT_TYPES = {"direct_edit", "revision_accepted", "voice_example"}
VOICE_REASONS = {
    "sentence_load",
    "word_choice",
    "cadence",
    "clarity",
    "repetition",
    "dialogue_voice",
    "character_voice",
    "pacing",
    "emotional_precision",
    "action_clarity",
    "other",
}
NON_VOICE_REASONS = {"continuity", "canon_or_fact", "typo_or_punctuation"}
SCOPE_FILES = {
    "monroe_shared": "shared.jsonl",
    "fantasy": "fantasy.jsonl",
    "science_fiction": "science-fiction.jsonl",
}

PWA_EVENT_TYPES = {
    "direct_edit",
    "voice_example",
    "revision_request",
    "revision_proposed",
    "revision_accepted",
    "revision_rejected",
    "protect",
    "unprotect",
    "revert",
}


class OwnerStyleError(Exception):
    """A safe, user-facing owner-style pipeline error."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def safe_component(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-.")
    if not cleaned:
        raise OwnerStyleError(f"cannot make a safe path component from {value!r}")
    return cleaned[:160]


def read_input(path: str) -> list[dict[str, Any]]:
    if path == "-":
        raw = sys.stdin.read()
        label = "stdin"
    else:
        label = path
        raw = Path(path).read_text(encoding="utf-8")
    raw = raw.strip()
    if not raw:
        return []

    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        rows: list[dict[str, Any]] = []
        for number, line in enumerate(raw.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise OwnerStyleError(f"{label}:{number}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise OwnerStyleError(f"{label}:{number}: each JSONL row must be an object")
            rows.append(row)
        return rows

    if isinstance(value, list):
        rows = value
    elif isinstance(value, dict) and isinstance(value.get("events"), list):
        rows = value["events"]
    elif isinstance(value, dict):
        rows = [value]
    else:
        raise OwnerStyleError(f"{label}: expected an event, event array, or export object")
    if not all(isinstance(row, dict) for row in rows):
        raise OwnerStyleError(f"{label}: every event must be a JSON object")
    return rows


def normalize_pwa_event(event: dict[str, Any]) -> dict[str, Any]:
    """Translate Boundary Universe's deployed flat v1 event to our archive shape.

    The source event remains immutable in GitHub. The normalized copy is the
    stable, provider-independent representation used by Monroe's selectors.
    Already-normalized v1.0 events pass through unchanged.
    """
    if event.get("schemaVersion") != "1":
        return event
    if "manuscript" in event or event.get("eventType") not in PWA_EVENT_TYPES:
        return event

    event_type = event.get("eventType")
    event_status = event.get("eventStatus")
    if event_type == "revision_request":
        status_value = "pending"
    elif event_type == "revision_rejected" or event_status == "rejected":
        status_value = "rejected"
    elif event_status == "conflicted":
        status_value = "conflict"
    elif event_status in {"recorded", "superseded"}:
        status_value = "pending" if event_status == "recorded" else "reverted"
    elif event_type == "revert":
        # A revert is itself an applied lifecycle event. Marking it applied lets
        # active_examples invalidate the superseded edit without erasing it.
        status_value = "applied"
    else:
        status_value = "applied"

    raw_reasons = event.get("reasonCodes") or []
    reasons: list[str] = []
    for reason in raw_reasons:
        normalized = reason if reason in VOICE_REASONS | NON_VOICE_REASONS else "other"
        if normalized not in reasons:
            reasons.append(normalized)

    result: dict[str, str] = {}
    revised = event.get("revisedText")
    instruction = event.get("revisionInstruction")
    if isinstance(revised, str):
        result["revisedText"] = revised
    if isinstance(instruction, str):
        result["instruction"] = instruction

    protection = "locked" if event.get("protectionStatus") == "protected" else "none"
    if (
        protection == "none"
        and event_type in POSITIVE_EVENT_TYPES
        and event.get("actorRole") == "owner"
    ):
        protection = "owner_authored"

    normalized_event: dict[str, Any] = {
        "schemaVersion": "1.0",
        "eventId": event.get("eventId"),
        "eventType": event_type,
        "createdAt": event.get("createdAt"),
        "actorRole": "owner" if event.get("actorRole") == "owner" else "assistant",
        "repository": event.get("repository"),
        "manuscript": {
            "bookId": event.get("bookId"),
            "bookTitle": event.get("bookTitle"),
            "chapterId": event.get("chapterId"),
            "chapterNumber": event.get("chapterNumber"),
            "chapterTitle": event.get("chapterTitle"),
            "sourcePath": event.get("sourcePath"),
            "resolvedSourcePath": event.get("resolvedSourcePath"),
            "baseCommit": event.get("baseCommit"),
            "baseDocumentHash": event.get("baseDocumentHash"),
        },
        "selection": {
            "blockId": event.get("blockId"),
            "originalText": event.get("originalText"),
            "contextBefore": event.get("contextBefore") or "",
            "contextAfter": event.get("contextAfter") or "",
            "pageHint": event.get("pageHint") or 0,
        },
        "result": result,
        "preference": {
            "reasonCodes": reasons,
            "ownerComment": event.get("ownerComment") or "",
            # PWA scopeHint describes selection size, not transferability of a
            # prose preference. Keep new evidence book-scoped until distilled.
            "scopeHint": "unclassified",
        },
        "protection": protection,
        "status": status_value,
    }
    series_id = event.get("seriesId")
    if isinstance(series_id, str) and series_id:
        normalized_event["manuscript"]["seriesId"] = series_id
    for source_key, target in (
        ("startOffset", normalized_event["selection"]),
        ("endOffset", normalized_event["selection"]),
    ):
        value = event.get(source_key)
        if isinstance(value, int):
            target[source_key] = value
    for key in ("supersedesEventId", "requestEventId"):
        value = event.get(key)
        if isinstance(value, str) and value:
            normalized_event[key] = value
    return normalized_event


def normalize_events(events: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [normalize_pwa_event(event) for event in events]


def validate_events(events: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    schema = load_json(SCHEMA_PATH)
    validated = list(events)
    seen: set[str] = set()
    for index, event in enumerate(validated):
        errors = validate_instance(event, schema)
        if errors:
            details = "\n".join(f"  - {error}" for error in errors)
            raise OwnerStyleError(f"event {index + 1} failed schema validation:\n{details}")
        event_id = event["eventId"]
        if event_id in seen:
            raise OwnerStyleError(f"input repeats eventId {event_id!r}")
        seen.add(event_id)
        selection = event["selection"]
        start = selection.get("startOffset")
        end = selection.get("endOffset")
        if start is not None and end is not None and end < start:
            raise OwnerStyleError(f"event {event_id!r}: endOffset precedes startOffset")
        if event["eventType"] in POSITIVE_EVENT_TYPES:
            revised = event["result"].get("revisedText", "")
            if not revised.strip():
                raise OwnerStyleError(
                    f"event {event_id!r}: {event['eventType']} requires result.revisedText"
                )
        if event["eventType"] == "revision_request":
            instruction = event["result"].get("instruction", "")
            if not instruction.strip():
                raise OwnerStyleError(
                    f"event {event_id!r}: revision_request requires result.instruction"
                )
        if event["eventType"] == "revision_proposed":
            if not event["result"].get("revisedText", "").strip():
                raise OwnerStyleError(
                    f"event {event_id!r}: revision_proposed requires result.revisedText"
                )
        if event["eventType"] in {
            "revision_proposed",
            "revision_accepted",
            "revision_rejected",
        } and not event.get("requestEventId"):
            raise OwnerStyleError(
                f"event {event_id!r}: {event['eventType']} requires requestEventId"
            )
        if event["eventType"] in {"unprotect", "revert"} and not event.get(
            "supersedesEventId"
        ):
            raise OwnerStyleError(
                f"event {event_id!r}: {event['eventType']} requires supersedesEventId"
            )
    return validated


def archive_path(root: Path) -> Path:
    return root / "edits.jsonl"


def load_archive(root: Path) -> list[dict[str, Any]]:
    path = archive_path(root)
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise OwnerStyleError(f"{path}:{number}: corrupt archive JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise OwnerStyleError(f"{path}:{number}: archive row is not an object")
        event_id = value.get("eventId")
        if isinstance(event_id, str):
            serialized = canonical_json(value)
            if event_id in seen:
                state = "different content" if seen[event_id] != serialized else "duplicate row"
                raise OwnerStyleError(f"{path}:{number}: eventId {event_id!r} has {state}")
            seen[event_id] = serialized
        rows.append(value)
    return rows


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def ingest(root: Path, incoming: list[dict[str, Any]]) -> tuple[int, int]:
    incoming = validate_events(normalize_events(incoming))
    existing = load_archive(root)
    by_id = {event["eventId"]: event for event in existing}
    additions: list[dict[str, Any]] = []
    skipped = 0
    for event in incoming:
        event_id = event["eventId"]
        previous = by_id.get(event_id)
        if previous is not None:
            if canonical_json(previous) != canonical_json(event):
                raise OwnerStyleError(
                    f"eventId {event_id!r} already exists with different content"
                )
            skipped += 1
            continue
        additions.append(event)
        by_id[event_id] = event

    additions.sort(key=lambda event: (event["createdAt"], event["eventId"]))
    full = existing + additions
    if additions:
        root.mkdir(parents=True, exist_ok=True)
        atomic_write(
            archive_path(root),
            "".join(f"{canonical_json(event)}\n" for event in full),
        )
    for event in full:
        manuscript = event["manuscript"]
        event_file = (
            root
            / "events"
            / safe_component(manuscript["bookId"])
            / safe_component(manuscript["chapterId"])
            / f"{safe_component(event['eventId'])}.json"
        )
        expected = json.dumps(event, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if event_file.exists():
            if event_file.read_text(encoding="utf-8") != expected:
                raise OwnerStyleError(f"event file disagrees with archive: {event_file}")
        else:
            atomic_write(event_file, expected)
    rebuild(root)
    return len(additions), skipped


def run_git(repo: Path, *args: str, check: bool = True) -> str:
    process = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if check and process.returncode != 0:
        detail = process.stderr.strip() or process.stdout.strip() or "git command failed"
        raise OwnerStyleError(detail)
    return process.stdout.strip()


def sync_state_path(root: Path) -> Path:
    return root / "sync" / "github.json"


def load_sync_state(root: Path) -> dict[str, Any]:
    path = sync_state_path(root)
    if not path.exists():
        return {}
    value = load_json(path)
    if not isinstance(value, dict):
        raise OwnerStyleError(f"{path}: sync state must be an object")
    return value


def github_event_paths(repo: Path, ref: str, previous: str | None) -> list[str]:
    if previous:
        ancestor = subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", previous, ref],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if ancestor.returncode == 0:
            output = run_git(
                repo,
                "diff",
                "--name-only",
                "--diff-filter=AM",
                previous,
                ref,
                "--",
                "edits/events",
            )
            return sorted(path for path in output.splitlines() if path.endswith(".json"))
    output = run_git(repo, "ls-tree", "-r", "--name-only", ref, "--", "edits/events")
    return sorted(path for path in output.splitlines() if path.endswith(".json"))


def sync_github(
    root: Path,
    repo: Path,
    ref: str = "origin/main",
    *,
    fetch: bool = True,
) -> dict[str, Any]:
    """Ingest immutable PWA event files from a Git ref and advance safely."""
    repo = repo.resolve()
    if not (repo / ".git").exists():
        raise OwnerStyleError(f"not a Git repository: {repo}")
    if fetch:
        remote = ref.split("/", 1)[0] if "/" in ref else "origin"
        run_git(repo, "fetch", "--quiet", remote)
    current = run_git(repo, "rev-parse", "--verify", ref)
    state = load_sync_state(root)
    same_feed = state.get("repository") == str(repo) and state.get("ref") == ref
    previous = state.get("commit") if same_feed and isinstance(state.get("commit"), str) else None
    paths = github_event_paths(repo, ref, previous)
    incoming: list[dict[str, Any]] = []
    for path in paths:
        raw = run_git(repo, "show", f"{ref}:{path}")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OwnerStyleError(f"{ref}:{path}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise OwnerStyleError(f"{ref}:{path}: event file must contain one object")
        incoming.append(value)

    added, skipped = ingest(root, incoming)
    next_state = {
        "repository": str(repo),
        "ref": ref,
        "commit": current,
        "syncedAt": datetime.now().astimezone().isoformat(),
    }
    atomic_write(sync_state_path(root), json.dumps(next_state, indent=2, sort_keys=True) + "\n")
    if added:
        atomic_write(
            root / "candidates" / "distill.prompt.md",
            build_distillation_prompt(root),
        )
    return {
        "sourceCommit": current,
        "filesExamined": len(paths),
        "added": added,
        "skipped": skipped,
        **status(root),
    }


def active_examples(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    invalidated: set[str] = set()
    for event in events:
        target = event.get("supersedesEventId")
        if not target or event.get("status") != "applied":
            continue
        if event.get("eventType") in {"direct_edit", "revision_accepted", "revert"}:
            invalidated.add(target)

    explicitly_selected = {
        event.get("requestEventId")
        for event in events
        if event.get("eventType") == "voice_example"
        and event.get("actorRole") == "owner"
        and event.get("status") == "applied"
        and event.get("requestEventId")
    }
    examples: list[dict[str, Any]] = []
    for event in events:
        if event.get("eventId") in invalidated:
            continue
        if event.get("eventId") in explicitly_selected:
            # The explicit selection supersedes the automatically inferred copy
            # as training evidence, while both immutable events remain archived.
            continue
        if event.get("eventType") not in POSITIVE_EVENT_TYPES:
            continue
        if event.get("actorRole") != "owner" or event.get("status") != "applied":
            continue
        original = event["selection"]["originalText"].strip()
        revised = event["result"].get("revisedText", "").strip()
        if not original or not revised:
            continue
        if original == revised and event.get("eventType") != "voice_example":
            continue

        preference = event.get("preference", {})
        reasons = set(preference.get("reasonCodes", []))
        scope = preference.get("scopeHint", "unclassified")
        if scope == "local_only":
            continue
        if reasons and reasons <= NON_VOICE_REASONS:
            continue
        if reasons and not (reasons & VOICE_REASONS):
            continue

        manuscript = event["manuscript"]
        examples.append(
            {
                "eventId": event["eventId"],
                "signal": "explicit" if event.get("eventType") == "voice_example" else "inferred",
                "createdAt": event["createdAt"],
                "scope": scope,
                "reasons": sorted(reasons),
                "ownerComment": preference.get("ownerComment", "").strip(),
                "bookId": manuscript["bookId"],
                "seriesId": manuscript.get("seriesId", ""),
                "chapterId": manuscript["chapterId"],
                "original": original,
                "revised": revised,
                "contextBefore": event["selection"].get("contextBefore", "").strip(),
                "contextAfter": event["selection"].get("contextAfter", "").strip(),
                "protection": event.get("protection", "none"),
            }
        )
    examples.sort(key=lambda item: (item["createdAt"], item["eventId"]))
    return examples


def active_protections(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    released = {
        event.get("supersedesEventId")
        for event in events
        if event.get("status") == "applied"
        and event.get("eventType")
        in {"direct_edit", "revision_accepted", "unprotect", "revert"}
        and event.get("supersedesEventId")
    }
    protections: list[dict[str, Any]] = []
    for event in events:
        is_explicit = event.get("eventType") == "protect"
        is_locked_edit = (
            event.get("eventType") in POSITIVE_EVENT_TYPES
            and event.get("protection") == "locked"
        )
        if not (is_explicit or is_locked_edit):
            continue
        if event.get("status") != "applied" or event.get("eventId") in released:
            continue
        manuscript = event["manuscript"]
        selection = event["selection"]
        protections.append(
            {
                "eventId": event["eventId"],
                "createdAt": event["createdAt"],
                "bookId": manuscript["bookId"],
                "chapterId": manuscript["chapterId"],
                "resolvedSourcePath": manuscript["resolvedSourcePath"],
                "blockId": selection["blockId"],
                "protectedText": event.get("result", {}).get("revisedText")
                or selection["originalText"],
            }
        )
    protections.sort(key=lambda item: (item["createdAt"], item["eventId"]))
    return protections


def event_queue(event: dict[str, Any]) -> str | None:
    if event.get("status") == "conflict":
        return "conflicts"
    if event.get("eventType") == "revision_request" and event.get("status") == "pending":
        return "revision-requests"
    if event.get("eventType") not in POSITIVE_EVENT_TYPES:
        return None
    preference = event.get("preference", {})
    reasons = set(preference.get("reasonCodes", []))
    if preference.get("scopeHint") == "local_only":
        return "local"
    if reasons and reasons <= {"typo_or_punctuation"}:
        return "mechanical"
    if reasons and reasons <= NON_VOICE_REASONS and reasons & {"continuity", "canon_or_fact"}:
        return "canon"
    return None


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    text = "".join(f"{canonical_json(row)}\n" for row in rows)
    atomic_write(path, text)


def rebuild(root: Path) -> list[dict[str, Any]]:
    events = load_archive(root)
    if events:
        validate_events(events)
    examples = active_examples(events)
    examples_root = root / "examples"
    write_jsonl(examples_root / "all.jsonl", examples)
    for scope, filename in SCOPE_FILES.items():
        write_jsonl(
            examples_root / filename,
            (example for example in examples if example["scope"] == scope),
        )
    write_jsonl(root / "protections.jsonl", active_protections(events))
    for queue in ("canon", "mechanical", "local", "revision-requests", "conflicts"):
        write_jsonl(
            root / "queues" / f"{queue}.jsonl",
            (event for event in events if event_queue(event) == queue),
        )
    return examples


def _scope_eligible(
    example: dict[str, Any], genre: str, book_id: str | None, series_id: str | None
) -> bool:
    scope = example["scope"]
    if scope == "monroe_shared":
        return True
    if scope == "fantasy":
        return genre == "fantasy"
    if scope == "science_fiction":
        return genre == "scifi"
    if scope == "series":
        return bool(series_id and example.get("seriesId") == series_id)
    if scope in {"book", "character", "unclassified"}:
        return bool(book_id and example.get("bookId") == book_id)
    return False


def select_examples(
    root: Path,
    genre: str,
    *,
    book_id: str | None = None,
    series_id: str | None = None,
    packet_text: str = "",
    limit: int = 8,
) -> list[dict[str, Any]]:
    if genre not in {"fantasy", "scifi"}:
        raise OwnerStyleError("genre must be fantasy or scifi")
    if limit < 0 or limit > 24:
        raise OwnerStyleError("example limit must be between 0 and 24")
    if limit == 0:
        return []
    examples = active_examples(load_archive(root))
    lowered = packet_text.lower()
    relevant: set[str] = {"sentence_load", "word_choice", "cadence", "clarity", "repetition"}
    if any(word in lowered for word in ("fight", "combat", "attack", "battle", "skirmish")):
        relevant.add("action_clarity")
    if any(word in lowered for word in ("dialogue", "conversation", "argument", "interview")):
        relevant.update({"dialogue_voice", "character_voice"})
    if any(word in lowered for word in ("grief", "loss", "choice", "relationship", "emotion")):
        relevant.add("emotional_precision")
    if any(word in lowered for word in ("pace", "pacing", "chase", "suspense")):
        relevant.add("pacing")

    scored: list[tuple[int, float, str, dict[str, Any]]] = []
    for example in examples:
        if not _scope_eligible(example, genre, book_id, series_id):
            continue
        score = 0
        scope = example["scope"]
        if scope == "monroe_shared":
            score += 30
        elif scope in {"fantasy", "science_fiction"}:
            score += 35
        elif scope == "series":
            score += 45
        elif scope in {"book", "character", "unclassified"}:
            score += 50
        score += 5 * len(set(example["reasons"]) & relevant)
        if example.get("protection") in {"owner_authored", "locked"}:
            score += 3
        if example.get("signal") == "explicit":
            score += 20
        # Prefer concise examples when relevance is otherwise equal.
        length_key = f"{len(example['original']) + len(example['revised']):08d}"
        try:
            recency = datetime.fromisoformat(example["createdAt"].replace("Z", "+00:00")).timestamp()
        except ValueError:
            recency = 0.0
        scored.append((score, recency, length_key, example))
    scored.sort(key=lambda row: (-row[0], row[2], -row[1], row[3]["eventId"]))
    return [row[3] for row in scored[:limit]]


def clip(text: str, limit: int = 1200) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    head = max(1, (limit - 24) // 2)
    tail = max(1, limit - 24 - head)
    return f"{text[:head].rstrip()}\n[…excerpt clipped…]\n{text[-tail:].lstrip()}"


def format_examples(examples: list[dict[str, Any]], max_chars: int = 7000) -> str:
    if not examples:
        return ""
    lines = [
        "These comparison pairs demonstrate owner taste. Learn the difference in kind.",
        "Do not copy their names, facts, settings, or distinctive phrases into this movement.",
        "A pair is contextual evidence, not automatically a universal rule.",
        "",
    ]
    used = len("\n".join(lines))
    for index, example in enumerate(examples, start=1):
        part = [
            f"## Example {index} — {example['eventId']}",
            f"Signals: {', '.join(example['reasons']) or 'owner choice'}"
            + ("; explicitly sent to Monroe" if example.get("signal") == "explicit" else ""),
        ]
        if example.get("signal") == "explicit" and example["original"] == example["revised"]:
            part.append(f"OWNER-APPROVED PASSAGE:\n{clip(example['revised'])}")
        else:
            part.extend(
                [
                    f"MODEL ORIGINAL:\n{clip(example['original'])}",
                    f"OWNER REVISION:\n{clip(example['revised'])}",
                ]
            )
        if example.get("ownerComment"):
            part.append(f"OWNER NOTE: {clip(example['ownerComment'], 500)}")
        block = "\n\n".join(part) + "\n\n"
        if used + len(block) > max_chars:
            break
        lines.append(block.rstrip())
        lines.append("")
        used += len(block)
    return "\n".join(lines).strip()


def build_distillation_prompt(root: Path, max_examples: int = 80) -> str:
    profile_path = root / "OWNER_VOICE.md"
    current = profile_path.read_text(encoding="utf-8").strip() if profile_path.exists() else ""
    examples = active_examples(load_archive(root))[-max_examples:]
    evidence = format_examples(examples, max_chars=50000) or "No eligible owner voice examples yet."
    return (
        "# Monroe Jackson — Owner voice distillation\n\n"
        "Produce a reviewable candidate. Do not modify the approved profile directly.\n\n"
        "---\n\n# ROLE\n\n"
        f"{LIBRARIAN_PATH.read_text(encoding='utf-8').strip()}\n\n"
        "---\n\n# CURRENT APPROVED OWNER VOICE\n\n"
        f"{current or 'No approved profile exists yet.'}\n\n"
        "---\n\n# ACTIVE OWNER EDIT EVIDENCE\n\n"
        f"{evidence}\n"
    )


def status(root: Path) -> dict[str, Any]:
    events = load_archive(root)
    examples = active_examples(events)
    counts: dict[str, int] = {}
    for example in examples:
        counts[example["scope"]] = counts.get(example["scope"], 0) + 1
    return {
        "root": str(root),
        "events": len(events),
        "activeVoiceExamples": len(examples),
        "activeProtections": len(active_protections(events)),
        "examplesByScope": dict(sorted(counts.items())),
        "approvedVoiceProfile": (root / "OWNER_VOICE.md").is_file(),
        "archiveSha256": hashlib.sha256(
            archive_path(root).read_bytes() if archive_path(root).exists() else b""
        ).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="validate and append JSON/JSONL exports")
    ingest_parser.add_argument("inputs", nargs="+", help="files or - for stdin")

    subparsers.add_parser("rebuild", help="rebuild active example views from the archive")
    subparsers.add_parser("status", help="report archive and active-example counts")

    sync_parser = subparsers.add_parser(
        "sync-github", help="fetch and ingest PWA events committed under edits/events"
    )
    sync_parser.add_argument("repository", type=Path)
    sync_parser.add_argument("--ref", default="origin/main")
    sync_parser.add_argument("--no-fetch", action="store_true")

    select_parser = subparsers.add_parser("select", help="print examples for a movement")
    select_parser.add_argument("--genre", choices=("fantasy", "scifi"), required=True)
    select_parser.add_argument("--book-id")
    select_parser.add_argument("--series-id")
    select_parser.add_argument("--packet", type=Path)
    select_parser.add_argument("--limit", type=int, default=8)

    distill_parser = subparsers.add_parser(
        "distill-prompt", help="compile a reviewable owner-voice librarian prompt"
    )
    distill_parser.add_argument("--output", type=Path)
    distill_parser.add_argument("--max-examples", type=int, default=80)

    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == "ingest":
            incoming: list[dict[str, Any]] = []
            for source in args.inputs:
                incoming.extend(read_input(source))
            added, skipped = ingest(root, incoming)
            print(json.dumps({"added": added, "skipped": skipped, **status(root)}, indent=2))
        elif args.command == "rebuild":
            examples = rebuild(root)
            print(json.dumps({"activeVoiceExamples": len(examples)}, indent=2))
        elif args.command == "status":
            print(json.dumps(status(root), indent=2))
        elif args.command == "sync-github":
            print(
                json.dumps(
                    sync_github(
                        root,
                        args.repository,
                        args.ref,
                        fetch=not args.no_fetch,
                    ),
                    indent=2,
                )
            )
        elif args.command == "select":
            packet_text = args.packet.read_text(encoding="utf-8") if args.packet else ""
            examples = select_examples(
                root,
                args.genre,
                book_id=args.book_id,
                series_id=args.series_id,
                packet_text=packet_text,
                limit=args.limit,
            )
            print(format_examples(examples))
        elif args.command == "distill-prompt":
            prompt = build_distillation_prompt(root, args.max_examples)
            if args.output:
                atomic_write(args.output, prompt)
                print(args.output)
            else:
                print(prompt)
    except (OSError, OwnerStyleError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

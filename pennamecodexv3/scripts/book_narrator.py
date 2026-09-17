#!/usr/bin/env python3
"""Create and inspect resumable Monroe Book Narrator 1.2.5 runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SYSTEM_ROOT = Path("/Users/drive/penname/pennamecodexv3")
VOICE_REGISTRY = SYSTEM_ROOT / "voices/book-narrator-voices.v1.json"
WORKFLOW = SYSTEM_ROOT / "workflows/book-narrator-1.2.5.md"
SCHEMA = SYSTEM_ROOT / "schemas/narration-clarity-item.v1.schema.json"
WORD_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", re.UNICODE)
CHAPTER_RE = re.compile(r"chapter-(\d+)(?:-|\.md$)", re.IGNORECASE)


def words(value: str) -> list[str]:
    return [m.group(0).casefold().replace("’", "'") for m in WORD_RE.finditer(value)]


def prose_paragraphs(value: str) -> list[str]:
    if value.startswith("---\n"):
        end = value.find("\n---\n", 4)
        if end >= 0:
            value = value[end + 5 :]
    paragraphs = []
    for part in re.split(r"\n\s*\n", value):
        stripped = part.strip()
        if not stripped:
            continue
        if stripped == "---" or all(line.lstrip().startswith("#") for line in stripped.splitlines()):
            continue
        if words(stripped):
            paragraphs.append(part)
    return paragraphs


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_chapters(value: str) -> list[int]:
    result: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = (int(piece) for piece in part.split("-", 1))
            if start < 1 or end < start:
                raise ValueError(f"Invalid chapter range: {part}")
            result.update(range(start, end + 1))
        else:
            number = int(part)
            if number < 1:
                raise ValueError("Chapter numbers begin at 1")
            result.add(number)
    if not result:
        raise ValueError("No chapters selected")
    return sorted(result)


def load_voices() -> tuple[dict[str, Any], dict[str, str]]:
    registry = json.loads(VOICE_REGISTRY.read_text(encoding="utf-8"))
    aliases: dict[str, str] = {}
    for key, voice in registry["voices"].items():
        aliases[key.casefold()] = key
        aliases[voice["displayName"].casefold()] = key
        for alias in voice.get("aliases", []):
            aliases[alias.casefold()] = key
    return registry, aliases


def resolve_voice(name: str) -> tuple[str, dict[str, Any]]:
    registry, aliases = load_voices()
    key = aliases.get(name.casefold())
    if not key:
        choices = ", ".join(voice["displayName"] for voice in registry["voices"].values())
        raise ValueError(f"Unknown voice {name!r}; choose {choices}")
    return key, registry["voices"][key]


def chapter_number(path: Path) -> int | None:
    match = CHAPTER_RE.search(path.name)
    return int(match.group(1)) if match else None


def find_chapters(book_root: Path, manuscript_dir: Path | None) -> dict[int, Path]:
    candidates: list[Path] = []
    if manuscript_dir:
        candidates = list(manuscript_dir.glob("chapter-*.md"))
    else:
        for directory in (
            book_root / "chapters",
            book_root / "manuscript",
            book_root,
        ):
            if directory.is_dir():
                matches = list(directory.glob("chapter-*.md"))
                if matches:
                    candidates = matches
                    break
    result: dict[int, Path] = {}
    for path in candidates:
        number = chapter_number(path)
        if number is None:
            continue
        if number in result:
            raise RuntimeError(f"More than one source found for chapter {number:02d}")
        result[number] = path.resolve()
    if not result:
        raise RuntimeError(f"No chapter-*.md manuscripts found under {book_root}")
    return result


def run_name(chapters: list[int]) -> str:
    return f"chapters-{chapters[0]:02d}-{chapters[-1]:02d}"


def discover_performance_dir(book_root: Path) -> Path | None:
    direct = book_root / "performance"
    if direct.is_dir():
        return direct.resolve()
    staged = (
        Path("/Users/drive/kindling-narrator-stage/public/manuscripts/books")
        / book_root.name
        / "performance"
    )
    return staged.resolve() if staged.is_dir() else None


def write_if_missing(path: Path, text: str, force: bool) -> None:
    if force or not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def start(args: argparse.Namespace) -> int:
    book_root = args.book_root.resolve()
    voice_key, voice = resolve_voice(args.voice)
    selected = parse_chapters(args.chapters)
    sources = find_chapters(book_root, args.manuscript_dir)
    missing = [number for number in selected if number not in sources]
    if missing:
        raise RuntimeError(f"Missing selected chapters: {', '.join(map(str, missing))}")
    if len(selected) > 3 and not args.allow_large_window:
        raise RuntimeError("A narrator run is three chapters. Use --allow-large-window deliberately.")

    output_root = (
        args.output_root.resolve()
        if args.output_root
        else book_root / "narration" / "monroe-1.2.5" / voice_key / run_name(selected)
    )
    output_root.mkdir(parents=True, exist_ok=True)
    performance_dir = discover_performance_dir(book_root)
    title = args.title or book_root.name.replace("-", " ").title()
    manifest_chapters: list[dict[str, Any]] = []
    for number in selected:
        source = sources[number]
        chapter_dir = output_root / f"chapter-{number:02d}"
        prepared = chapter_dir / f"chapter-{number:02d}.narration.md"
        write_if_missing(prepared, source.read_text(encoding="utf-8"), args.force)
        context = performance_dir / f"chapter-{number:02d}.context.md" if performance_dir else None
        manifest_chapters.append(
            {
                "number": number,
                "source": str(source),
                "sourceSha256": sha256(source),
                "prepared": str(prepared),
                "clarityReview": str(chapter_dir / "clarity-review.jsonl"),
                "performanceChoices": str(chapter_dir / "performance-choices.md"),
                "writingFeedback": str(chapter_dir / "writing-monroe-feedback.md"),
                "performanceTrack": str(chapter_dir / f"chapter-{number:02d}.performance.json"),
                "audio": str(chapter_dir / f"chapter-{number:02d}.{voice_key}.mp3"),
                "listeningReview": str(chapter_dir / "listening-review.md"),
                "bookContext": str(context) if context and context.exists() else None,
            }
        )
    run = {
        "schemaVersion": 1,
        "pipeline": "Monroe Book Narrator",
        "pipelineVersion": "1.2.5",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "title": title,
        "audience": args.audience,
        "bookRoot": str(book_root),
        "runRoot": str(output_root.resolve()),
        "voiceKey": voice_key,
        "voice": voice,
        "workflow": str(WORKFLOW),
        "claritySchema": str(SCHEMA),
        "performanceDirectory": str(performance_dir) if performance_dir else None,
        "chapters": manifest_chapters,
    }
    run_path = output_root / "run.json"
    run_path.write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    source_list = "\n".join(
        f"- Chapter {item['number']:02d}: `{item['source']}`" for item in manifest_chapters
    )
    run_doc = f"""# {title} — Monroe Book Narrator 1.2.5

- Voice: {voice['displayName']}
- Audience: {args.audience}
- Rolling window: {selected[0]:02d}–{selected[-1]:02d}
- Approved master: `{voice['approvedMaster']}`
- Delivery coach: `{voice['coach']}`
- Native provider speed instruction: {voice['nativeSpeed']}
- Final pace authority: measured approved-master range, not requested speed

## Sources

{source_list}

## Order

1. Read the complete book or existing performance bible.
2. Read all chapters in this window before changing punctuation or directing delivery.
3. Complete each `clarity-review.jsonl` and its word-locked narration copy.
4. A/B any punctuation that materially changes the performance; wait for owner choice.
5. Send wording problems to `writing-monroe-feedback.md`; rerun after canon changes.
6. Direct each clean narration copy with book context and the selected voice coach.
7. Render, measure, listen, make exact pickups, and preserve accepted takes.

The detailed loop is in `{WORKFLOW}`. Run state is in `{run_path}`.
"""
    write_if_missing(output_root / "RUN.md", run_doc, args.force)
    write_if_missing(output_root / "book-narrator.prompt.md", build_prompt(run), args.force)
    print(run_path)
    print(output_root / "book-narrator.prompt.md")
    return 0


def build_prompt(run: dict[str, Any]) -> str:
    chapters = ", ".join(f"{item['number']:02d}" for item in run["chapters"])
    return f"""Activate Monroe Book Narrator 1.2.5 for **{run['title']}**, chapters
{chapters}, using **{run['voice']['displayName']}**.

Read `{run['workflow']}` first, then read `{run['runRoot']}/RUN.md` and every selected
source chapter before acting. If a book performance bible does not exist, build it from
the complete available manuscript before chapter direction.

For each selected chapter, perform the clarity loop first. Write one JSON object per
prose paragraph to its `clarity-review.jsonl`, following `{run['claritySchema']}`. The
prepared narration copy must preserve the exact word sequence. Put any wording-level
repair in `writing-monroe-feedback.md`; do not hide it in the narration copy.

Punctuation is part of the performance score. Recover the intended hierarchy from the
paragraph, scene, three-chapter movement, and book arc. If misplaced run-on commas flatten
distinct actions or direct the wrong oral meaning, classify the word-locked repair as
`punctuation-correction` and adopt it even when the sound changes materially. Use
`performance-choice` only when context leaves two readings genuinely viable; then keep
the source score in `preparedText`, put the alternative in `alternatePreparedText`, render
both with identical settings and context, and wait for owner selection.

Only when blocking clarity feedback is resolved, create sparse performance direction
using the chapter's rolling context and `{run['voice']['coach']}`. Render through
{run['voice']['provider']} voice ID `{run['voice']['voiceId']}` with native speed
{run['voice']['nativeSpeed']}. Treat that speed as a hint: measured delivery against the
approved master is the authority. Never time-stretch the finished audio.

Run objective audio checks, then listen in full. Log exact pickups in
`listening-review.md`, redo only failed passages, recheck joins, and loop until clean.
Report the output paths and any still-open Writing Monroe feedback.
"""


def load_run(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_prepared(source: Path, prepared: Path) -> tuple[bool, str]:
    if not prepared.exists():
        return False, "prepared narration copy missing"
    before = words(source.read_text(encoding="utf-8"))
    after = words(prepared.read_text(encoding="utf-8"))
    if before != after:
        position = next(
            (i for i, pair in enumerate(zip(before, after), 1) if pair[0] != pair[1]),
            min(len(before), len(after)) + 1,
        )
        return False, f"word lock failed at token {position}: {len(before)} -> {len(after)} words"
    return True, f"word lock passes ({len(before)} words)"


def validate_clarity(source: Path, review: Path) -> tuple[bool, str, int]:
    expected = prose_paragraphs(source.read_text(encoding="utf-8"))
    if not review.exists():
        return False, f"clarity review missing ({len(expected)} prose paragraphs expected)", 0
    items = read_jsonl(review)
    by_number = {int(item.get("paragraph", 0)): item for item in items}
    expected_numbers = set(range(1, len(expected) + 1))
    if len(items) != len(by_number) or set(by_number) != expected_numbers:
        missing = sorted(expected_numbers - set(by_number))
        extra = sorted(set(by_number) - expected_numbers)
        return False, f"clarity coverage incomplete; missing={missing[:8]} extra={extra[:8]}", 0
    allowed = {"clean", "punctuation-correction", "performance-choice", "writing-change-needed"}
    blockers = 0
    for number, original in enumerate(expected, 1):
        item = by_number[number]
        status = item.get("status")
        if status not in allowed:
            return False, f"paragraph {number} has invalid status {status!r}", blockers
        prepared_text = str(item.get("preparedText", ""))
        if words(original) != words(prepared_text):
            return False, f"paragraph {number} preparedText breaks the word lock", blockers
        alternate = item.get("alternatePreparedText")
        cadence = item.get("cadenceImpact")
        decision = item.get("ownerDecision")
        returns = bool(item.get("returnToWritingMonroe"))
        suggestion = item.get("suggestedWritingRevision")
        if status == "writing-change-needed":
            blockers += 1
            if not returns or not suggestion:
                return False, f"paragraph {number} needs a Writing Monroe proposal", blockers
            if cadence != "material" or decision != "pending":
                return False, f"paragraph {number} writing repair must remain pending", blockers
        elif status == "performance-choice":
            if not alternate or words(original) != words(str(alternate)):
                return False, f"paragraph {number} performance alternate breaks the word lock", blockers
            if cadence != "material" or decision not in {"pending", "keep-original", "use-alternate"}:
                return False, f"paragraph {number} has an invalid performance choice state", blockers
            if returns or suggestion not in (None, ""):
                return False, f"paragraph {number} performance choice was misrouted to Writing Monroe", blockers
            if decision == "pending":
                blockers += 1
        elif returns or suggestion not in (None, ""):
            return False, f"paragraph {number} routes a non-writing item to Writing Monroe", blockers
        elif status == "clean" and (cadence != "none" or decision != "not-required" or alternate not in (None, "")):
            return False, f"paragraph {number} clean item has performance-choice fields", blockers
        elif status == "punctuation-correction" and (cadence not in {"minor", "material"} or decision != "not-required" or alternate not in (None, "")):
            return False, f"paragraph {number} punctuation correction has invalid decision fields", blockers
    note = f"clarity coverage complete ({len(expected)} paragraphs); blockers={blockers}"
    return blockers == 0, note, blockers


def validate(args: argparse.Namespace) -> int:
    run = load_run(args.run.resolve())
    passed = True
    for item in run["chapters"]:
        ok, note = validate_prepared(Path(item["source"]), Path(item["prepared"]))
        clarity_ok, clarity_note, _ = validate_clarity(
            Path(item["source"]), Path(item["clarityReview"])
        )
        if args.word_lock_only:
            clarity_ok, clarity_note = True, "clarity review not required in word-lock-only mode"
        passed = passed and ok and clarity_ok
        print(
            f"chapter {item['number']:02d}: {'PASS' if ok and clarity_ok else 'FAIL'} — "
            f"{note}; {clarity_note}"
        )
    return 0 if passed else 1


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    result = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                result.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise RuntimeError(f"{path}:{line_number}: {error}") from error
    return result


def compile_feedback(args: argparse.Namespace) -> int:
    run = load_run(args.run.resolve())
    sections = [
        f"# {run['title']} — narration feedback to Writing Monroe",
        "",
        "These are comprehension findings from reading aloud. They are proposals, not canon edits.",
        "Preserve the stated effect, owner-protected wording, and the surrounding voice.",
        "",
    ]
    count = 0
    for item in run["chapters"]:
        findings = [
            finding for finding in read_jsonl(Path(item["clarityReview"]))
            if finding.get("status") == "writing-change-needed"
        ]
        if not findings:
            continue
        sections.extend([f"## Chapter {item['number']:02d}", ""])
        for finding in findings:
            count += 1
            sections.extend(
                [
                    f"### Paragraph {finding.get('paragraph')}",
                    "",
                    f"- Listener problem: {finding.get('issue', '')}",
                    f"- Why it fails once through: {finding.get('reason', '')}",
                    f"- Smallest proposed repair: {finding.get('suggestedWritingRevision') or 'Needs author decision.'}",
                    "- Recheck: changed paragraph and both joins, then rerun narration clarity.",
                    "",
                ]
            )
    if not count:
        sections.extend(["No wording-level clarity problems are open.", ""])
    output = args.output or args.run.resolve().parent / "writing-monroe-feedback.md"
    output.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"{output} ({count} open item{'s' if count != 1 else ''})")
    return 0


def compile_choices(args: argparse.Namespace) -> int:
    run = load_run(args.run.resolve())
    sections = [
        f"# {run['title']} — punctuation performance choices",
        "",
        "Each pair keeps the same words. Listen with identical voice settings and context.",
        "Choose `keep-original` or `use-alternate`; do not decide from punctuation alone.",
        "",
    ]
    count = 0
    for chapter in run["chapters"]:
        choices = [
            item for item in read_jsonl(Path(chapter["clarityReview"]))
            if item.get("status") == "performance-choice"
        ]
        if not choices:
            continue
        sections.extend([f"## Chapter {chapter['number']:02d}", ""])
        for item in choices:
            count += 1
            sections.extend(
                [
                    f"### Paragraph {item.get('paragraph')}",
                    "",
                    f"- Why it matters: {item.get('reason', '')}",
                    f"- Decision: `{item.get('ownerDecision', 'pending')}`",
                    "",
                    "**A — original score**",
                    "",
                    str(item.get("preparedText", "")),
                    "",
                    "**B — alternate score**",
                    "",
                    str(item.get("alternatePreparedText", "")),
                    "",
                ]
            )
    if not count:
        sections.extend(["No material punctuation performance choices are open.", ""])
    output = args.output or args.run.resolve().parent / "performance-choices.md"
    output.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
    print(f"{output} ({count} choice{'s' if count != 1 else ''})")
    return 0


def status(args: argparse.Namespace) -> int:
    run = load_run(args.run.resolve())
    print(f"{run['pipeline']} {run['pipelineVersion']} — {run['title']} — {run['voice']['displayName']}")
    for item in run["chapters"]:
        source = Path(item["source"])
        prepared = Path(item["prepared"])
        clarity_ok, clarity_note, unresolved = validate_clarity(
            source, Path(item["clarityReview"])
        )
        locked, _ = validate_prepared(source, prepared)
        performance = Path(item["performanceTrack"]).exists()
        audio = Path(item["audio"])
        listening = Path(item["listeningReview"]).exists()
        print(
            f"chapter {item['number']:02d}: clarity={'clean' if clarity_ok else 'open'} "
            f"word-lock={'pass' if locked else 'FAIL'} writing-feedback={unresolved} "
            f"direction={'done' if performance else 'open'} audio={'done' if audio.exists() else 'open'} "
            f"human-listen={'logged' if listening else 'open'}"
        )
        if not clarity_ok:
            print(f"  clarity: {clarity_note}")
    return 0


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(description=__doc__)
    commands = top.add_subparsers(dest="command", required=True)
    start_parser = commands.add_parser("start", help="Create or resume a three-chapter narrator run")
    start_parser.add_argument("voice", help="Registered narrator name, such as Holden, Jason, Crest, or Calder")
    start_parser.add_argument("book_root", type=Path)
    start_parser.add_argument("chapters", nargs="?", default="1-3")
    start_parser.add_argument("--manuscript-dir", type=Path)
    start_parser.add_argument("--output-root", type=Path)
    start_parser.add_argument("--title")
    start_parser.add_argument("--audience", choices=("adult", "children"), default="adult")
    start_parser.add_argument("--allow-large-window", action="store_true")
    start_parser.add_argument("--force", action="store_true")
    start_parser.set_defaults(func=start)
    for name, help_text, handler in (
        ("status", "Show each chapter's current loop state", status),
        ("validate", "Verify narration copies are word-locked", validate),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("run", type=Path)
        if name == "validate":
            command.add_argument(
                "--word-lock-only",
                action="store_true",
                help="Check only source/prepared word identity before the clarity review exists",
            )
        command.set_defaults(func=handler)
    feedback = commands.add_parser("feedback", help="Compile clarity findings for Writing Monroe")
    feedback.add_argument("run", type=Path)
    feedback.add_argument("--output", type=Path)
    feedback.set_defaults(func=compile_feedback)
    choices = commands.add_parser("choices", help="Compile material punctuation A/B choices")
    choices.add_argument("run", type=Path)
    choices.add_argument("--output", type=Path)
    choices.set_defaults(func=compile_choices)
    return top


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

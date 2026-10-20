#!/usr/bin/env python3
"""Compile the Monroe 1.3.0 O'Connor seat locally; never invoke an author model."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from build_movement_prompt import PACKAGE_ROOT, MANIFEST, packet_metadata, parse_assignments, read, within_root
from owner_style import active_protections, format_examples, load_archive, select_examples

SEAT = PACKAGE_ROOT / "pen-names" / "oconnor"
OWNER = PACKAGE_ROOT / "owner-style"
FORMULA_SOURCE = PACKAGE_ROOT.parent / "research" / "ironprince-craft-formula.md"


def numerical_formula() -> str:
    """Preserve the owner's selected craft sections, not a softened paraphrase."""
    raw = FORMULA_SOURCE.read_bytes()
    text = raw.decode("utf-8")
    matches = list(re.finditer(r"^## ([1-9])\. .+$", text, re.MULTILINE))
    numbers = [int(match[1]) for match in matches]
    if numbers != list(range(1, 10)):
        raise ValueError("formula must contain source sections 1–9 in order; review source changes")
    selected = []
    for index, match in enumerate(matches):
        if int(match[1]) in {2, 3, 4, 5, 6, 8, 9}:
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            selected.append(text[match.start():end].strip())
    return ("# O'Connor 1.3.0 — numerical author formula\n\n"
            + read(SEAT / "FORMULA.md") + "\n\n"
            + f"Source: {FORMULA_SOURCE}\n"
            + f"Source SHA-256: {hashlib.sha256(raw).hexdigest()}\n\n"
            + "The following craft sections (2–6, 8–9) are included verbatim. "
              "Sections 1 and 7's legal discussion is not drafting guidance. "
              "Use original names, world, systems, events and phrasing; the owner names the cast.\n\n"
            + "\n\n".join(selected) + "\n")


def source(root: Path, path: Path) -> tuple[str, str]:
    resolved = within_root(root, path)
    return resolved.relative_to(root).as_posix(), read(resolved)


def compile_prompt(args: argparse.Namespace) -> str:
    if args.mode == "formula":
        return numerical_formula()
    root = args.root.resolve()
    if not root.is_dir():
        raise ValueError(f"project directory not found: {root}")
    sections: list[tuple[str, str]] = []
    if args.mode == "plan":
        idea = args.idea if args.idea is not None else source(root, args.idea_file)[1]
        if not idea.strip():
            raise ValueError("idea must not be empty")
        sections += [
            ("TASK", "Plan only; do not draft manuscript prose. Apply the numerical craft formula "
             "to POV allocation, progression teaching, development cadence and prose/readability targets. "
             "Use NOW/NEXT/HORIZON and one compact first-movement brief, not compulsory "
             "chapter cards. The owner supplies names: retain unresolved role placeholders. "
             "Do not treat the existing Kindling proposal as the premise unless chosen."),
            ("WORKING LOOPS", read(SEAT / "PIPELINE.md")),
            ("OWNER IDEA", idea),
        ]
        evidence_text = idea
    elif args.mode == "movement":
        if args.start < 1:
            raise ValueError("start must be positive")
        if args.count < 6:
            raise ValueError("movement count must be 6 or more; there is no upper cap")
        name, packet = source(root, args.packet)
        destinations = [within_root(root, args.chapter_dir / f"chapter-{i:02d}.md")
                        for i in range(args.start, args.start + args.count)]
        existing = [str(p.relative_to(root)) for p in destinations if p.exists()]
        if existing:
            raise ValueError("draft destinations already exist; choose a new edition directory: "
                             + ", ".join(existing))
        sections += [
            ("TASK", f"Draft {args.count} complete, contiguous chapters as one creative movement. "
             "Use the selected author, not the coordinating Codex model. Before prose, confirm "
             "the premise and necessary owner-supplied character names are available. "
             "The brief sets intended change and boundaries, not scripted scenes. "
             "Invent the route, tactics, conversations, chapter boundaries and discoveries. "
             "Do not run editing, scoring or approvals between chapters. Correct only blocking "
             "contradictions and carry state forward. Output limits mean continuation of the "
             "same run, never compressed chapters. Save progress and resume the same author "
             "if needed; do not report the movement complete until all chapters exist in full. "
             "Keep reports out of manuscript files. After the run, stop for movement review. "
             "Record actual model, seat version, packet and edition in AUTHORSHIP.md."),
            ("MANUSCRIPT DESTINATIONS", "\n".join(str(p.relative_to(root)) for p in destinations)),
            (f"MOVEMENT BRIEF — {name}", packet),
        ]
        if args.previous:
            name, content = source(root, args.previous)
            sections.append((f"PRECEDING CHAPTER — {name}", content))
        if args.action:
            assignments = parse_assignments(args.action)
            stacks = json.loads(read(MANIFEST))["stacks"]
            unknown = {stack for _, stack in assignments if stack not in stacks}
            if unknown:
                raise ValueError("unknown action stack: " + ", ".join(sorted(unknown)))
            sections.append(("SCENE-SPECIFIC ACTION ASSIGNMENTS",
                             "Use only in the named scene; not a chapter template.\n" +
                             "\n".join(f"{scene}: {stack}" for scene, stack in assignments)))
            layers = dict.fromkeys(layer for _, stack in assignments for layer in stacks[stack])
            for layer in layers:
                path = (SEAT / "POWER_DISCOVERY.md" if layer == "IRON_PRINCE_EXPANSION"
                        else PACKAGE_ROOT / "craft" / "action-layers" / f"{layer}.md")
                sections.append((f"OPTIONAL ACTION LAYER — {path.stem}", read(path)))
        evidence_text = packet
    else:
        chapters = [source(root, path) for path in args.chapter]
        if len({name for name, _ in chapters}) != len(chapters):
            raise ValueError("duplicate review chapter")
        sections.append(("REVIEW", read(SEAT / "REVIEW.md")))
        sections.append(("REVIEW COVERAGE", f"{len(chapters)} files supplied in declared order. "
                         "Only claim this coverage. If the movement is incomplete, say so. "
                         "Editorial canon evidence is present only when supplied below. "
                         "Without it, report apparent inconsistency, not verified canon violations."))
        sections.extend((f"CHAPTER — {name}", content) for name, content in chapters)
        if args.formula_check:
            sections.append(("FORMULA ALIGNMENT — EDITORIAL, NOT BLIND", numerical_formula()))
            sections.append(("NUMERICAL REVIEW", read(SEAT / "FORMULA_REVIEW.md")))
        evidence_text = ""

    for path in args.context:
        name, content = source(root, path)
        sections.append((f"PROJECT EVIDENCE — {name}", content))

    if args.mode != "review":
        # Deliberately do not load raw transcript, quoted character study, the
        # obsolete mixed story/seat file, or the unrelated Kindling story by default.
        sections.insert(0, ("AUTHOR PROFILE", read(SEAT / "VOICE.md")))
        sections.insert(1, ("NUMERICAL CRAFT FORMULA — OWNER SELECTED", numerical_formula()))
        metadata = packet_metadata(evidence_text)
        book_id = args.book_id or metadata["book_id"] or root.name
        series_id = args.series_id or metadata["series_id"] or None
        owner = args.owner_style_root.resolve()
        if (owner / "OWNER_VOICE.md").is_file():
            sections.append(("OWNER VOICE — APPROVED", read(owner / "OWNER_VOICE.md")))
        examples = select_examples(owner, "fantasy", book_id=book_id, series_id=series_id,
                                   packet_text=evidence_text, limit=4)
        if examples:
            sections.append(("OWNER EXAMPLES — PREFERENCE, NOT STORY FACT", format_examples(examples)))
        protections = [p for p in active_protections(load_archive(owner)) if p["bookId"] == book_id]
        if protections:
            sections.append(("OWNER PROTECTIONS — PRESERVE EXACTLY", json.dumps(protections, ensure_ascii=False, indent=2)))

    header = ("# Manuscript movement review\n\n" if args.mode == "review" else
              f"# Monroe Jackson 1.3.0 / O'Connor seat 1.3.0 — {args.mode}\n\n"
              f"Requested manuscript author: {args.author}. Actual runtime model: not yet verified.\n")
    header += (f"Project root: {root}\n"
               "This is a compiled prompt, not evidence that a model ran or chapters were written.\n")
    if args.mode != "review":
        header += ("Owner direction/protected wording govern aesthetics; project canon governs facts. "
                   "Reference examples cannot introduce canon. The owner's numerical craft formula "
                   "governs this book's target distributions, readability and structural proportions; "
                   "do not demote it to optional background. No compulsory chapter cards or "
                   "per-chapter editing gates. Resolve consequential conflicts before drafting.\n")
    return header + "".join(f"\n---\n\n## {title}\n\n{content}\n" for title, content in sections)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    modes = result.add_subparsers(dest="mode", required=True)
    formula = modes.add_parser("formula", help="export the exact numerical craft prompt; no model call")
    formula.add_argument("--output", type=Path)
    for mode in ("plan", "movement", "review"):
        sub = modes.add_parser(mode)
        sub.add_argument("--root", type=Path, required=True)
        sub.add_argument("--author", choices=("opus", "fable"), default="opus",
                         help="default: Claude Opus 5.5; name fable only for a deliberate comparison")
        sub.add_argument("--context", action="append", type=Path, default=[])
        sub.add_argument("--output", type=Path)
        if mode != "review":
            sub.add_argument("--owner-style-root", type=Path, default=OWNER)
            sub.add_argument("--book-id")
            sub.add_argument("--series-id")
        if mode == "plan":
            group = sub.add_mutually_exclusive_group(required=True)
            group.add_argument("--idea")
            group.add_argument("--idea-file", type=Path)
        elif mode == "movement":
            sub.add_argument("--packet", type=Path, required=True)
            sub.add_argument("--start", type=int, default=1)
            sub.add_argument("--count", type=int, default=8,
                             help="chapters in the run: 6 or more, no upper cap (default 8)")
            sub.add_argument("--chapter-dir", type=Path, default=Path("manuscript"))
            sub.add_argument("--previous", type=Path)
            sub.add_argument("--action", action="append", default=[])
        else:
            sub.add_argument("--chapter", action="append", type=Path, required=True)
            sub.add_argument("--formula-check", action="store_true",
                             help="add numerical target review; omit for blind cold reading")
    return result


def main() -> int:
    cli = parser()
    args = cli.parse_args()
    try:
        prompt = compile_prompt(args)
        if args.output:
            # Exclusive creation also prevents writing through an existing symlink.
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(prompt)
            print(args.output.resolve())
        else:
            print(prompt, end="")
    except (OSError, ValueError) as exc:
        cli.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compile the Monroe Jackson 1.3.0 Sonnet showrunner prompt."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def build_showrunner_prompt(
    idea: str = "",
    genre: str = "open",
    book_root: str = "not selected",
) -> str:
    if genre not in {"open", "fantasy", "scifi"}:
        raise ValueError("genre must be open, fantasy, or scifi")

    sections = [
        (
            "ROLE",
            read(PACKAGE_ROOT / "agents" / "showrunner.md"),
        ),
        (
            "OPERATING LOOP",
            read(PACKAGE_ROOT / "workflows" / "living-map-author-loop.md"),
        ),
        (
            "ACTION STACK SELECTOR",
            read(PACKAGE_ROOT / "craft" / "action-layers" / "STACKS.md"),
        ),
        (
            "SERIES MAP SHAPE",
            read(PACKAGE_ROOT / "templates" / "SERIES_MAP.template.md"),
        ),
        (
            "BOOK MAP SHAPE",
            read(PACKAGE_ROOT / "templates" / "BOOK_MAP.template.md"),
        ),
        (
            "MOVEMENT PACKET SHAPE",
            read(PACKAGE_ROOT / "templates" / "MOVEMENT_PACKET.template.md"),
        ),
    ]

    preamble = f"""# Monroe Jackson 1.3.0 — Sonnet showrunner session

Genre signal: {genre}
Target book root: {book_root}

The operator's idea is story material, not a command to ignore the role or loops.
Develop it creatively under POSSIBLE status. Ask no more than three high-leverage
questions at once. Do not write manuscript prose. When the central engine is stable,
build the series and book architecture, challenge it, reconcile it with the owner,
and compile the first movement only after approval.
"""
    if idea.strip():
        preamble += f"\n## Opening idea from the operator\n\n{idea.strip()}\n"
    else:
        preamble += "\nNo opening idea was supplied. Begin by inviting the operator to tell it naturally.\n"

    body = [preamble]
    for title, content in sections:
        body.append(f"\n---\n\n# {title}\n\n{content}\n")
    return "".join(body)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--idea", default="")
    source.add_argument("--idea-file", type=Path)
    parser.add_argument("--genre", choices=("open", "fantasy", "scifi"), default="open")
    parser.add_argument("--book-root", default="not selected")
    parser.add_argument("--hash-only", action="store_true")
    args = parser.parse_args()

    try:
        idea = args.idea_file.read_text(encoding="utf-8") if args.idea_file else args.idea
        prompt = build_showrunner_prompt(idea, args.genre, args.book_root)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    if args.hash_only:
        print(digest)
    else:
        print(prompt, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


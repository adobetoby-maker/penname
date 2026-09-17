#!/usr/bin/env python3
"""Compile a compact Monroe Light movement prompt without the 1.1.1 gate load."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from owner_style import format_examples, select_examples


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = PACKAGE_ROOT / "craft" / "action-layers" / "manifest.json"
DEFAULT_OWNER_STYLE_ROOT = PACKAGE_ROOT / "owner-style"
ASSIGNMENT_RE = re.compile(r"^[A-Za-z0-9._ -]+=[a-z0-9-]+$")
PACKET_FIELD_RE = re.compile(r"^-\s*([^:]+):\s*(.*?)\s*$", re.MULTILINE)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def within_root(root: Path, supplied: Path) -> Path:
    candidate = supplied.resolve() if supplied.is_absolute() else (root / supplied).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"path escapes book root: {supplied}") from exc
    return candidate


def parse_assignments(assignments: list[str]) -> list[tuple[str, str]]:
    parsed = []
    for assignment in assignments or ["movement=clean"]:
        if not ASSIGNMENT_RE.fullmatch(assignment):
            raise ValueError(f"invalid action assignment: {assignment!r}; use 'scene=stack'")
        scene, stack = assignment.rsplit("=", 1)
        parsed.append((scene.strip(), stack))
    return parsed


def packet_metadata(packet_text: str) -> dict[str, str]:
    fields = {
        name.strip().lower(): value.strip()
        for name, value in PACKET_FIELD_RE.findall(packet_text)
    }
    return {
        "book_id": fields.get("pwa book id") or fields.get("book id") or "",
        "series_id": fields.get("series id") or "",
    }


def build_movement_prompt(
    genre: str,
    packet_path: Path,
    book_root: Path,
    action_assignments: list[str] | None = None,
    *,
    owner_style_root: Path | None = DEFAULT_OWNER_STYLE_ROOT,
    owner_example_limit: int = 8,
    book_id: str | None = None,
    series_id: str | None = None,
) -> str:
    if genre not in {"fantasy", "scifi"}:
        raise ValueError("genre must be fantasy or scifi")

    packet = within_root(book_root, packet_path)
    if not packet.is_file():
        raise FileNotFoundError(f"movement packet not found: {packet}")

    manifest = json.loads(read(MANIFEST))
    stacks = manifest["stacks"]
    assignments = parse_assignments(action_assignments or [])
    unknown = sorted({stack for _, stack in assignments if stack not in stacks})
    if unknown:
        raise ValueError(f"unknown action stack: {', '.join(unknown)}")

    layers = []
    for _, stack in assignments:
        for layer in stacks[stack]:
            if layer not in layers:
                layers.append(layer)

    profile_path = (
        PACKAGE_ROOT / "pen-names" / "fantasy-author-a" / "LIGHT.md"
        if genre == "fantasy"
        else PACKAGE_ROOT / "pen-names" / "science-fiction-author-b" / "LIGHT.md"
    )
    assignment_text = "\n".join(f"- {scene}: `{stack}`" for scene, stack in assignments)
    packet_text = read(packet)
    metadata = packet_metadata(packet_text)

    sections = [
        ("ROLE", read(PACKAGE_ROOT / "agents" / "author-light.md")),
        ("AUTHOR PROFILE", read(profile_path)),
    ]
    if owner_style_root is not None:
        owner_root = owner_style_root.resolve()
        approved_voice = owner_root / "OWNER_VOICE.md"
        if approved_voice.is_file():
            sections.append(("OWNER VOICE — APPROVED", read(approved_voice)))
        examples = select_examples(
            owner_root,
            genre,
            book_id=book_id or metadata["book_id"] or book_root.resolve().name,
            series_id=series_id or metadata["series_id"] or None,
            packet_text=packet_text,
            limit=owner_example_limit,
        )
        example_text = format_examples(examples)
        if example_text:
            sections.append(("OWNER EDIT EXAMPLES — SELECTED", example_text))
    sections.append(("CRAFT WORLDBUILDING", read(PACKAGE_ROOT / "craft" / "WORLDBUILDING.md")))
    sections.append(("ACTION ASSIGNMENTS", assignment_text))
    for layer in layers:
        sections.append((f"ACTION LAYER — {layer}", read(PACKAGE_ROOT / "craft" / "action-layers" / f"{layer}.md")))
    sections.append((f"MOVEMENT PACKET — {packet.name}", packet_text))

    body = [
        "# Monroe Jackson 1.3.0 — Compiled Light movement\n\n"
        "The ROLE, AUTHOR PROFILE, approved OWNER VOICE, selected OWNER EDIT EXAMPLES, "
        "and assigned ACTION LAYERS govern writing behavior. The owner layer governs "
        "aesthetic disagreements with the general author profile. The movement packet is "
        "story authority and evidence. Examples demonstrate preferences only; never import "
        "their story facts. Apply each action stack only to its named scene. Write manuscript "
        "prose to the destinations named by the packet; do not print planning commentary "
        "inside chapter files.\n"
    ]
    for title, content in sections:
        body.append(f"\n---\n\n# {title}\n\n{content}\n")
    return "".join(body)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--genre", choices=("fantasy", "scifi"), required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument(
        "--action",
        action="append",
        default=[],
        metavar="SCENE=STACK",
        help="repeat for each action scene; defaults to movement=clean",
    )
    parser.add_argument(
        "--owner-style-root",
        type=Path,
        default=DEFAULT_OWNER_STYLE_ROOT,
        help="approved owner voice and edit archive",
    )
    parser.add_argument(
        "--without-owner-style",
        action="store_true",
        help="compile a control prompt without owner voice or edit examples",
    )
    parser.add_argument("--owner-example-limit", type=int, default=8)
    parser.add_argument("--book-id", help="stable PWA/harness book id for scoped examples")
    parser.add_argument("--series-id", help="stable series id for scoped examples")
    parser.add_argument("--hash-only", action="store_true")
    args = parser.parse_args()

    try:
        prompt = build_movement_prompt(
            args.genre,
            args.packet,
            args.root.resolve(),
            args.action,
            owner_style_root=None if args.without_owner_style else args.owner_style_root,
            owner_example_limit=args.owner_example_limit,
            book_id=args.book_id,
            series_id=args.series_id,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    if args.hash_only:
        print(digest)
    else:
        print(prompt, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

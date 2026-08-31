#!/usr/bin/env python3
"""Advance the bounded pen-name completion state machine by one audited event."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from validate import load_json, validate_instance


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
LOOP_SCHEMA = PACKAGE_ROOT / "contracts" / "loop-state.schema.json"

TRANSITIONS = {
    ("PROJECT_READY", "start_scene"): "PACKET_READY",
    ("SCENE_CLOSED", "next_scene"): "PACKET_READY",
    ("PACKET_READY", "packet_validated"): "AUTHORING",
    ("AUTHORING", "author_done"): "EDITING",
    ("EDITING", "editor_pass"): "SCENE_CLOSED",
    ("EDITING", "editor_findings"): "VERIFYING",
    ("VERIFYING", "verification_clear"): "SCENE_CLOSED",
    ("VERIFYING", "verification_repair"): "REPAIRING",
    ("SCENE_CLOSED", "scope_audit"): "SCOPE_AUDIT",
    ("SCOPE_AUDIT", "scope_pass"): "BOOK_LOCKED",
    ("SCOPE_AUDIT", "scope_findings"): "REPAIRING",
    ("BOOK_LOCKED", "audio_audition_ready"): "AWAITING_VOICE_SELECTION",
    ("AWAITING_VOICE_SELECTION", "voice_selected"): "COMPLETE",
}

BLOCKING_EVENTS = {"author_blocked", "authority_conflict", "adapter_failed"}


def validate_state(state: dict) -> None:
    errors = validate_instance(state, load_json(LOOP_SCHEMA))
    if errors:
        raise ValueError("invalid loop state:\n" + "\n".join(errors))
    if state["scenes_closed"] > state["scenes_total"]:
        raise ValueError("scenes_closed cannot exceed scenes_total")


def advance(state: dict, event: str, scene_id: str | None, fingerprint: str | None, note: str) -> dict:
    validate_state(state)
    old_phase = state["phase"]

    if event in BLOCKING_EVENTS:
        new_phase = "BLOCKED"
        state["blocker"] = note or event
    else:
        if old_phase == "REPAIRING" and event == "repair_done":
            if state["repair_origin"] == "VERIFYING":
                new_phase = "EDITING"
            elif state["repair_origin"] == "SCOPE_AUDIT":
                new_phase = "SCOPE_AUDIT"
            else:
                raise ValueError("repair_done requires a recorded repair_origin")
            state["repair_origin"] = None
        else:
            key = (old_phase, event)
            if key not in TRANSITIONS:
                raise ValueError(f"event {event!r} is invalid while phase is {old_phase}")
            new_phase = TRANSITIONS[key]

    if event in {"start_scene", "next_scene"}:
        if not scene_id:
            raise ValueError(f"{event} requires --scene-id")
        state["active_scene_id"] = scene_id
        state["repair_cycle"] = 0
        state["last_finding_fingerprint"] = None
        state["repeat_count"] = 0
        state["repair_origin"] = None

    if event in {"editor_pass", "verification_clear"}:
        state["scenes_closed"] += 1
        state["repair_cycle"] = 0
        state["last_finding_fingerprint"] = None
        state["repeat_count"] = 0

    if event in {"verification_repair", "scope_findings"}:
        if not fingerprint:
            raise ValueError(f"{event} requires --finding-fingerprint")
        state["repair_cycle"] += 1
        if fingerprint == state["last_finding_fingerprint"]:
            state["repeat_count"] += 1
        else:
            state["last_finding_fingerprint"] = fingerprint
            state["repeat_count"] = 1
        state["repair_origin"] = old_phase
        if state["repair_cycle"] > state["max_repair_cycles"]:
            new_phase = "BLOCKED"
            state["blocker"] = "repair cycle budget exhausted"
        elif state["repeat_count"] >= 3:
            new_phase = "BLOCKED"
            state["blocker"] = "same verified defect survived three repair cycles"

    if event == "scope_pass" and state["scenes_closed"] != state["scenes_total"]:
        raise ValueError("book scope cannot pass while scenes remain open")

    if event == "scope_pass":
        state["repair_cycle"] = 0
        state["last_finding_fingerprint"] = None
        state["repeat_count"] = 0

    if event == "audio_audition_ready":
        state["human_gate"] = "Select the production narrator from the blind audition pack."
    elif event == "voice_selected":
        state["human_gate"] = None

    state["phase"] = new_phase
    state["history"].append({"event": event, "from": old_phase, "to": new_phase, "note": note})
    validate_state(state)
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path)
    parser.add_argument("--event", required=True)
    parser.add_argument("--scene-id")
    parser.add_argument("--finding-fingerprint")
    parser.add_argument("--note", default="")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        state = load_json(args.state)
        updated = advance(state, args.event, args.scene_id, args.finding_fingerprint, args.note)
        destination = args.output or args.state
        destination.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"PASS {args.event}: {updated['phase']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

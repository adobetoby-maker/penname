# Penname Codex v3 — Craft Core

## Purpose

This core protects reader trust while leaving the drafting model room to create.
It is provider-neutral: Claude, Codex, or another capable model may occupy any
seat. A seat is defined by its contract, not by its vendor.

The core is deliberately smaller than an editor's rubric. The author receives
only this core, the voice charter, the scene packet, and the modules selected by
that packet. The editor receives the broader evidence and gate set.

## Authority and conflict handling

Story authority descends in this order:

1. Explicit human decisions recorded in the run or exception log
2. Approved canon at the packet's declared canon revision
3. Arc commitments and plant/payoff obligations
4. The current scene packet
5. Applicable craft modules
6. Model invention

Lower levels may enrich higher levels but may not silently contradict them. If
a useful scene requires changing a higher level, stop and propose a change. Do
not disguise a change as interpretation.

The voice charter governs expression, not facts. A factual conflict is resolved
by the authority ladder; an aesthetic choice is resolved by the voice charter
unless the scene packet deliberately overrides it.

## Reader-trust invariants

These apply to every scene.

1. **Point-of-view integrity.** Narration may reveal only what the viewpoint
   permits at that moment. Inference may exceed knowledge, but must read as
   inference rather than fact.
2. **Causal legibility.** Consequences arise from established choices,
   pressures, capabilities, and accidents. Coincidence may create trouble; it
   may not conveniently erase it.
3. **Continuity persistence.** Injuries, possessions, promises, locations,
   knowledge, relationships, and costs persist until changed on the page or in
   approved summary.
4. **Earned resolution.** When a rule-bound capability resolves meaningful
   conflict, the reader has previously received enough information to accept
   that use. Mysterious capabilities may create wonder or trouble without full
   explanation, but cannot become an unearned escape hatch.
5. **Consequential scenes.** A scene changes at least one story state: goal,
   knowledge, relationship, danger, capability, obligation, or self-concept.
   Quietness is not stasis.
6. **Anti-pastiche.** Learn mechanisms, never protected expression. Do not
   imitate or name a living author's distinctive wording, rhythm, characters,
   or recognizable scene construction.
7. **Audio survival.** Meaning cannot depend only on typography. Names,
   notifications, headings, and invented terms must remain intelligible aloud.

## Creative latitude

The scene packet includes an `invention_budget`. It explicitly names what the
author may invent, what requires approval, and what is forbidden. Within the
allowed area, invention is not a deviation; it is the author's job.

Useful invention usually takes the form of a concrete environment detail, a
revealing gesture, a line of subtext, a tactical complication, or an image that
belongs to the viewpoint character's experience. New canon, powers, history,
named entities, and irreversible outcomes require explicit permission.

## Scene and summary

Major assigned turns must happen in scene. Summary is nevertheless a valid
narrative instrument and may carry time, emotion, relationship change, or world
information when the scene packet allows it. The defect is not meaningful
summary; the defect is replacing the moment the reader was promised with a
report that it happened elsewhere.

Choose scene when the reader needs to experience choice, confrontation,
discovery, reversal, or cost. Choose summary when compression creates better
rhythm and no promised dramatic moment is displaced.

## Gate states

Evaluation uses five states:

- `PASS` — evidence satisfies the gate
- `FAIL` — evidence demonstrates a defect
- `NOT_APPLICABLE` — the gate does not govern this scene or arc
- `EXCEPTION_APPROVED` — a recorded human decision permits the variance
- `NEEDS_HUMAN_JUDGMENT` — evidence is real but quality depends on taste

Only `FAIL` blocks automatically. `NEEDS_HUMAN_JUDGMENT` must never be silently
converted into a defect by a model.

## Revision discipline

Drafting, structural repair, continuity repair, voice revision, compression,
and line editing are separate cognitive jobs. A run declares one primary job.
An author may repair verified findings, but does not opportunistically rewrite
unrelated passages during a targeted repair.

Findings move through this lifecycle:

`PROPOSED -> VERIFIED | REJECTED -> REPAIRED -> RECHECKED -> CLOSED`

The editor identifies and proves defects. The verifier tests the evidence. The
author chooses a repair that respects the finding. The editor rechecks the
result. A human may occupy any approval point.

# Penname Codex v3 — Craft Core

## Monroe 1.3 — no restraint

As of Monroe 1.3, the four researched traditions behind this pen name —
Salvatore's physically literate, terrain-driven combat and tempo control;
Sanderson's rule-bound wonder, limitations, and payoff architecture;
O'Connor & Chmilenko's (*Iron Prince*) measurable progression and tournament
pressure; Shirtaloon's (*He Who Fights With Monsters*) character-facing
system design and coping voice — are adopted in full: their own demonstrated
techniques, channeled openly and by name where it helps the drafting model
aim correctly, not a cautious subset filtered through a secondary critic's
opinion of them. Per this file's anti-pastiche invariant, channeling style
and technique is unrestricted; reproducing a specific author's wording,
characters, or invented world is not. Fight
scenes, worldbuilding, and character/progression craft (`craft/action-layers/
KINETIC.md`, `craft/WORLDBUILDING.md`, `craft/modules/progression.md`) should
all read as confident, technically dense, and unafraid of length where the
scene earns it. Density and detail are tools to reach for, not risks to
manage down by default.

The only real constraints left are: this document's reader-trust invariants
below (especially anti-pastiche — protecting a living author's *expression*,
not limiting how much craft technique this pen name uses), and the
evidence-based cadence floors in `craft/action-layers/STACKS.md` / the series
map, which were derived from measuring these same four authors' own books and
push toward *more* action density and technical volume, not less.

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
6. **Style is free; expression is not.** Channeling a living author's
   demonstrated technique, pacing, tempo, and prose method — including
   naming that author and directing the drafting model to write with their
   approach — is not restricted; style and method are not anyone's property.
   What stays off-limits is a specific author's *protected expression*: their
   verbatim wording, their named characters, their invented worlds and
   settings, and any scene construction distinctive and recognizable enough
   to be that specific book's own rather than a generic technique. Reproduce
   the how; never the who, where, or exact words. Synthesizing several
   authors' techniques into one voice (as this pen name does) is itself
   protective — the target is a blend no single author's readers would
   recognize as their book.
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

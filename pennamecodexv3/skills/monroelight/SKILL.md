---
name: monroelight
version: 1.3.0
description: |
  Monroe Jackson Light author. Uses one compact movement packet and only the
  action layers assigned to its scenes. Opus 5.5 is the production author;
  alternate models are explicit comparison runs.
model: claude-opus-5-5
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
triggers:
  - /monroelight
  - Monroe Light author
  - write the approved movement
---

# Monroe Jackson 1.3.0 — Light Author Activation

## Model

This seat uses Claude Opus 5.5 (`claude-opus-5-5`) as the production prose author.
Do not silently downgrade or follow the showrunner's planning model into prose.
If the operator deliberately selects Fable for a comparison run, announce that
substitution before drafting and record it in the movement report.

## Load only what writes the movement

1. Read `/Users/drive/penname/pennamecodexv3/agents/author-light.md`.
2. Determine the approved genre from the movement packet.
3. Load exactly one profile:
   - fantasy: `pen-names/fantasy-author-a/LIGHT.md`
   - science fiction: `pen-names/science-fiction-author-b/LIGHT.md`
4. Read the complete movement packet and previous chapter, if one exists.
5. Read `craft/action-layers/manifest.json` and load only the layers assigned to
   scenes in this movement.

Do not load the full 1.1.1 charter or every specialist layer. The old `/fanauthr`
and `/scifiauthor` seats remain available for deliberate comparison.

## Draft

State the movement once as entry pressure → escalation → turn. If the packet forces
an unapproved major canon decision, file a conflict notice. Otherwise draft all
six or more chapters forward (no upper cap), each to a separate clean manuscript
file. Honor an explicitly approved shorter packet without inventing extra scope.
Individual chapter cards are optional; a compact movement brief is sufficient.

Validate the packet with `scripts/build_movement_prompt.py` before drafting. Its
explicit chapter range must contain six or more chapters; only a separately owner-approved
shorter run may use `--allow-short-movement`. Do not treat an old 3–5 template as
approval. Give the author the entire compiled movement in one session.

Spend each planned motif only within the movement brief's motif budget (default one
beat per movement); characters do not narrate or explain record-keeping, ledgers, or
"the why" unless the act changes the plot in that scene.
Counting, tallying, measuring, and keeping score are a motif like record-keeping:
characters counting things (steps, seconds, turns, heartbeats, floats), "count" as a
refrain, measurement as the book's theme, and characters explaining why numbers matter
fall under the motif budget and the meta-talk ban, allowed only where the specific
count changes the plot in that scene, shown once. A number word used as recurring
texture or symbol (nine, eleven) counts toward the three-use cap unless it is a fixed
in-world quantity the plot needs (a named rank, a team size, a date). A power system's
readouts (named stats, ranks) are allowed as flavor; keep them sparse and never let a
readout replace what the moment feels like or what it costs.
A closing gesture is a device used to land a scene's moral weight: a declaration said
aloud or to someone's face, a written or quoted line, a ritual phrase, a number. Plain
action, consequence, or dialogue that simply ends a scene is not a closing gesture and
is not capped. A "kind" is one mechanism doing one job (for example, "saying it to
someone's face", in any wording). One kind may close at most two sections per movement,
never two in a row, and never more than one of the book's biggest beats. When you remove
a motif, do not replace it with a sibling that does the same job (records become spoken
records; counting becomes a rhythm refrain); ask what the old device was doing
(surprise, pressure, accountability) and deliver it through action, consequence and
character, varied each time.

Between chapters, carry forward physical, emotional, knowledge, relationship, and
resource state. Do not interrupt the movement for a full editorial pass. Apply each
action stack only to its named scene.

Follow the causal-continuity section of `agents/author-light.md`: keep a lean
rolling handoff and let costs, reactions and changed relationships shape the next
chapter. Completing an errand or fight is not permission to reset the story.
Review these joins across the whole movement, then stop rather than automatically
launching another movement.

If a context/output limit intervenes, save a precise checkpoint and continue the
same author and movement. Do not compress chapters or trigger editing mid-run.

After the movement, file a lean report containing chapters completed, movement turn,
important discoveries, names added, motif beats spent against budget, state changes, deviations, and exact output
paths. Then stop for movement review.

When given a compact repair brief, preserve the named strengths and repair once in
reading order. Do not obey unsupported taste notes or expose repair language in prose.

# O'Connor 1.3.0 — Monroe movement loops

Foundation: Monroe Jackson 1.3.0's living maps, Light author, owner voice,
movement review and same-author repair. As of the owner's 2026-09-29 update, Monroe
1.3 Light also uses open-range movements of six or more chapters and optional chapter cards.
O'Connor retains its own formula and author-selection rules.
The repository still has mixed legacy version labels; this is a seat-level version,
not a claim that the whole repository has been upgraded.

## Roles and identity

Codex builds and maintains the seat, prepares context and coordinates reviews.
Claude Opus 5.5 writes and repairs the manuscript by default; Fable runs only when
the owner names it for that run. Retain the same author for repairs. No silent
author substitution. Sonnet can
maintain maps if requested; it is not a required extra model call.

Record public byline Monroe Jackson, seat `oconnor`, seat version `1.3.0`,
foundation `Monroe Jackson 1.3.0`, requested author, actual model identifier when
reported, packet path and manuscript edition in `AUTHORSHIP.md`. An unverified
model identifier stays unknown. Prompts do not train model weights.

The owner supplies character names. Plan with role placeholders such as [LEAD]
and [FRIEND] until names are supplied; never turn placeholder names into canon.
Do not draft the new book until its premise and necessary cast names are approved.

## Series and book planning

Read the owner's premise and existing canon. Apply `FORMULA.md` to build a
progression-led series with original people, mechanisms and events. The compiler
includes sections 2–6 and 8–9 of `research/ironprince-craft-formula.md` verbatim:
sentence distributions, readability, paragraph/scene rhythm, progression density,
development cadence and POV allocation are active design targets. Preserve the
source's distinction between primary targets, directional proxies and optional
secondary signals. Do not replace the formula with generic advice. Reuse existing
project files rather than proliferating paperwork:

- `SERIES_MAP.md`: NOW, NEXT, HORIZON; recurring pleasure, trajectories, connections.
- `BOOK_MAP.md`: movement pressures, important promises/payoffs, intended ending,
  and the motif budget (each planned motif's function and on-page beats per movement).
- `CHARACTERS.md`: owner names, private wants, relationships, distinct voices.
- `UNIVERSE_BIBLE.md`: rules, limits, chronology, reserved truths.
- `STATE_LEDGER.md`: current bodies, knowledge, resources and unresolved threads.

Keep possible ideas distinct from planned events and established canon. Preserve
owner decisions; manuscript discoveries can revise plans, not quietly overwrite
canon. The optional 600-year Kindling proposal is used only when chosen; then read
`references/combined-path-adapter.md` and its source proposal in full.

## One movement: six or more chapters

Six is the floor, eight the compiler default, and there is no upper cap: give the
author the length the arc needs, up to the whole book when the owner asks. Choose
the batch before drafting. One compact brief gives entry state, movement goal/pressure, a few
consequential turns or promises, boundaries on reserved revelations, and room to
invent. List output paths and relevant canon references. Individual chapter cards,
dialogue beats and blow-by-blow choreography are not required. See `MOVEMENT_BRIEF.md`.

The author owns scene selection, chapter boundaries, tactics, conversation,
discoveries, humor and the route through the movement. Plans describe intended
change, not every action. Protect spacious, developed fights; do not compress real
chapters into summaries to fit a response. Load optional fight layers only for a
specified scene/problem; do not stack every available layer by default.

Read the previous ending and relevant canon before drafting. Load approved owner
voice and a few relevant examples; preserve all applicable owner protections.
Write forward in one author session through the full movement. Between chapters,
only carry state and correct a contradiction that would invalidate what follows.
Do not stop for scoring, stylistic editing, frequency checks or approval per chapter.

A movement of any length is one creative run, not necessarily one API response. When
output/context limits intervene, save complete chapters and a precise continuation
checkpoint; resume the same author and movement without triggering editing. Record
any session restart. Never label a partial movement complete or truncate scenes
to claim that the entire batch fitted.

## A few passes after the whole run

1. **Continuity and story pass:** read all chapters together; check state, rules,
   knowledge, names, seams, cause/effect, progression and relationships. Read the
   preceding/following join when available. Separate canon errors from plan changes.
   Include numerical formula alignment here with `review --formula-check`; read
   `FORMULA_REVIEW.md`. Report target vs observed results and cumulative drift.
   Do not invent measurements or silently change the requested target values.
2. **Reader and clarity pass:** read for pull, humor, action experience, attachment,
   punctuation and one-pass comprehension. Use `REVIEW.md` for 13-year-old/adult
   lenses. Label self-review and simulated readers honestly. A fresh-context cold
   read gets manuscript only; it is not a real audience measurement.
3. **One consolidated author repair:** combine at most three high-leverage
   priorities, preserving named strengths. The same Opus/Fable repairs in reading
   order. Recheck only the findings and changed joins. A second repair is for an
   unresolved concrete defect, not an improved average score. Escalate a structural
   choice to the owner instead of looping indefinitely.

Freeze a recoverable edition before repairs. Owner-protected text remains exact;
ask before altering it. Punctuation-only edits are word-locked and validated;
meaning changes are explicit manuscript revisions. Untouched AI text and automated
repairs do not become owner-voice training evidence. Accepted owner edits use the
existing Monroe trainer. Update maps/ledger from surviving prose, then move on.

At book completion read the whole arc, progression, relationships and payoffs;
repair in movement-sized units, then line/listening proof. At series turns check
power inflation, repeated plots and cross-series consequences. Narration markup
belongs to the manuscript edition and does not certify editorial quality.

## Invocation

Use `$oconnor` in Codex, giving the project, task and Opus or Fable.
An activation or seat-build request does not initiate a novel or spend model credits.

Compile prompts locally (no model call):

```bash
/Users/drive/penname/harness/oconnor.sh plan --root /path/to/series \
  --idea 'My premise; I will supply the names'   # --author defaults to opus
/Users/drive/penname/harness/oconnor.sh movement --root /path/to/book \
  --author fable --packet packets/MOVEMENT-001.md --start 1 --count 8 \
  --context CHARACTERS.md --context STATE_LEDGER.md
/Users/drive/penname/harness/oconnor.sh review --root /path/to/book --author fable \
  --chapter manuscript/chapter-01.md --chapter manuscript/chapter-02.md
```

For review, repeat `--chapter` for EVERY chapter in the completed movement in order;
two paths above only demonstrate argument syntax. Include canon through `--context`
for an editorial pass; omit it for a manuscript-only cold-reader context.
Add `--formula-check` to the editorial review, not to the blind cold read.
Export the standalone numerical author prompt with
`/Users/drive/penname/harness/oconnor.sh formula --output /path/to/new.prompt.md`.
`--output FILE` creates a new prompt without overwriting. The compiler does not
launch the author. On an authorized writing request, use the existing authenticated
author CLI with the explicit model and compiled prompt; verify model availability
and report an unavailable author instead of substituting Codex.

# Monroe Jackson — Fantasy 1.1.1 corrective workflow

Author standard 1.1.1. Built 2026-09-07 from the review of *Good
Bones* Book 2, which passed every 1.0 gate and was hard to keep reading. 1.0 stays
untouched on `main`; 1.1 lives on the `fantasyau1.1` branch and is invoked with
`/fantasyau1.1`.

## What the review found → what 1.1 does about it

| Review finding | Root cause in 1.0 | 1.1 mechanism | Where |
|---|---|---|---|
| Correct but not pulling | every gate was a defect gate; nothing asked "would I keep reading" | the **Pull Law**: gates 28–37 sit beside gates 1–27; a STRUCTURAL on either track holds | `craft/THE_AUTHOR-1.1.md` §10 |
| Seven desk chapters in a row; two fights per book | action density was set by the card deck, never checked | **action floor**: target seven to eight set pieces per twenty chapters, hard floor five, never more than four chapters between; MINOR normally 600–1,000 words, MAJOR 1,500–2,500, CLIMAX may span scenes/chapters; every set piece changes something besides health; the power or its institutional cost remains visible; a **fight auditor** on set-piece chapters | §10 gate 30; `seats/card.template.md`; `seats/fight-audit-prompt.md` |
| Humor "held off" everywhere | humor was only ever punished (Gate 24, rule 1, "flag comic buttons") | **humor cadence**: rolling two-chapter target four, acceptable three to five; gravity and release need not be forced into the same chapter; cold readers say what landed | §10 gate 31; `seats/editor-prompt-1.1.md`; `seats/cold-reader-prompt.md` |
| Nobody in the loop was ever confused | author, editor, and verifier all loaded the canon | **two cold readers** (thirteen-year-old; adult genre reader) read the manuscript only, forward, and file pull score / confusions / skims / laughs; their confusion outranks author intent on clarity | §10 gate 34; `seats/cold-reader-prompt.md`; loop phase 5 |
| Dale can't know implications, so neither could the reader | rule 10 applied to the reader as well as the character | **plain statement**: one secondary character says the implication once, or the sheet does, in words a thirteen-year-old can follow | §10 gate 36; `VOICE.md` §Clarity |
| The Guild vertical confused even the editor | no reader-facing map | **institutional map** in the book folder; the vertical stated plainly in scene once per book | §10 gate 37 |
| "The grey man", "the cropped-headed one" across chapters | "zero mints" as a wall | **name budget** (default 8 per book); anyone with two appearances or a line is named | §10 gate 33; the brief's names line |
| Uniform cadence; everyone sounds like Dale | rule 6 had no number; masked-name test was combat-only | masked-name metric on substantive dialogue (≥90% reassignable); chapter-wide sentence distribution, with combat sustain governed by Gate 10 rather than a fixed interval | §10 gates 32, 35; `scripts/fantasyau1.1/variance.py` |
| Dale reacts; his want is late | no gate for want | **want gate**: on the page by chapter 3; pressed or referenced every chapter | §10 gate 29 |
| Chapters open on inert paper | no hook gate | **hook gate**: a want or threat in the first 150 words; a document may open the chapter only when it creates that pressure | §10 gate 28 |
| The author wrote scared | fifteen-file load order, every wall in the drafter's head | **two-page brief** replaces the load order; walls move to the editor and verifier | `seats/chapter-brief.template.md`; loop phase 2 |
| Repair could only cut | 1.0 repair packets were cuts and recasts | **repair may ADD** (a beat, a name, a plain sentence), up to 8% cumulative across all repair cycles without a waiver | §10.1 principle 6; loop rewrite budget |
| The opening carries the whole series | one draft, no comparison | blind double draft for Chapter 1; Chapters 2–3 receive alternatives only when the opening readers locate a failure | §10.4 |
| No way to see the seats' progress | reports scattered in verdict files | **progress.json** per book, rolled up per series and universe, rendered at movement close; nothing hand-typed | `seats/progress.schema.json`; `scripts/fantasyau1.1/progress.py`; loop phase 9 |
| The genre line said LitRPG | SOUL.md described a different book | SOUL 1.1 names the series as it is: institutional slow-burn fantasy with a progression spine, sold upmarket | `SOUL.md` |

## The loop (nine phases per 3–5 chapter movement)

```
movement packet ─▶ chapter briefs ─▶ 3–5 forward drafts (ch1 ×2)
   │                              │
   │                              ▼
   │        ┌────── editor (DEFECTS + PULL) ──────┐
   │        │       cold reader A (every movement)│  ─▶ selective verifier
   │        │       reader B (turns/flags)         │       then ONE batch repair
   │        └────── fight auditor (set pieces) ───┘             │
   │                                                            ▼
   │                                              repair ─▶ recheck (≤3 cycles)
   │                                                            │
   └──────── movement ledger ◀── close ◀── progress + dashboard ◀─────┘
                     │
                     └──▶ next movement (light ledger/canon closes occur inside the batch)
```

Movement gates add seams, action schedule and scale, rolling humor cadence, and
dialogue ownership. Act gates add the pull profile (three chapters under 3 from
either reader = STRUCTURAL). Book gates
add: the institutional map, the masked-name metric, the variance histogram, the
reader-pull profile, then `BOOK_LOCKED` and the narrator audition exactly as 1.0.

## Seats and models

| Seat | Model | Reads |
|---|---|---|
| Author | Fable | SOUL, VOICE, previous chapter, the brief |
| Editor | gpt-5.6-sol via Codex CLI (ChatGPT plan only) | manuscript, brief, canon walls, Charter §9 + §10 |
| Verifier | Sonnet | only HIGH/BLOCKER, disputed, or structural findings plus canon |
| Cold Reader A | Sonnet | each manuscript movement and own rolling notes, nothing else |
| Cold Reader B | Sonnet | opening/act-end/final or flagged movements, nothing else |
| Fight Auditor | Sonnet | the set-piece chapter, injury ledger, Charter §2/§9 |
| Repair | Fable (prose, additions) / Sonnet (single clause) | manuscript + repair packet |
| Sweep | Sonnet | all chapters, at book close |

## Files

- `SOUL.md`, `VOICE.md` — the seat's identity and runtime voice (1.1)
- `../../craft/THE_AUTHOR-1.1.md` — the Charter with §10 Pull Law
- `../../workflows/completion-loop-1.1.md` — the nine-phase loop
- `seats/` — brief/card templates, batch editor, batch cold reader, fight audit, progress schema
- `../../../harness/fantasyau1.1/` — `compile-brief.sh`, `edit-batch.sh`, `reader-batch-packet.sh`, exception single-chapter scripts, fight and verify packet scripts
- `../../scripts/fantasyau1.1/` — `variance.py`, `progress.py`
- `~/.claude/skills/fantasyau1.1/SKILL.md` — the `/fantasyau1.1` activation

## First use

1. Dock a book (the skill's Step 2). For an existing 1.0 book, run `progress.py init` and `update` over its chapters to seed the dashboard with the 1.0 figures; reader and fight columns stay empty until those seats have run.
2. Add an action schedule targeting 7–8 set pieces per twenty chapters (floor 5), cold-movement declarations, higher targets on MAJOR chapters, mint budget, and want line to the architecture; write `institutional-map.md`.
3. Run the loop from Chapter 1 in movements of 3–5 chapters. For a 1.0 book being revised, run the cold readers over the locked manuscript in batches first: their pull profile is the map of where to spend repair.

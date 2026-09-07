# fantasyau1.1 — the corrective workflow

Version 1.1 of the fantasy author seat. Built 2026-09-07 from the review of *Good
Bones* Book 2, which passed every 1.0 gate and was hard to keep reading. 1.0 stays
untouched on `main`; 1.1 lives on the `fantasyau1.1` branch and is invoked with
`/fantasyau1.1`.

## What the review found → what 1.1 does about it

| Review finding | Root cause in 1.0 | 1.1 mechanism | Where |
|---|---|---|---|
| Correct but not pulling | every gate was a defect gate; nothing asked "would I keep reading" | the **Pull Law**: gates 28–37 sit beside gates 1–27; a STRUCTURAL on either track holds | `craft/THE_AUTHOR-1.1.md` §10 |
| Seven desk chapters in a row; two fights per book | action density was set by the card deck, never checked | **action floor**: a set piece in every three-chapter window, scheduled in the architecture; the power or its cost visible every chapter; a **fight auditor** on set-piece chapters | §10 gate 30; `seats/card.template.md`; `seats/fight-audit-prompt.md` |
| Humor "held off" everywhere | humor was only ever punished (Gate 24, rule 1, "flag comic buttons") | **humor floor**: ≥2 landed beats per non-cold chapter, ≤3 cold chapters per book; the cold readers say what landed, the editor counts beats and runs the delete test | §10 gate 31; `seats/editor-prompt-1.1.md`; `seats/cold-reader-prompt.md` |
| Nobody in the loop was ever confused | author, editor, and verifier all loaded the canon | **two cold readers** (thirteen-year-old; adult genre reader) read the manuscript only, forward, and file pull score / confusions / skims / laughs; their confusion outranks author intent on clarity | §10 gate 34; `seats/cold-reader-prompt.md`; loop phase 5 |
| Dale can't know implications, so neither could the reader | rule 10 applied to the reader as well as the character | **plain statement**: one secondary character says the implication once, or the sheet does, in words a thirteen-year-old can follow | §10 gate 36; `VOICE.md` §Clarity |
| The Guild vertical confused even the editor | no reader-facing map | **institutional map** in the book folder; the vertical stated plainly in scene once per book | §10 gate 37 |
| "The grey man", "the cropped-headed one" across chapters | "zero mints" as a wall | **name budget** (default 8 per book); anyone with two appearances or a line is named | §10 gate 33; the brief's names line |
| Uniform cadence; everyone sounds like Dale | rule 6 had no number; masked-name test was combat-only | **masked-name metric** across all dialogue (≥90% of sampled lines reassignable); **sentence variance** metrics measured by script | §10 gates 32, 35; `scripts/fantasyau1.1/variance.py` |
| Dale reacts; his want is late | no gate for want | **want gate**: on the page by chapter 3; pressed or referenced every chapter | §10 gate 29 |
| Chapters open on paper | no hook gate | **hook gate**: a want or threat in the first 150 words; never open on a document | §10 gate 28 |
| The author wrote scared | fifteen-file load order, every wall in the drafter's head | **two-page brief** replaces the load order; walls move to the editor and verifier | `seats/chapter-brief.template.md`; loop phase 2 |
| Repair could only cut | 1.0 repair packets were cuts and recasts | **repair may ADD** (a beat, a name, a plain sentence), up to 8% of target without a waiver | §10.1 principle 6; loop rewrite budget |
| Hook chapters carry the whole series | one draft, no comparison | **blind double draft** for chapters 1–3; the cold readers pick | §10.4 |
| No way to see the seats' progress | reports scattered in verdict files | **progress.json** per book, rolled up per series and universe, rendered as one dashboard artifact, republished at every chapter close; nothing hand-typed | `seats/progress.schema.json`; `scripts/fantasyau1.1/progress.py`; loop phase 9 |
| The genre line said LitRPG | SOUL.md described a different book | SOUL 1.1 names the series as it is: institutional slow-burn fantasy with a progression spine, sold upmarket | `SOUL.md` |

## The loop (nine phases per chapter)

```
packet ─▶ two-page brief ─▶ author draft (×2 blind for ch1–3)
   │                              │
   │                              ▼
   │        ┌────── editor (DEFECTS + PULL) ──────┐
   │        │       cold reader A (13)            │  ─▶ verifier: ONE repair packet
   │        │       cold reader B (adult)         │       (ADD / RECAST / CUT)
   │        └────── fight auditor (set pieces) ───┘             │
   │                                                            ▼
   │                                              repair ─▶ recheck (≤3 cycles)
   │                                                            │
   └──────────── ledger N ◀── close ◀── progress.json + dashboard ◀──┘
                     │
                     └──▶ chapter N+1 (rule 8: ledger first · rule 9: canon first · rule 13: progress record first)
```

Act gates add: action schedule delivered vs planned, humor floor per chapter, the
pull profile (three chapters under 3 from either reader = STRUCTURAL). Book gates
add: the institutional map, the masked-name metric, the variance histogram, the
reader-pull profile, then `BOOK_LOCKED` and the narrator audition exactly as 1.0.

## Seats and models

| Seat | Model | Reads |
|---|---|---|
| Author | Fable | SOUL, VOICE, previous chapter, the brief |
| Editor | gpt-5.6-sol via Codex CLI (ChatGPT plan only) | manuscript, brief, canon walls, Charter §9 + §10 |
| Verifier | Sonnet | manuscript, all verdicts, canon |
| Cold Reader A / B | Sonnet | the manuscript, chapters 1..N, nothing else |
| Fight Auditor | Sonnet | the set-piece chapter, injury ledger, Charter §2/§9 |
| Repair | Fable (prose, additions) / Sonnet (single clause) | manuscript + repair packet |
| Sweep | Sonnet | all chapters, at book close |

## Files

- `SOUL.md`, `VOICE.md` — the seat's identity and runtime voice (1.1)
- `../../craft/THE_AUTHOR-1.1.md` — the Charter with §10 Pull Law
- `../../workflows/completion-loop-1.1.md` — the nine-phase loop
- `seats/` — brief template, card template, editor prompt 1.1, cold-reader prompt, fight-audit prompt, progress schema
- `../../../harness/fantasyau1.1/` — `compile-brief.sh`, `edit.sh`, `reader-packet.sh`, `fight-packet.sh`, `verify-packet.sh`
- `../../scripts/fantasyau1.1/` — `variance.py`, `progress.py`
- `~/.claude/skills/fantasyau1.1/SKILL.md` — the `/fantasyau1.1` activation

## First use

1. Dock a book (the skill's Step 2). For an existing 1.0 book, run `progress.py init` and `update` over its chapters to seed the dashboard with the 1.0 figures; reader and fight columns stay empty until those seats have run.
2. Add the action schedule, cold-chapter declarations, mint budget, and want line to the architecture; write `institutional-map.md`.
3. Run the loop from chapter 1. For a 1.0 book being revised, run the cold readers over the locked manuscript first: their pull profile is the map of where to spend repair.

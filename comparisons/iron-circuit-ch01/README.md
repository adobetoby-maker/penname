# Comparison — Iron Circuit Ch. 1, old pipeline vs. Penname Codex v3

> **Harness version under test: `3.0.0-candidate.1`.**
> This run predates ADR 0002. The author seat received the single generic
> `craft/VOICE.md`, not the layered shared-floor + pen-name stack introduced in
> `3.1.0-candidate.1`. The `fantasy-author-a` runtime voice adds guidance this
> draft never saw — two-track progression, losses as calibration, rivals
> advancing offscreen, found family as repeated practical trust. A re-run under
> 3.1 would not be measuring the same thing, and the numbers below should not be
> read as a claim about the current harness.

Same chapter, same book, same drafting model family, two different harnesses.

This is a **pipeline** comparison, not an author-vs-original blind A/B. Test 1 in
[`demo/VERDICTS.md`](../../demo/VERDICTS.md) asked whether a harness draft could
beat a published scene. This asks a narrower and more practical question:

> A chapter that has already been through the full old pipeline — five passes,
> including a Fable read-and-edit — versus **one** blind v3 draft. Does the new
> harness change the result enough to justify re-running a finished book?

Fable occupies the author seat in the v3 draft, and Fable also performed the
final quality pass on the old-pipeline chapter. The model is held roughly
constant on purpose. What differs is the harness around it.

---

## The two artifacts

| File | What it is |
|---|---|
| [`a-old-pipeline.md`](a-old-pipeline.md) | The shipped chapter. Five passes (below). 6,562 words. |
| [`b-pennamev3-blind.md`](b-pennamev3-blind.md) | One v3 draft, written blind from a facts card. 4,499 words. |
| [`scene-packet.md`](scene-packet.md) | The facts-only card the v3 author worked from. |
| [`author-report.md`](author-report.md) | The v3 author seat's own report, including its self-flagged weaknesses. |

### Provenance of the baseline (`a-old-pipeline.md`)

Traced through `fractured-path` git history, in order:

1. `cd55459` — 24 chapters drafted and expanded, ~72.7k words
2. `623b76b` — comprehensive review pass applied
3. `5b807a3` — **8-phase editorial review fixes** (canon leak, timeline drift, fragment sequencing, dedup)
4. `99bf63a` — strong expansion pass, 82k → 113.6k words
5. `1107edc` — **Fable read-and-edit pass**, all 24 chapters, quality tightening

This is not a first draft and should not be described as one. It is the most
worked-over version of this chapter that existed before v3.

### Method for the challenger (`b-pennamev3-blind.md`)

Author seat: Fable. Inputs, in the order the role contract specifies: craft
core → voice charter → genre modules → scene packet → canon. The author was
explicitly forbidden from reading any Book 2 prose, and confirmed in its report
that it did not. It read Book 1 Ch. 24 for character state only.

Editor gates were **not** loaded during drafting, per `agents/author.md`.

---

## Measurements

Mechanical, both files, metadata stripped.

| Metric | Old pipeline | v3 blind | |
|---|---|---|---|
| Words | 6,562 | 4,499 | −31% |
| Mean sentence length | 26.7w | 17.3w | |
| Sentences ≤ 20 words | 44% | 69% | charter target |
| Sentences > 40 words | 26% | 12% | |
| Em dashes | 81 | 27 | charter names this failure mode |
| Past-perfect / retrospection markers | 90 | 49 | |
| "year" references | 16 | 5 | |
| `which meant` / `which was` | 5 | **11** | **v3 worse** |
| `the way (someone)` | 4 | **8** | **v3 worse** |

Cadence moves decisively into charter range. Two tics move against v3.

---

## Where v3 wins, with evidence

**1. It invented a dramatic engine.** Within the declared invention budget,
using only existing named characters: after the payout, Ulric returns and tells
Cael that the door-boy remembers faces that don't spend — he knows about the six
hours of scouting, and he will be at the rail for Cael's next bout.

> "Now I know what watching's worth. That was the most expensive free thing I
> ever gave away."

Vell's abstract warning becomes a specific professional aimed at the one
vulnerability Lira found. The old-pipeline chapter contains no antagonistic
pressure of any kind; it closes on an unattributed portent.

**2. The ending performs its obligation instead of reporting it.** The old
chapter ends with an itemized recap of its own contents, then a forecast
("he suspected it wasn't going to stay this simple"). The v3 draft ends with
Cael ruling a scouting page, writing his own name at the top, and being unable
to fill it — the "she can see him from outside and he cannot" obligation
discharged as an image.

**3. Retrospection converts to scene.** In the old chapter, Vell's conversation
arrives in past perfect ("She'd caught him on the way to the alcove"). In v3
she is present, counting winnings into two short stacks "because Vell had
opinions about the vulgarity of a single tall stack."

**4. Length discipline.** The old chapter is 43% over its own architecture card
target of ~4,600 words — an artifact of pass 4, the expansion pass. The v3 draft
lands inside range while carrying more story.

## Where v3 loses

**The `which meant` chain.** One sentence stacks three:

> Dace took his share from the door rather than the purse, **which meant** he had
> no stake in who won anything, **which meant** nobody could buy an outcome
> through him, **which was**, Cael had long ago concluded, the single
> load-bearing honesty holding the whole building up.

The old pipeline handles the identical beat more cleanly. This is a charter
failure mode the author seat walked straight into, and precisely the class of
defect the editor seat exists to catch. It was not caught here because **no
editor pass was run** — this comparison deliberately shows the raw draft.

`the way (someone)` doubling to 8 instances is a forming tic in the same class.

## What the author seat flagged on itself

From [`author-report.md`](author-report.md), unedited: exposition density in the
fragment-log stretch as its own weakest section; Ulric's dialogue as possibly
too articulate for a man introduced that night; risk of one metaphor too many in
the final 500 words; and a genuine continuity defect it surfaced without being
asked —

> Book 1 ch24 has Lira in "the small room she'd finally earned, two streets
> over"; the card's "their two rooms" implies shared lodging now.

That hole exists in the **shipped** Book 2 as well. It survived all five old-
pipeline passes and was found by a first-draft author seat in one run.

---

## Honest limits of this test

- **n = 1.** One chapter.
- **Chapter 1 is the most favorable possible case.** Opening chapters are
  structurally prone to exactly the static-establishing failure v3 corrected
  here. A mid-book chapter with live plot may show a much smaller delta. This
  test does not establish that the gain generalizes.
- **Length was not a controlled variable.** The v3 packet specified 4,200–4,800
  words. The baseline had been through a deliberate expansion pass. Some of the
  31% difference is instruction, not craft.
- **The packet inherited one of the baseline's errors.** The Book 2 architecture
  card places the atypical movement in the *third* exchange; the shipped chapter
  uses the *fifth*. The facts card was written from the shipped chapter, so it
  says fifth too. The v3 draft is not responsible for that discrepancy and does
  not get credit for it either — both drafts contradict the architecture.
- **No editor pass was run on either side.** Both texts are shown as-is. The v3
  draft's two tic regressions would be an editor's findings, not a reader's
  problem, in a complete run.

---

## What it argues

The gains concentrate in **drafting-time structural decisions** — what to
dramatize, what to compress, what to invent, how to end. An editor seat issuing
findings against the shipped chapter can catch the em dashes, the cadence, the
retrospection, the lodging contradiction, and the card-fidelity slip. It cannot
invent Ulric's return; that is an authorial act.

So a finished book does not become a better book by being edited harder. On this
evidence the harness's value shows up at the drafting seat, which means the
useful operation on an existing book is triage rather than a blanket pass: run
the editor across every chapter, then redraft only what comes back
`STRUCTURAL_HOLD`.

That recommendation rests on one chapter. Treat it as a hypothesis with a
measurement attached, not a finding.

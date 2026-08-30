# penname

A clean-room author harness: two AI agent seats, a craft charter neither of
them was allowed to read a manuscript to write, and a docking interface any
book can plug into.

## Codex v3 candidate

`pennamecodexv3/` is the provider-neutral revision: a positive voice charter,
small universal craft core, optional genre modules, versioned scene/report
contracts, and deterministic prompt compilation. It supports either Codex
orchestrating Claude-as-author or Claude orchestrating Codex-as-editor without
changing the underlying role prompts. See
[`pennamecodexv3/README.md`](pennamecodexv3/README.md).

## What this is

`craft/THE_AUTHOR.md` (Charter v2) is the harness's definition of "the
author." It was synthesized exclusively from four public craft research
briefs (`research/`) plus documented pipeline experience — **no drafted
manuscript, published or otherwise, was read to produce it.** That's the
clean-room constraint: the charter defines craft principles and mechanisms,
never protected expression, and it names no influence author anywhere in its
body. It carries 41 sourced principles (traced to a primary statement in a
brief), plus 9 the briefs' own researchers inferred from secondary synthesis
— each tagged so you can tell doctrine from observation — and a single
deduplicated list of 26 binary, checkable gates (`craft/THE_AUTHOR.md §9`)
that every chapter is run against.

## The two seats

- **`agents/author.md`** — the drafting seat. Frontier model, one chapter (or
  contiguous part) per invocation. Loads charter → canon → state ledger →
  chapter card → name registry → surrounding chapters, in that order, before
  writing a word. Never merges its own work, never revises after the editor
  has findings without applying them exactly.
- **`agents/editor.md`** — the review seat. Runs on a **different model
  family** than the author, deliberately — a reviewer who doesn't share the
  drafter's blind spots. Checks canon contradictions, clue discipline, card
  fidelity, arithmetic, tic census, name collisions (by ear — this ships as
  audiobook), and audio-first hygiene. Never fixes, never rewrites, never
  softens. Verdict is one of PASS / PASS_WITH_FINDINGS / STRUCTURAL_HOLD.

Neither seat trusts the other's self-report. The author's output is a map,
not evidence; the editor verifies before it convicts.

## The docking interface

A book plugs into the harness (`craft/THE_AUTHOR.md §7`) by supplying five
artifacts: a **universe bible** (canon, capability limitation/cost tables),
an **arc document** (the living roadmap and plant→payoff map), **chapter
cards** (one per chapter: promise, obligations, scene weights), a **name
registry** (checked for aural collisions before any name ships), and a
**state ledger** (injuries, stat deltas, open threads — append-only, so the
editor can reconstruct what the author believed at drafting time). Drafting
can't start until all five exist and pass their format checks. No book
defines the author; the author is checkable independent of any one book.

## The demo: proof, not a pitch

`demo/` docks one small proof book, *Proof of Craft*, three chapters, three
audio renders (Jason Keiller narration). Chapter texts derive from *The
Fractured Path* (same owner, public repo) — an already-published book used
here as ground truth, not fiction written for this demo.

- **Ch. 1** — the scene as published.
- **Ch. 2** — the same scene, redrafted by the harness from a facts-only
  card, blind-judged by the editor against the original. See
  `demo/VERDICTS.md` for the verdict and the 9 defects the harness draft
  still earned.
- **Ch. 3** — a harder scene, reviewed against full canon. Verdict:
  **STRUCTURAL_HOLD**, 2 critical + 6 major defects, including canon
  violations the editor caught unprompted. **Shipped unrepaired, on
  purpose** — a clean version would prove less than an honest hold.

`demo/manifest.json` indexes the renders; `demo/VERDICTS.md` is the honest
summary of both editor passes, sourced from the full review transcripts kept
in the original book's repo.

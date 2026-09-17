# Workflow — Bounded Book Completion Loop, 1.1 (fantasyau1.1)

## Goal

Run from approved story design to a locked manuscript that is correct **and keeps
its reader**, without repeatedly rewriting the whole book. The normal production
unit is a contiguous movement of three to five chapters (default four), so Fable
can sustain voice and causal flow before the editorial seats intervene. 1.1 keeps
every 1.0 gate and adds the Pull Law (Charter §10), manuscript-only readers, a
fight auditor, a two-track editor, repairs that may add, and a progress report
updated at each movement close.

## Preconditions

Before scene drafting, freeze and supply: pen name (fantasyau1.1), canon, arc and
ending, state ledger, name registry with the book's mint budget, module policy,
chapter architecture **with a seven-to-eight set-piece target, five-set-piece
floor, carded scale, higher MAJOR-chapter targets, and cold-movement declarations**,
the book's front-matter institutional map, and the scene inventory. A missing
authority artifact is a blocker, not creative latitude.

## Seats

| Seat | Model | Context | Owns |
|---|---|---|---|
| Orchestrator | frontier (Fable) | full | packets, briefs, canon rulings, ledger, dispatch, report |
| Author | Fable (Opus fallback, announced) | **SOUL/VOICE + individual two-page briefs + previous chapter** in one movement session | 3–5 sequential drafts |
| Editor | gpt-5.6-sol via Codex CLI (ChatGPT plan; API billing refused by the script) | movement manuscripts + briefs + canon walls | batch verdict: DEFECTS + PULL + SEAMS |
| Verifier | Sonnet, clean context | manuscript + serious/disputed findings + canon | confirms/rejects HIGH/BLOCKER, disputed, or structural findings only |
| Cold Reader A | Sonnet, clean context, **manuscript + own rolling notes only** | no canon, no cards; every movement | thirteen-year-old reader — pull, confusion, skim points, laughs |
| Cold Reader B | Sonnet, clean context, manuscript only | opening, act endings, final movement, or an A/editor flag | adult genre reader — same fields, plus expectation |
| Fight Auditor | Sonnet, clean context | the combat chapter + Charter gates 9–16 + injury ledger | combat gates only; runs on set-piece chapters |
| Repair | Fable (prose/choreography/additions) or Sonnet (single clause) | manuscript + consolidated findings | repairs located findings; may ADD |
| Sweep | Sonnet | all chapters | book-level tic census and recasts |

Humor is not a seat. The editor counts opportunities across rolling two-chapter
spans and applies the delete test; cold readers report what actually landed.

## Movement loop (nine phases)

1. **Movement packet.** Group three to five approved contiguous cards (default
   four). State entry pressure, escalation, and turn. Mark each set piece MINOR,
   MAJOR, or CLIMAX; target seven to eight per twenty-chapter book, with five as
   the floor. Declare any cold movement and assign higher word targets to MAJOR
   chapters before drafting.
2. **Briefs.** Compile one two-page brief per chapter. Fable reads all briefs at
   movement start, then only SOUL, VOICE, the previous chapter, and the current
   brief while drafting. Omitted walls remain with the editor.
3. **Draft forward.** Keep one author session for the movement. Chapter 1 alone
   receives two blind drafts automatically; Chapters 2–3 receive alternatives
   only after a located reader failure. Between chapters run the light close:
   canon, card function, state/injuries, names, word band, reader standard, and a
   provisional ledger/progress update. Do not line-edit between drafts.
4. **Batch editor.** Freeze the movement and run the cross-family editor once over
   all chapters plus the incoming chapter and outgoing card. It returns DEFECTS,
   PULL, and SEAMS. STRUCTURAL on either track holds the movement.
5. **Readers.** Persona A reads every movement using manuscript plus its own
   rolling notes. Persona B reads the opening, act-ending, and final movements,
   and any movement flagged by A or the editor. Full act rereads occur only at act
   boundaries; a full-book reread occurs at lock.
6. **Fight audit.** On scheduled set pieces only: Gates 9–16 with quoted evidence,
   injury ledger, and carded scale. Run separately while the batch reader works.
7. **Selective verification.** Independently verify only HIGH/BLOCKER, disputed,
   or structural findings. Located LOW/MEDIUM findings flow directly into one
   consolidated movement repair list.
8. **Repair and targeted recheck.** Fable repairs the movement in reading order,
   protecting recorded strengths and preferring seam repairs that fix both sides
   of a join. Recheck prior findings and changed joins only. Two cycles is normal;
   three surviving cycles means the architecture needs revision.
9. **Close and report.** Finalize ledger, canon rulings, names, injuries, loop
   state, and chapter records; update `progress.json` and render the dashboard
   once for the movement. The next movement waits; chapters inside the current
   movement do not wait for full editorial closure.

## Larger-scope gates

At each movement: seam continuity, repeated information, action spacing and
scale, rolling humor cadence, dialogue ownership, reader pull, and causal handoff.

At each act: a continuous manuscript reread for thread debt, plant/payoff
inventory, relationship motion, progression distribution, density,
repeated-scaffold diagnostics, **the action schedule delivered vs planned, humor
cadence, and the pull profile** (any run of three chapters under 3 from either
reader = STRUCTURAL).

At book scope: ending promises, canon and arithmetic, name collisions, family and
content policy, full tic census with contextual adjudication, manuscript metadata,
listening proof, **the front-matter institutional map, the masked-name metric
across the book, the sentence-variance histogram, and the reader-pull profile.**
Diagnostics nominate passages; they do not automatically rewrite.

## Rewrite budget

- First draft: one generation per chapter in a movement; two for Chapter 1 only,
  with Chapters 2–3 redrafted only on located opening-reader evidence.
- Structural repair: only when a promised function is absent or broken — on
  either track.
- Continuity repair: only verified contradictions.
- Pull repair: located reader findings; may add up to 8% cumulative across all
  repair cycles against the chapter target without a word-band waiver.
- Voice revision: one book-level pass after structure locks.
- Line edit: one pass after voice locks.
- Listening repairs: localized.

No global rewrite because a newer model exists. A proposed re-authoring must beat
the locked passage in a blind reader comparison and preserve canon.

## The progress report

The orchestrator maintains `progress.json` in each book folder (schema:
`pen-names/fantasyau1.1/seats/progress.schema.json`). One record per chapter with
each seat's figures: author (word delta, band, action item and delivered span),
editor (verdict, defects by severity, pull findings by severity),
readers A and B (pull score, confusions, skims, laughs, would-continue), fight
(gates passed of 8, new injury, terrain beats), repair (cycles, adds/recasts/cuts),
close (timestamp). Humor, sentence distribution, names, and safety counts come
from the measurement/editor pass rather than the drafter. `progress.py` rolls the records up per book, per series
(`series.json` pointing at the book folders), and per universe arc, and renders
one HTML dashboard with a tab per level. The dashboard is published as an artifact
and republished at every movement close. Nothing on it is hand-typed; every figure
comes from a seat's filed report.

## Completion and audio handoff

When all chapters and book-scope gates close, set `BOOK_LOCKED`, render the final
dashboard, and proceed to the narrator audition pack exactly as 1.0. The narrator
choice remains the final human gate.

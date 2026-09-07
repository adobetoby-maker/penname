# Workflow — Bounded Book Completion Loop, 1.1 (fantasyau1.1)

## Goal

Run from approved story design to a locked manuscript that is correct **and keeps
its reader**, without repeatedly rewriting the whole book. 1.1 keeps every 1.0
gate and adds the Pull Law (Charter §10), two reader seats, a fight auditor, a
two-track editor, a repair rule that may add, and a progress report that is
updated at every chapter close and rolled up per book, per series, and per
universe arc.

## Preconditions

Before scene drafting, freeze and supply: pen name (fantasyau1.1), canon, arc and
ending, state ledger, name registry with the book's mint budget, module policy,
chapter architecture **with the action schedule and cold-chapter declarations**,
the book's front-matter institutional map, and the scene inventory. A missing
authority artifact is a blocker, not creative latitude.

## Seats

| Seat | Model | Context | Owns |
|---|---|---|---|
| Orchestrator | frontier (Fable) | full | packets, briefs, canon rulings, ledger, dispatch, report |
| Author | Fable (Opus fallback, announced) | **the two-page brief + previous chapter + SOUL/VOICE only** | the draft |
| Editor | gpt-5.6-sol via Codex CLI (ChatGPT plan; API billing refused by the script) | manuscript + brief + canon walls | verdict: DEFECTS track + PULL track |
| Verifier | Sonnet, clean context | manuscript + verdict + canon | confirms/rejects every finding; consolidates the repair packet |
| Cold Reader A | Sonnet, clean context, **manuscript only, chapters 1..N** | no canon, no cards | persona: thirteen-year-old reader — pull score, confusions, skim points, laughs |
| Cold Reader B | Sonnet, clean context, manuscript only | no canon | persona: adult genre reader — same fields, plus "what I expect next" |
| Fight Auditor | Sonnet, clean context | the combat chapter + Charter gates 9–16 + injury ledger | combat gates only; runs on set-piece chapters |
| Repair | Fable (prose/choreography/additions) or Sonnet (single clause) | manuscript + repair packet | applies verified findings; may ADD |
| Sweep | Sonnet | all chapters | book-level tic census and recasts |

Humor is not a seat. It is scored twice: the cold readers report beats that
landed; the editor's PULL track counts beats and applies the delete test.

## Chapter loop (nine phases)

1. **Packet.** Build and validate the chapter packet: card (with floors and
   cold/hot declaration), ledger entry N−1, canon rulings, name budget remaining.
2. **Brief.** Compile the **two-page author brief** from the packet: the card;
   where the last chapter left the board; the want line; the action-floor item or
   the declared gap; the humor expectation; five walls that matter for this
   chapter; the name budget; the tic ceilings. The brief replaces the fifteen-file
   load order. The walls the brief omits still bind — they are enforced by the
   editor and verifier, not memorized by the drafter.
3. **Draft.** One generation (two clean seats for chapters 1–3, blind pick by the
   cold readers). The author files manuscript + report with the pull self-check.
4. **Editor.** Cross-family, two tracks. STRUCTURAL on either track holds.
5. **Readers.** Both cold readers read chapter N with chapters 1..N−1 already in
   their context from prior calls (or a rolling summary they wrote themselves;
   never the canon). They file per-chapter reader reports.
6. **Fight audit.** On set-piece chapters only: Gates 9–16 with quoted evidence and
   the injury ledger.
7. **Verify.** The verifier tests every editor, reader, and fight finding against
   the manuscript and frozen evidence, and writes ONE repair packet, each item
   marked ADD / RECAST / CUT and SONNET / FABLE.
8. **Repair and recheck.** Repair verified findings only; preserve recorded
   strengths. Recheck by the editor; if a PULL repair added material, the cold
   readers re-read the changed span. Maximum three cycles; the same verified
   defect surviving three cycles = `BLOCKED`.
9. **Close and report.** Ledger entry N; loop state; **progress.json updated with
   every seat's figures for chapter N; dashboard re-rendered.** Chapter N+1 is not
   dispatched until the ledger entry and the progress record exist.

## Larger-scope gates

At each act: thread debt, plant/payoff inventory, relationship motion, progression
distribution, density, repeated-scaffold diagnostics, **the action schedule
delivered vs planned, the humor floor per chapter, and the pull profile** (any run
of three chapters under 3 from either reader = STRUCTURAL).

At book scope: ending promises, canon and arithmetic, name collisions, family and
content policy, full tic census with contextual adjudication, manuscript metadata,
listening proof, **the front-matter institutional map, the masked-name metric
across the book, the sentence-variance histogram, and the reader-pull profile.**
Diagnostics nominate passages; they do not automatically rewrite.

## Rewrite budget

- First draft: one generation (two for hook chapters, blind pick).
- Structural repair: only when a promised function is absent or broken — on
  either track.
- Continuity repair: only verified contradictions.
- Pull repair: verified reader findings; may add up to 8% of the chapter's target
  without a word-band waiver (Charter §10.1 principle 6).
- Voice revision: one book-level pass after structure locks.
- Line edit: one pass after voice locks.
- Listening repairs: localized.

No global rewrite because a newer model exists. A proposed re-authoring must beat
the locked passage in a blind reader comparison and preserve canon.

## The progress report

The orchestrator maintains `progress.json` in each book folder (schema:
`pen-names/fantasyau1.1/seats/progress.schema.json`). One record per chapter with
each seat's figures: author (word delta, band, humor beats claimed, action item,
variance), editor (verdict, defects by severity, pull findings by severity),
readers A and B (pull score, confusions, skims, laughs, would-continue), fight
(gates passed of 8, new injury, terrain beats), repair (cycles, adds/recasts/cuts),
close (timestamp). `progress.py` rolls the records up per book, per series
(`series.json` pointing at the book folders), and per universe arc, and renders
one HTML dashboard with a tab per level. The dashboard is published as an artifact
and republished at every chapter close. Nothing on it is hand-typed; every figure
comes from a seat's filed report.

## Completion and audio handoff

When all chapters and book-scope gates close, set `BOOK_LOCKED`, render the final
dashboard, and proceed to the narrator audition pack exactly as 1.0. The narrator
choice remains the final human gate.

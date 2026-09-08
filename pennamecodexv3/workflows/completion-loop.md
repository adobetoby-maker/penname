# Workflow — Bounded Book Completion Loop

## Goal

Run from approved story design to a locked manuscript and narrator audition pack
without repeatedly rewriting the whole book. The loop pauses for the owner only
when a real authority conflict survives bounded repair, or when the narrator must
be selected.

## Preconditions

Before scene drafting, freeze and supply: pen name, canon, arc and ending, current
state ledger, name registry, module policy, chapter architecture, and the book's
scene inventory. A missing authority artifact is a blocker, not creative latitude.

## Scene loop

1. Build and validate one scene packet.
2. Compile a fresh author prompt for the selected pen name.
3. Draft once and validate paths, report identity, actual word count, and metadata.
4. Compile a fresh cross-family editor prompt.
5. Verify every proposed finding against manuscript and frozen evidence.
6. Repair verified findings only; preserve recorded strengths.
7. Re-edit the repaired scene.
8. Close the scene when no verified blocker/high finding remains.

Maximum automatic repair cycles: three. If the same verified defect survives three
cycles, stop as `BLOCKED`; changing words forever is not progress.

The repair origin is recorded. A repaired scene returns to scene editing; a repaired
book-scope finding returns to the book audit. The state machine never silently moves
a large-scope repair into the wrong evaluator.

## Fantasy movement loop (default for `/fanauthr`)

Fantasy Author A normally groups the scene loop into a contiguous movement of
three to five chapters; four is the default. The detailed sequence lives in
`pen-names/fantasy-author-a/PIPELINE.md`.

1. Compile one movement packet from approved cards, the current ledger, the
   previous chapter, the next card after the batch, and the scheduled action/cold
   chapters.
2. Draft the chapters forward in one author session. Between chapters run only
   the light close: card function, canon, state, names, word band, reader standard,
   and ledger update. Do not line-edit between drafts.
3. Freeze the movement and send all of its chapters to the cross-family batch
   editor. The editor checks both chapter defects and the connections between
   chapters.
4. Run one rotating cold reader on an ordinary batch and both cold readers on the
   opening, act-ending, and final batches. Readers receive manuscript only.
5. Run a fight audit only for scheduled set pieces. Use an independent verifier
   only for high-impact, disputed, or structural findings.
6. Consolidate one repair list, repair in reading order, and target the recheck to
   prior findings and changed seams. Two repair cycles is normal; three is the
   hard ceiling.
7. Close the batch, update authority artifacts, and begin the next movement.

The single-scene loop remains the exception lane for a major canon ruling,
irreversible death, complex system reveal, or any chapter whose uncertainty
makes continued drafting unsafe.

## Larger-scope gates

At each chapter: light seam, promise, state delta, reader-standard, and
audio-readability check. This is a safety close, not a full editorial pass.

At each movement: full seam and continuity review, repeated information,
progression delivery, action spacing, humor distribution, dialogue distinction,
and reader pull.

At each act: thread debt, plant/payoff inventory, rival/relationship motion,
progression distribution, density, and repeated-scaffold diagnostics across the
continuous act.

At book scope: ending promises, canon and arithmetic, name collisions, family/content
policy, full tic census with contextual adjudication, manuscript metadata, and a
listening proof. Diagnostics nominate passages; they do not automatically rewrite.

Only located, verified defects create repair packets. A new preference does not
reopen a closed scene.

## Rewrite budget

- First draft: one generation per chapter, normally inside a three-to-five-chapter
  movement session.
- Structural repair: only when a promised scene function is absent or broken.
- Continuity repair: only verified contradictions.
- Movement repair: one consolidated pass after batch editing and cold reading.
- Voice revision: one book-level pass after structure locks.
- Line edit: one pass after voice locks.
- Listening repairs: localized, followed by regenerated audio.

No global rewrite occurs merely because a newer model exists. A proposed re-authoring
must beat the locked passage in a blind comparison and preserve canon before it may
replace anything.

## Completion and audio handoff

When all scenes and book-scope gates close, set `BOOK_LOCKED`. The production layer
then renders the same representative passages with candidate narrators, normalizes
them, and produces a blind audition pack with pronunciation notes. Advance to
`AWAITING_VOICE_SELECTION`. The owner selects the narrator; that event advances the
book to `COMPLETE` and starts full rendering from the locked manuscript.

The narrator choice is intentionally the final human gate. Text-generation models
may prepare excerpts, pronunciation notes, and anonymized candidate labels, but they
must not choose the production voice on the owner's behalf.

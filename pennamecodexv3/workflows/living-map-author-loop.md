# Monroe Jackson 1.2.0 — Living-map author loop

## Principle

The planning system remembers. The author discovers. The editor locates. The same
author repairs. The reader decides. Canon absorbs what survived.

This is a set of loops, not a contract ladder.

## New-book loop — Sonnet showrunner

1. Capture the idea's irreducible promise: who the reader follows, what changes,
   why it creates a novel rather than a premise, and what pleasure repeats.
2. Develop several `POSSIBLE` architectures. Ask only high-leverage questions that
   genuinely change the book.
3. Build the series map at three horizons: NOW, NEXT, and HORIZON.
4. Build the current book as connected movements with escalating problems,
   character choices, plants, payoffs, and an ending promise.
5. Schedule physical or problem-solving set pieces for story reasons. Select the
   smallest action stack that describes each one.
6. Challenge the architecture: sameness, passive protagonist, free victories,
   unsupported twists, stalled middle, generic opposition, premature crossover,
   or an ending that only promises the next book.
7. Reconcile the challenge. Present consequential alternatives to the owner and
   preserve unchosen options as `RETIRED` or `POSSIBLE`.
8. On approval, promote current-book decisions to `PLANNED` and compile Movement 1.

Sonnet is the operational showrunner. It organizes and maintains the architecture;
it is not presumed to be the strongest prose author.

## Movement loop — Fable or Opus Light author

1. Import any new PWA owner-edit events and rebuild the active owner examples.
2. The showrunner compiles one packet for three to five contiguous chapters.
3. The packet names the stable PWA book and series IDs plus entry pressure,
   escalation, turn, current state, chapter cards, plants/payoffs, reserved
   truths, freedom to invent, and action-stack assignments.
4. Compile Monroe Light with the approved owner voice, a small set of relevant
   owner comparison pairs, and only the assigned action layers.
5. The Light author drafts forward. Between chapters it performs only a state and
   canon close; it does not stop for full line editing.
6. A deterministic scan checks file integrity and the thirteen-year-old reader
   standard. It identifies locations and never writes prose.
7. Run the punctuation-integrity review (`scripts/punctuation_review.py`,
   codex backend) on every chapter in the movement. It proposes word-locked
   candidates only — no word added, removed, replaced, or reordered — for
   missing or wrong commas, semicolons, periods, and quotation marks that
   would make the prose hard to read silently or aloud. Validate each
   candidate (`scripts/promote_punctuation_reviews.py`, dry run first) before
   applying; skip anything that fails the word-lock check or lands on a
   file with uncommitted changes.
8. Freeze the movement. The continuity editor and a cold reader read it as one unit.
9. Run specialist review only where the movement contains that specialist subject.
10. Consolidate at most three high-leverage findings into a compact repair brief.
11. The original drafting model repairs once in reading order. Protected owner
    wording remains unchanged unless the owner explicitly unlocks it.
12. Recheck only the original findings and changed joins.
13. Update canon, state, the living maps, and the next movement packet.

## Owner-edit learning loop

1. The PWA exports immutable, versioned owner-edit events.
2. `scripts/owner_style.py ingest` validates and archives them idempotently.
3. Reverted, rejected, conflicted, mechanical-only, canon-only, and local-only
   changes are excluded from author-voice examples.
4. Active direct edits and accepted revision pairs become scoped evidence.
5. An owner may explicitly **Send to Monroe** an edited pair or an unchanged
   passage worth preserving; this positive example receives selection priority.
6. The owner-voice librarian periodically distills repeated preferences into a
   candidate profile; it never overwrites the approved profile.
7. The owner reviews and promotes the candidate deliberately.
8. The next movement prompt receives the approved profile and no more than the
   selected example limit.
9. Later edit density and repeated corrections show whether Monroe is learning.

## Five silent author exits

1. The promised event happened on the page.
2. Canon and carried state remain intact.
3. The viewpoint character wants, decides, attempts, or withstands something.
4. Pressure or relationship state changes by the ending.
5. The manuscript satisfies the clean thirteen-year-old reader standard.

## Book loop

1. Freeze the complete first edition.
2. Run an unprimed whole-book cold read.
3. Run structural and developmental review.
4. Convert findings into movement-sized repair briefs.
5. The original author repairs each affected movement.
6. Recheck continuity and movement joins.
7. Run a second whole-book cold read.
8. Run voice distinction, line edit, listening proof, and a whole-book
   punctuation-integrity pass (same word-locked tool as the movement loop, run
   once over the full manuscript to catch drift the per-movement pass missed)
   as separate passes.
9. Run Monroe Book Narrator 1.2.5 in rolling three-chapter units. Return any
   meaning-level one-pass comprehension failures to the original Writing Monroe
   seat; keep punctuation-only narration preparation word-locked.
10. Recheck accepted writing repairs in silent reading and aloud, then lock the
    edition and update series truth.

## Series and universe loops

After each book, update trajectories, relationship state, promise debt, antagonist
motion, repeated structures, side stories, and NEXT/HORIZON plans. Major changes
receive an architecture challenge.

After each series-level turn, update the shared cosmology, chronology, entities,
artifacts, knowledge boundaries, travel constraints, and crossover windows. A future
collision must change both stories and remain understandable to a reader arriving
from either series.

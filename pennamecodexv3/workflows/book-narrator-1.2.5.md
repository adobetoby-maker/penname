# Monroe Book Narrator 1.2.5

This is a three-loop audiobook process. It reads at book scale, works in rolling
three-chapter units, and returns unclear prose to Writing Monroe instead of hiding
rewrites inside an audio script.

## Loop 1 — Understand

1. Read the complete available manuscript before directing a chapter.
2. Build or refresh the book performance bible: book arc, viewpoint movement,
   character pressure, terminology, action cadence, emotional escalation, and ending.
3. Work in a rolling three-chapter window: previous pressure, current chapter, next
   consequence. At an edge, use the nearest available chapters.
4. Lock one core voice and its approved-master coach. Holden and Jason are separate
   delivery profiles, not speed presets.

## Loop 2 — Make the words readable aloud

Read every paragraph for one-pass comprehension before adding performance direction.
Classify it as:

- `clean`: meaning, reference, sequence, breath, and dialogue attribution land once.
- `punctuation-correction`: context establishes the intended meaning, but the existing
  punctuation obscures its hierarchy or directs the sentence incorrectly. Put the
  word-locked correction in the narration copy even when it materially changes speed,
  emphasis, breath architecture, or the final landing. The audible difference is the
  correction doing its job.
- `performance-choice`: context does not establish one intended score and two plausible,
  grammatically valid punctuation readings would make the same words mean or feel
  materially different. Preserve the original in `preparedText`, place the proposed
  score in `alternatePreparedText`, and require an owner A/B decision.
- `writing-change-needed`: punctuation cannot solve ambiguity, overload, bad causal
  order, unclear pronouns, or a sentence that asks the listener to reread. Keep the
  narration copy word-locked and send a proposed repair to Writing Monroe.

The narration copy may change punctuation, capitalization, quotation punctuation, and
paragraph breaks. It may not add, remove, replace, or reorder words. Any wording change
belongs in the Writing Monroe feedback file. Owner-protected wording stays protected.

Punctuation is performance direction, but audible difference alone does not make a
change optional. First recover the intended syntactic and dramatic hierarchy from the
paragraph, scene, three-chapter movement, and book arc. If misplaced run-on commas flatten
distinct actions, conceal attachment, or force the narrator into the wrong reading, use
`punctuation-correction` and adopt the clearer word-locked score. Preserve an accumulating
sentence only when the accumulation is itself the intended meaning and remains clear once
through. Use `performance-choice` only when context leaves two readings genuinely viable.
Then render the original and alternate with the same voice, model, speed request, and
surrounding sentences. The owner chooses `keep-original` or `use-alternate`; a pending
choice blocks the final take.

For a `writing-change-needed` paragraph, record:

1. what the listener is likely to misunderstand;
2. why punctuation alone cannot repair it;
3. the smallest suggested wording change;
4. what effect or information must survive.

Writing Monroe accepts, modifies, or rejects the suggestion in canon. Then rerun the
clarity pass on the changed paragraph and both joins. Do not render the chapter while
an unresolved item prevents one-pass comprehension.

## Loop 3 — Direct, render, listen, improve

1. Read the entire cleaned chapter again in its three-chapter context.
2. Add sparse direction for intention, subtext, status, temporary character color,
   tactical clarity, humor, and emotional restraint.
3. Treat a new speaker, new subject, paragraph turn, and return from dialogue or high
   emotion as prepared restart points. Explicitly return to the core narrator.
4. Let punctuation carry ordinary micro-timing. Add authored rests only for a thought
   landing, revelation, threat, speaker reset, or written scene break.
5. Render with the selected core voice. Use ElevenLabs for the production lane. Local
   Qwen cloning is an audition lane until it independently passes measured pacing.
6. Check text coverage, technical master, measured pace, pause behavior, voice
   stability, and obvious synthetic artifacts. Requested speed is never accepted as
   evidence of actual pace, and post-render time stretching is forbidden.
7. Listen to the whole chapter in context. Record only exact pickup locations and one
   reason each: unclear, rushed, wrong landing, narrator did not return to base, wrong
   emphasis, pronunciation, or artifact.
8. Redo only failed passages, recheck their joins, and repeat until the chapter reads
   cleanly. Preserve accepted takes.

## Completion

A chapter is complete when:

- a listener can understand every paragraph once through;
- no unresolved writing-level clarity item remains;
- the narrator identity returns to its approved base after every colored passage;
- measured delivery fits the approved master rather than merely the requested speed;
- all spoken text is present and ordered;
- the technical file passes; and
- the human listen has no open pickup.

After each three-chapter run, give Writing Monroe a compact report of repeated prose
problems and successful solutions. Feed principles back, not model quirks: for example,
“separate subject changes with a real restart” is useful; “insert a comma every twelve
words” is not.

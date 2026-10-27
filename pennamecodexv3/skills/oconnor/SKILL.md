---
name: oconnor
description: Plan and orchestrate the O'Connor 1.3.1 progression-adventure seat (Monroe 1.3.0 foundation), using Iron Prince structural research, Opus or Fable authorship, open-range movements and focused editorial loops.
---

# O'Connor 1.3.1 — Monroe Jackson author seat

Canonical package: `/Users/drive/penname/pennamecodexv3`.
Read `pen-names/oconnor/PIPELINE.md`, `VOICE.md` and `FORMULA.md` in that package.
Read `/Users/drive/penname/research/ironprince-craft-formula.md` for its exact
numerical targets. The compiler embeds craft sections 2–6 and 8–9 verbatim in both
planning and drafting prompts. These are the owner's selected design targets,
not optional research notes; do not soften them into generic craft advice.
Codex maintains/orchestrates; Opus or Fable writes and repairs. Opus 5.5 is the default author;
Fable (or another model) runs only when the owner names it. Never substitute the
current Codex model silently. The public
byline is Monroe Jackson; O'Connor is an internal seat name.

Use six or more contiguous chapters per creative run (default 8, no upper cap). One compact
movement brief replaces compulsory chapter cards. No chapter-by-chapter editorial
gates. Output limits can require continuation of the same run; they must not cause
shortened chapters or premature claims of completion.

The owner names the characters. Use role placeholders during planning and resolve
the needed names before prose drafting. A request to build/activate the seat is
not permission to start a novel. Preserve canon and exact owner-protected text.

Compile locally with `/Users/drive/penname/harness/oconnor.sh`:

- `plan --root PROJECT --author opus --idea 'idea'` (or `--idea-file FILE`).
- `formula --output FILE` exports the standalone numerical formula prompt.
- `movement --root BOOK --author fable --packet packets/MOVEMENT-001.md --count 8`
  with `--start N`, repeated `--context FILE`, optional `--previous FILE`, and
  optional scene-specific `--action 'scene=stack'`.
- `review --root BOOK --author fable --chapter manuscript/chapter-01.md`, repeating
  `--chapter` for the complete movement in reading order. Add `--context FILE`
  for editorial canon evidence; omit for manuscript-only cold reading.
  Use `--formula-check` for editorial target/observed comparisons; omit it for a
  blind cold read. Read `pen-names/oconnor/FORMULA_REVIEW.md` for measurement rules.

The compiler prints a prompt; `--output FILE` saves without overwrite. It makes
no model call. For authorized drafting, verify the locally installed author CLI's
available model and subscription login, then supply the selected model and saved
prompt. Do not switch to a paid API or alternate author on failure. Record the
actual reported model separately from the seat version and requested alias.
No new model invocation is authorized merely to validate this skill.

After the completed movement: continuity/story pass, reader/clarity pass, one
consolidated same-author repair, targeted recheck. Read `REVIEW.md` for the rubric.
Label self-review vs fresh-context simulated cold read honestly. Use approved owner
voice/examples; only accepted owner evidence updates the trainer.

Read `PROVENANCE.md` when discussing research validity. Do not claim a full-book
read or verified percentages from partial inspection. The transcript and quoted
source-character study are private research, not drafting inputs. Read
`references/combined-path-adapter.md` only for the owner's selected 600-year Kindling
proposal; it is not a default premise for new books.

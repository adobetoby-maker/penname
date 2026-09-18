# ADR 0003 — Named-influence pen names are permitted

- Status: Accepted for v3.1
- Date: 2026-09-18

## Context

`craft/CORE.md`'s reader-trust invariant §6 originally read "Anti-pastiche:
learn mechanisms, never protected expression; do not imitate or name a
living author's distinctive wording, rhythm, characters, or recognizable
scene construction." It bundled two different things into one rule: (a)
never reproduce an author's protected expression, and (b) never even name
the author being learned from. Rule (a) is a real and correct constraint —
character names, place names, invented terminology, and verbatim or
near-verbatim text are protected expression and must never appear in a
docked book. Rule (b) is not: prose style, word choice, sentence rhythm, and
structural/architectural technique are not protected expression under
copyright, and naming a comp author for clarity ("this pen name writes in
the lineage of X") is ordinary, legal creative practice — publishers and
authors do it routinely ("for fans of X").

Keeping rule (b) alongside rule (a) had a real cost: a pen name whose whole
purpose is single-lineage fidelity to one named author's craft (owner
request, 2026-09-18) was writing its own runtime files under a hedge that
warned itself away from precision it was explicitly built to have —
producing vaguer, less committed word-choice and register guidance than the
owner asked for.

## Decision

Split the invariant. `CORE.md` §6 now states only rule (a): protected
expression (names, places, invented terms, verbatim/near-verbatim text,
plot-as-expressed) may never be reproduced, full stop, for every pen name.
Naming an influence author is explicitly permitted and left to each pen
name's own `PROVENANCE.md`/`VOICE.md`/`SOUL.md` — a pen name may name its
influence openly (Monroe does, as of v1.4) or keep the name provenance-only
(Fantasy Author A and Science Fiction Author B continue to, unchanged, by
their own existing choice, not because the rule forces it).

Research briefs built from secondary sources only (reviews, craft essays,
wikis — never the source text itself) were already incapable of producing
protected expression; they document mechanism and reviewer-characterized
register, not sentences. Naming the author those mechanisms were researched
from adds clarity without adding risk.

## Consequences

- `CORE.md` §6 is renamed "No protected expression" and no longer mentions
  withholding an author's name.
- Monroe (`pen-names/monroe/`, formerly the placeholder `fantasy-author-c`)
  names Bryce O'Connor and Luke Chmilenko directly in `VOICE.md`,
  `SOUL.md`, and `PROVENANCE.md`, and the compiled author/editor prompt
  carries that name. This is intentional, not a leak to fix.
- Every pen name still owes the same hard floor: no borrowed names, places,
  invented terms, or verbatim/near-verbatim text, checked the same way it
  always was (book-level name registry, editor gates, human review).
- Fantasy Author A and Science Fiction Author B are unaffected unless their
  own owners choose to name their sources too; nothing in this ADR requires
  it.

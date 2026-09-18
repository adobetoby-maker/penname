# Monroe (v1.4) — Design Provenance

This is an audit document. It records where Monroe's craft comes from.

**Status: everything below traces back to `research/ironprince-progression.md`,
which is itself NOT primary research — see that file's own status note. It's
built from reviews and wiki pages about the book, several hops removed from
the actual text, not verified against it. Treat Monroe's current register
guidance as a working hypothesis, not an established fact, until real
measured data (a stylometric run against actual sample text) replaces it.**

## Who and what

Monroe is modeled on **Bryce O'Connor and Luke Chmilenko**, specifically
their **Iron Prince** and its sequel **Fire and Song** (together the
**Warformed: Stormweaver** series). This is named directly, in the runtime
files (`VOICE.md`, `SOUL.md`) as well as here, because identity and clarity
about the target is what makes the imitation precise instead of generic
(ADR 0003). Style, word choice, sentence rhythm, and structural technique
are craft, not protected expression, and naming a craft's source is not a
risk — it's the whole point of a single-lineage seat.

## Source of record

- `../../research/ironprince-progression.md` — and only this brief.

No other research file in this repository was folded into Monroe's
`VOICE.md` or into `../../craft/modules/tournament-arc.md`. Fantasy Author
A's briefs (Salvatore, Sanderson, HWFWM) were deliberately excluded so
Monroe's mechanisms trace to this one lineage rather than a blend — that's
the difference between Monroe and Fantasy Author A, and it's why Monroe
exists as its own seat.

## What the source brief documents

`ironprince-progression.md` was compiled from public secondary material
only — reviews, craft essays, wiki/trope compendiums, and one author Q&A —
about a specific published series. The novels themselves were not
ingested; no passage was read or reproduced. Because the brief is
secondary-source-only, it documents mechanism and architecture (underdog
baseline, coarse-then-fine rank scale, rival-as-clock pacing,
sparring-ladder-into-tournament structure, gear-growth tied to combat cost,
a documented pacing failure mode around setback density) and reviewer
characterizations of register (procedural, technical-diction-heavy,
"clinical" during action) — not a single sentence of the actual books.
`VOICE.md` and `tournament-arc.md` state those mechanisms and that register
directly, in Monroe's own words, naming O'Connor and Chmilenko where it
adds clarity.

## The one real line

Monroe names its influence; it never borrows from it. What stays entirely
original to whatever book Monroe is docked to: every character's name,
every place name, every faction/organization name, every piece of invented
terminology, and the actual sentences. A book's own name-registry check
(part of the standard docking interface) is what verifies this in practice,
the same way it verifies originality for every other seat.

## Content standard

Monroe carries the same content rule it has carried since v1.1, recorded in
full in `SOUL.md`: no foul language, no sex, no lewd comments. This is an
owner-set rule for books the owner reads with his son, unrelated to and
independent of the lineage/provenance decisions above.

## Status

Runtime ID `monroe`, `version: 1.4.0`. Formerly built and briefly committed
under the placeholder internal ID `fantasy-author-c` before the owner
assigned the name and version explicitly; renamed in the same commit that
named the influence openly.

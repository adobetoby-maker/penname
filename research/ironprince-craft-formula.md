# Iron Prince Craft Formula — Mechanism, Not Expression

Purpose: a prose-generation target for an author agent (Opus or otherwise) writing an
**original story, original world, original characters** that reads in the structural
tradition of Bryce O'Connor & Luke Chmilenko's *Iron Prince* (Warformed: Stormweaver,
Book 1), without reusing any of that book's protected expression.

Derived from a direct statistical pass over a Whisper transcript of the owner's own
purchased audiobook (61 files, ~326,000 words, mlx-community/whisper-large-v3-turbo-asr-fp16).
Full methodology and raw numbers: `research/ironprince-craft-stats.json`. The transcript
itself lives at `research/iron-prince-book1-transcript.md` — **local reference only, never
to be copied into generated prose, never pushed to a shared repo.**

---

## 1. Why this is a legitimate craft extraction, not a copyright problem

**The governing rule is 17 U.S.C. §102(b):** copyright "in no case" extends to "any idea,
procedure, process, system, method of operation, concept, principle, or discovery." Every
number in this document describes a *pattern* — a distribution, a rate, a placement
tendency — not a string of his words.

**Nichols v. Universal Pictures** (Learned Hand, 2d Cir. 1930) is the operative test: a
work can be described at any level of abstraction from bare theme down to verbatim text,
and protection attaches only at the concrete end. "Underdog with a device that grows
through combat losses, at a competitive academy" is exactly the kind of abstract pattern
Hand's opinion places outside protection — same tier as "star-crossed lovers whose families
feud." The specific words O'Connor used to render any one scene are protected; the
narrative-engineering pattern behind a hundred scenes is not, and never was his to own.

**Scènes à faire** — tournament brackets, academy hierarchies, training-montage beats,
mentor-pep-talk scenes — are standard furniture of progression fantasy. Unprotectable
because they are not original to any one author; using them is not "borrowing from Iron
Prince," it's writing in a genre.

**Style is one of the most settled unprotected categories in the caselaw.** Sentence-length
distribution, paragraph rhythm, dialogue-tag frequency, where a chapter chooses to land its
progression beat — these are *how* he writes, not *what* he wrote. No court has ever let an
author own a cadence.

**What this document is careful never to hand over:** his invented terminology as *his*
naming choices (CAD, Growth/Offense/Defense as exact labels, "Galens Institute," any
character or place name from this book), the specific sequence of his actual scenes, or
any sentence-level phrasing. Section 7 makes this an explicit checklist, not an assumption.

**One adjacent, non-copyright flag:** if this project is ever *marketed* as "feels just like
Iron Prince," that's a Lanham Act false-designation-of-origin question — a labeling risk,
separate from whether the craft extraction itself is sound. It is sound. Don't advertise
affiliation that doesn't exist.

---

## 2. Sentence rhythm

| Metric | Target |
|---|---|
| Mean sentence length | 14.6 words |
| Median sentence length | 11 words |
| Spread (population stdev) | ~26 words — wide, meaning short declaratives sit right next to long compound-complex sentences, not clustered near the mean |
| Share of very short sentences (≤5 words) | 27.7% |
| Share of very long sentences (≥40 words) | 3.3% |

**Read:** roughly 1 sentence in 4 is a hard, short beat (often a single clause landing a
punch after a longer setup) — this is the "short sentence for impact" technique, not
uniform mid-length prose. Target this ratio, not just the mean; a manuscript that hits mean
14.6 but has no short-sentence spikes will not read the same.

## 3. Paragraph and scene rhythm (ASR-inferred proxy)

Whisper transcripts carry no typographic paragraph marks — this section is inferred from
pause gaps between narrated speech segments, not a count of the print manuscript's actual
paragraph breaks. Treat as directional, not exact.

| Metric | Target |
|---|---|
| Inferred paragraph length (pause ≥0.6s) | median 18 words, mean 26.8 words — short, frequent beats |
| Inferred scene/section length (pause ≥1.6s) | mean ~950 words between scene-level breaks, ~8.7 scene breaks per 10k words |

**Read:** short paragraphs are the default texture, with scenes running roughly 900–1000
words before a beat change (POV settle, location change, or time-skip). Avoid long
unbroken expository blocks; break early and often.

## 4. Progression-mechanic ("change frequency") callout rate

| Metric | Target |
|---|---|
| Progression/stat-vocabulary density | ~58 hits per 10k words (rank, growth-analog, spec, level-up, stat-block language) |
| Placement | front-loaded — the opening third of the book carries roughly 1.7x the progression-callout density of the middle and closing thirds (900 vs. 471 vs. 514 hits, by third) |

**Read:** the system gets *established* early and hard, then recedes into the background
as character and plot take over — it does not stay evenly dense through the whole book.
Build your own progression system's vocabulary (do not reuse his axis names — see §7), but
match this front-loaded shape: teach the mechanic aggressively in the first third, then let
it surface only at genuine turning points afterward.

## 5. Character-development beat cadence

Methodology: named-character mention within ~120 characters of a reflection/interiority
marker ("realized," "decided," "for the first time," "swore," "no longer," etc.) — a
heuristic count, not a scene-by-scene read.

| Metric | Target |
|---|---|
| Protagonist development-moment rate | 4.5 per 10k words |
| Protagonist distribution across thirds | roughly even (41 / 56 / 50 — a slight middle-third bump, not backloaded) |
| Supporting-cast development-moment rate | an order of magnitude lower per character (0.1–0.7 per 10k words each), spread across 8–10 named characters rather than concentrated in one deuteragonist |

**Read:** growth beats for the lead land steadily throughout, not saved up for a finale —
and the supporting cast gets *many* small beats each rather than one character getting a
big secondary arc. If your story gives one best-friend character 80% of the secondary
development budget, that's a different shape than this book's.

## 6. POV structure

| Metric | Target |
|---|---|
| Protagonist POV share | ~87% of chapter-word-volume (combining his given-name and surname references) |
| Secondary-character POV/focus share | ~13%, spread across 4–5 named characters at 2.5–3.7% each — brief cutaways, not sustained alternating-POV chapters |

**Read:** this is single-POV-dominant with occasional short cutaway scenes to a handful of
other named characters, not a true multi-POV structure. If you want to signal "feels like
Iron Prince," don't build alternating-chapter dual POV — keep the lead's POV overwhelming
and let other characters get glimpses, not chapters.

## 7. What to build yourself — do not reuse

This is the wall between mechanism (above, safe to target) and expression (below, never
copy). Invent your own equivalents for every line:

- **His device's name and axis labels** — do not use "CAD," "Growth," "Offense," "Defense"
  as your system's exact terms. A multi-axis, letter-graded progression system is an
  unprotectable *method* (§102(b) again — "system" is explicitly excluded); his specific
  naming of it is his expression. Name your own axes.
- **Character names** — protagonist, cast, mentors, antagonists: all original. Do not use
  near-homophones of his names as a wink (no "Raden Word," no "Vivi").
- **Place and institution names** — invent your own academy, city, system names.
- **Scene sequence and content** — the *pattern* "open on the protagonist demonstrably
  worst-in-room in a public setting" is fair game; the specific scene he wrote to do that
  is not. Write your own scene from scratch to hit the same structural beat.
- **Any sentence-level phrasing** — nothing lifted, nothing paraphrased closely enough that
  a side-by-side read would show matching word order. Style-match at the level of *rhythm*
  (§2–3), never at the level of *wording*.

## 8. Supporting craft signals (secondary, use to taste)

- **Filler-word discipline:** "that" runs hot (92.1 per 10k words) — a known, common genre
  tic, not a target to imitate; if anything, tighten below this. Other fillers ("just,"
  "almost," "felt," "seemed") sit in the 5–25-per-10k band — moderate, not aggressively
  self-edited, not sloppy either.
- **Adverb density:** ~161 -ly adverbs per 10k words — fairly high; this is a book that
  lets adverbs carry tone rather than insisting on pure show-don't-tell. Not a craft flaw
  to correct, a genre-register signal to optionally match.
- **Dialogue-tag (reporting-verb) density:** ~41 per 10k words — moderate dialogue presence,
  consistent with an action/interiority-forward book rather than a dialogue-driven one.
- **Combat-vocabulary density:** ~22 per 10k words (strike/block/dodge/blade/impact/etc.) —
  present throughout, not just in set-piece fight chapters.
- **Readability:** Flesch Reading Ease 72.3, Flesch-Kincaid grade 6.8 — accessible YA/adult
  crossover register, short-to-medium sentence construction, low jargon-density outside the
  progression-vocabulary spikes.
- **Repetition discipline:** common connective 3-grams ("out of the," "one of the," "for a
  moment") sit at 2–4 per 10k words — normal English-prose background rate, not a
  distinctive tic to replicate. Don't chase these; they're noise, not signature.

---

## 9. One-paragraph brief for the drafting agent

> Write single-POV-dominant (~85–90% lead-character screen time), short-paragraph,
> pause-heavy prose (median paragraph ~18 words, scenes breaking roughly every 900–1000
> words). Mix short punch sentences (~28% of all sentences ≤5 words) against longer
> compound-complex ones (mean 14.6 words, wide spread) rather than settling into uniform
> mid-length sentences. Establish your progression system hard and often in the first
> third of the book, then let it recede to occasional high-stakes surfacing afterward. Land
> a protagonist growth/realization beat roughly every 2,200 words, spread evenly across the
> book rather than saved for the climax, and give 8–10 supporting characters small
> development beats each rather than concentrating growth in one deuteragonist. Moderate
> dialogue-tag and adverb use; accessible ~7th-grade reading level; combat vocabulary
> present in the background throughout, not confined to fight scenes. Every name, every
> system-label, every scene: yours, invented, original.

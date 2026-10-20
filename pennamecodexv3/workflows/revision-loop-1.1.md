# Workflow — Revision Loop, 1.1 (fantasyau1.1)

## Goal

Take a book that already exists — locked under 1.0, or any finished draft — and
improve it against the Pull Law without rewriting it blind. The revision loop is
the forward loop run in reverse order: **read first, diagnose second, rewrite only
what the readers and the floors indict, re-read to prove the change.** It
produces a new edition of the book; the previous edition stays in git as a tag.

## When it runs

- A 1.0 book being brought under 1.1 (Good Bones 1–2, Fractured Path 1–8, Boundary 1).
- A book in progress whose early chapters were written before the floors existed
  (the sci-fi: chapters drafted before the revision architecture exists get the
  whole-book read as soon as the draft reaches the end of an act).
- Any book whose dashboard shows three consecutive chapters under 3 from either
  reader.

## Phases

### R1 — Intake
Dock the book (skill Step 2). `progress.py init` and `update` over every chapter so
the dashboard carries the existing seat figures. Tag the current manuscript
`edition-<n>` in git. Write `institutional-map.md` if missing (Gate 37).

### R2 — Whole-book cold read
Both personas read the entire book in order, in batches of five chapters per call,
carrying their own rolling notes (`reader-notes/A-notes.md`, `B-notes.md`) and
filing one report per chapter (`reader-reports/chNN-reader-A.md` / `-B.md`).
Rules: manuscript only; a batch never starts until the previous batch's notes are
on disk; the same persona prompt for every batch. `progress.py update` after each
batch; the dashboard's reader sparklines are the **pull profile**.

Optional in R2: the fight auditor over every existing set piece; the sweep's tic
census; `variance.py` over every chapter. All of it lands in `progress.json`.

### R3 — Diagnosis and the revision architecture
The lead reads the pull profile against the floors (Charter §10; the benchmark
framework) and writes `REVISION_ARCHITECTURE.md`: one **revision card** per
chapter (`seats/revision-card.template.md`) with a disposition —

| Disposition | Means | Typical trigger |
|---|---|---|
| KEEP | no change; protected | both readers ≥4, no floor breach |
| TIGHTEN | line pass only; cadence, names, a hook line | located monotony; substantive voices merge; unnamed recurrers |
| REPAIR | bounded additions/recasts inside the chapter: beats, a plain statement, a want line, a Mark micro-use | located confusions or skims; rolling humor span below 3 |
| RESTRUCTURE | merge, split, reorder, or move material between chapters | a run of low chapters; a floor that no single chapter can fix (set-piece spacing) |
| INSERT | a new set piece or scene the architecture never scheduled | set pieces >4 apart; power invisible for >6 chapters |
| CUT | the chapter's function is absorbed elsewhere | sustained low-score trend plus located reader evidence, and the promise it carried is paid by a neighbor |

Above the cards, **long-arc moves**: the want line placed by chapter 3; the
action schedule redrawn to target 7–8 with no gap over four; the climax as a 3–4 chapter
sequence; rolling two-chapter humor cadence; the institutional map's on-page statement;
the name budget spent on the recurring unnamed. Every long-arc move names the
chapters it touches and the canon it must not touch (the Book 3 reserves, locked
verbatim lines, the buried plant).

Canon changes forced by revision are **new ledger entries and new Bible rulings**
(Charter §7.3 — corrections are entries, never edits); the ledger's prior entries
are not rewritten.

### R4 — Execute, in reading order
Group adjacent non-KEEP chapters into movements of three to five and run the
forward movement loop with a **revision brief** (`seats/revision-brief.template.md`)
for each chapter: existing prose, revision card, located reader findings, floors,
and walls. The author repairs forward in one session; it does not draft from
nothing unless the disposition is INSERT. Batch editor, selective verifier, fight
audit where relevant, repair, and targeted recheck run as forward. RESTRUCTURE and
INSERT chapters get canon rulings before dispatch (rule 9) and ledger entries after
(rule 8).

### R5 — Re-read and prove
After each act's revisions close, both personas re-read the revised span (and
everything after a RESTRUCTURE, since the reader's memory changed). The dashboard
shows **edition n vs n+1** per chapter. Scores are trend signals; located new
confusion, skimming, or lost causal connection—not a scalar alone—triggers revert
or re-repair.

### R6 — Book gates and the new edition
The forward loop's book-scope gates, then `BOOK_LOCKED` as `edition-<n+1>`. The
narrator audition re-runs only for chapters whose text changed.

## Budget

- R2 is cheap (Sonnet readers) and always runs in full.
- R4 spends Fable only on REPAIR/RESTRUCTURE/INSERT chapters; TIGHTEN is Sonnet.
- Two repair cycles per movement is normal and three is the hard ceiling. A
  movement with a surviving located defect or a three-chapter low-score trend is
  reported to the owner with the readers' words, not rewritten a fourth time.

## The dashboard in revision

`progress.json` gains an `editions` array per chapter; `progress.py update --edition n`
files the current seat figures under that edition and `render` shows the delta
columns (reader pull, defects, humor beats, words) between the last two editions.

# Penname Harness — Monroe Jackson 1.2.0

The default system is now the living-map author loop:

- Sonnet (`/monroeplan`) develops and maintains the series, book, character,
  universe, and movement maps.
- Fable or announced Opus fallback (`/monroelight`) writes three to five connected
  chapters from one compact packet.
- Action scenes load only the tested layers selected for that scene.
- A continuity editor and cold reader diagnose the complete movement.
- The original drafting model performs one bounded repair before the maps advance.

Start an interactive Sonnet showrunner session with the existing `books` shell
command, optionally followed by the idea in quotes. The older `/fanauthr` and
`/scifiauthor` 1.1.1 seats remain available for controlled comparisons and existing
book continuity.

The 1.2.0 path uses Markdown living maps and loops. It does not require the legacy
JSON scene-contract state machine described below.

## 1.2.0 prompt compilers

Compile a Sonnet showrunner prompt:

```bash
python3 -B pennamecodexv3/scripts/build_showrunner_prompt.py \
  --genre fantasy --idea "your book idea"
```

Compile an approved Light-author movement:

```bash
python3 -B pennamecodexv3/scripts/build_movement_prompt.py \
  --genre fantasy --root /path/to/book --packet packets/MOVEMENT-001.md \
  --action "chapter 2=learning-deception"
```

Available action stacks are documented in
[`craft/action-layers/STACKS.md`](craft/action-layers/STACKS.md).

## Monroe Book Narrator 1.2.5

The narrator seat reads the complete book arc, then prepares and produces rolling
three-chapter units. It locks Holden or Jason to an approved master, performs a
word-locked punctuation and one-pass comprehension review, directs sparse delivery,
renders, listens, and loops exact pickups. Meaning-level prose problems go back to
Writing Monroe instead of being hidden in an audio-only script.

In Codex, invoke `$book-narrator`. In Claude, invoke `/book-narrator`. From a shell:

```bash
booknarrator holden /path/to/book 1-3
booknarrator jason /path/to/book 4-6 --audience adult
```

The run keeps the retake-ready narration copy, clarity findings, Writing Monroe
feedback, performance direction, audio, and listening notes together under the book's
`narration/monroe-1.2.5/` folder. See
[`workflows/book-narrator-1.2.5.md`](workflows/book-narrator-1.2.5.md).

## Owner-edit trainer

Monroe 1.2.0 can learn from exact owner revisions exported by the Boundary
Universe PWA. The PWA supplies immutable evidence; the harness decides which
events are active, separates voice choices from canon and mechanical fixes, and
compiles only the approved owner profile plus a small relevant example set.

On the author's Mac, automatic intake uses the PWA's immutable GitHub event
mirror and does not need the publisher-desk password:

```bash
harness/monroe-trainer.sh sync
harness/install-monroe-watch.sh
```

The installed watcher checks once an hour. New direct edits become eligible
examples for the next matching movement prompt; revision requests enter the
pending queue. It never publishes books or promotes a distilled voice profile.

Validate and ingest a PWA JSON or JSONL export:

```bash
python3 -B pennamecodexv3/scripts/owner_style.py ingest /path/to/owner-edits.jsonl
python3 -B pennamecodexv3/scripts/owner_style.py status
```

The command is idempotent by event ID. A repeated ID with changed content is
rejected rather than silently rewriting history. Reverted, rejected, conflicted,
mechanical-only, canon-only, and local-only edits do not enter author prompts.

Compile a periodic profile-distillation prompt:

```bash
python3 -B pennamecodexv3/scripts/owner_style.py distill-prompt \
  --output pennamecodexv3/owner-style/candidates/distill.prompt.md
```

The librarian returns a candidate. Review it before replacing
[`owner-style/OWNER_VOICE.md`](owner-style/OWNER_VOICE.md); no script promotes a
candidate automatically.

Movement packets should carry `PWA book ID` and `Series ID`. The movement compiler
then selects shared, genre, series, book, and character examples safely. Explicit
CLI values are also supported:

```bash
python3 -B pennamecodexv3/scripts/build_movement_prompt.py \
  --genre fantasy --root /path/to/book --packet packets/MOVEMENT-002.md \
  --book-id kindling-book-01 --series-id kindling \
  --action "chapter 8=learning"
```

Use `--without-owner-style` only for a deliberate control run.

## Legacy 1.1.1 compatibility

Provider-neutral, multi-pen-name author harness for audio-first speculative fiction.

The harness separates the creative author from the production machine:

- `craft/CORE.md` protects universal reader trust.
- `craft/VOICE.md` defines shared prose and audio-readability behavior.
- `pen-names/` supplies exactly one versioned genre-author identity per run.
- `craft/modules/` contains optional genre-specific guidance and editor gates.
- `agents/` defines roles without naming a provider or model.
- `contracts/` defines interoperable JSON artifacts.
- `scripts/build_prompt.py` compiles the same frozen prompt regardless of which
  provider orchestrates the run.
- `scripts/advance_loop.py` advances a bounded, auditable completion loop.

Claude may author while Codex edits, or Codex may orchestrate Claude and then
occupy the editor seat. Nothing in the core changes when control changes hands.

## Design boundary

```text
orchestrator (Claude or Codex)
        |
        +-- selects one pen name and validates one scene packet
        +-- compiles one role prompt
        +-- records provider/model/hash metadata
        |
        +--> author seat (recommended: Fable)
        |       +-- manuscript
        |       +-- author report
        |
        +--> editor seat (recommended: different model family)
        |       +-- gate results
        |       +-- proposed findings
        |       +-- strengths and taste concerns
        |
        +--> verifier seat
                +-- verified or rejected findings
                +-- evidence-bound repair authorization
```

Provider adapters are intentionally outside the trusted core. A provider may
change command syntax, authentication, model aliases, or tool names without
changing the author.

## Included pen names

| Runtime ID | Genre promise | Default modules |
|---|---|---|
| `fantasy-author-a` | **Monroe Jackson — Fantasy.** Progression fantasy/LitRPG: legible growth, tactical action, human cost, found family | `progression` |
| `science-fiction-author-b` | **Monroe Jackson — Science Fiction.** Character-driven problem-solving SF: rigorous speculation, relationship pressure, moral choice | `hard-science`, `moral-choice` |

These are stable internal compatibility IDs. The public pen name and canonical
authorship answers are defined in [`pen-names/MONROE_JACKSON.md`](pen-names/MONROE_JACKSON.md).
Each profile has a runtime `VOICE.md` and a separate `PROVENANCE.md`. Research names and links remain
in provenance and are never compiled into creative prompts. The goal is a coherent
craft system, not imitation of any living author's prose.

Existing books enter the catalogue through the named
[`Book Review and New Edition`](workflows/book-review-and-new-edition.md) loop.
It reads before editing, revises in connected movements, and ends with a locked,
recoverable edition rather than an open-ended rewrite.

## Quick start

All scripts use the Python standard library.

Validate the example packet:

```bash
python3 -B pennamecodexv3/scripts/validate.py \
  pennamecodexv3/contracts/scene-packet.schema.json \
  pennamecodexv3/templates/scene-packet.example.json
```

Compile the author prompt:

```bash
python3 -B pennamecodexv3/scripts/build_prompt.py author \
  --packet pennamecodexv3/templates/scene-packet.example.json \
  --root . > author.prompt.md
```

Give that exact prompt to the author seat. The selected `pen_name` controls the
voice layer and permitted modules. The seat needs file access to the docked book
root so it can write the two paths declared by `output`.

After the author has written the draft and report, compile the editor prompt:

```bash
python3 -B pennamecodexv3/scripts/build_prompt.py editor \
  --packet path/to/scene-packet.json \
  --root path/to/book > editor.prompt.md
```

The compiler refuses missing required context, paths outside the book root,
invalid packets, omitted default modules, modules owned by another pen name,
missing editor drafts, inaccurate reported word counts, and context bundles larger
than 2 MB.
This encourages deliberately compiled scene context rather than dumping an
entire series into every run.

## Scene-packet principle

The packet is a contract, not an outline-shaped prompt. It defines:

- frozen story revisions
- viewpoint and knowledge boundary
- emotional and causal scene shape
- plants, payoffs, and prohibited outcomes
- allowed, approval-required, and forbidden invention
- only the context files needed for this scene
- separate manuscript and report destinations

The author sees positive voice guidance and the author half of selected modules.
The editor sees the complete selected modules and their gates.

## Finding lifecycle

```text
PROPOSED -> VERIFIED | REJECTED -> REPAIRED -> RECHECKED -> CLOSED
```

The editor does not rewrite. The verifier does not expand findings. The author
chooses a repair that satisfies verified evidence. A human may approve or
occupy any step.

## Bounded completion

The state machine in `scripts/advance_loop.py` moves a book through validated
packets, authoring, editing, independent verification, localized repair, scope
audit, book lock, and narrator selection. The default repair ceiling is three.
The same verified defect surviving three cycles becomes `BLOCKED`; it does not
trigger an indefinite rewrite.

After all scenes and book-scope checks pass, the production adapter prepares a
blind narrator audition pack and advances the loop to
`AWAITING_VOICE_SELECTION`. The owner chooses the narrator, which advances the
book to `COMPLETE`. See [the completion workflow](workflows/completion-loop.md).

## Running in either direction

- [Codex orchestrates, Claude authors](workflows/codex-orchestrates.md)
- [Claude orchestrates, Codex edits](workflows/claude-orchestrates.md)

Both workflows compile identical role prompts. Compare prompt hashes in run
records to prove that an orchestration change did not alter the creative
contract.

`examples/minimal-book/` is a fully docked fixture with frozen canon, arc,
state, packet, draft, and author report. It allows both the author and editor
prompt paths to run immediately after cloning.

## Runtime boundary

- Provider API calls and authentication
- Canon retrieval or vector search
- State-ledger mutation
- Automatic acceptance of proposed findings (verification is mandatory)
- Automatic manuscript merge or publication
- Provider-specific text-to-speech calls

Those belong to adapters in the machine built around the author. V3.1 defines the
stable author identity, evidence contracts, stopping rules, and final human voice
gate those adapters must honor.

# Penname Codex v3

Provider-neutral author harness for audio-first progression fantasy.

V3 separates the creative author from the production machine:

- `craft/CORE.md` protects universal reader trust.
- `craft/VOICE.md` positively defines the pen name's prose and emotional method.
- `craft/modules/` contains optional genre-specific guidance and editor gates.
- `agents/` defines roles without naming a provider or model.
- `contracts/` defines interoperable JSON artifacts.
- `scripts/build_prompt.py` compiles the same frozen prompt regardless of which
  provider orchestrates the run.

Claude may author while Codex edits, or Codex may orchestrate Claude and then
occupy the editor seat. Nothing in the core changes when control changes hands.

## Design boundary

```text
orchestrator (Claude or Codex)
        |
        +-- validates one scene packet
        +-- compiles one role prompt
        +-- records provider/model/hash metadata
        |
        +--> author seat (recommended: Fable)
        |       +-- manuscript
        |       +-- author report
        |
        +--> editor seat (recommended: different model family)
                +-- gate results
                +-- proposed findings
                +-- strengths and taste concerns
```

Provider adapters are intentionally outside the trusted core. A provider may
change command syntax, authentication, model aliases, or tool names without
changing the author.

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

Give that exact prompt to the author seat. The seat needs file access to the
docked book root so it can write the two paths declared by `output`.

After the author has written the draft and report, compile the editor prompt:

```bash
python3 -B pennamecodexv3/scripts/build_prompt.py editor \
  --packet path/to/scene-packet.json \
  --root path/to/book > editor.prompt.md
```

The compiler refuses missing required context, paths outside the book root,
invalid packets, missing editor drafts, and context bundles larger than 2 MB.
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

## Running in either direction

- [Codex orchestrates, Claude authors](workflows/codex-orchestrates.md)
- [Claude orchestrates, Codex edits](workflows/claude-orchestrates.md)

Both workflows compile identical role prompts. Compare prompt hashes in run
records to prove that an orchestration change did not alter the creative
contract.

`examples/minimal-book/` is a fully docked fixture with frozen canon, arc,
state, packet, draft, and author report. It allows both the author and editor
prompt paths to run immediately after cloning.

## What v3 deliberately does not automate yet

- Provider API calls and authentication
- Canon retrieval or vector search
- State-ledger mutation
- Automatic acceptance of proposed findings
- Automatic manuscript merge or publication

Those belong to the machine built around the author. V3 first establishes the
stable contracts that machine must honor.

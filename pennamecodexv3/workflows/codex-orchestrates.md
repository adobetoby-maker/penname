# Workflow — Codex Orchestrates, Claude Authors

## Seat assignment

- Orchestrator: Codex
- Author: Claude Fable or the selected Claude writing model
- Editor: Codex, preferably in a fresh context
- Verifier: deterministic checks plus Codex or a human for semantic findings

Seat assignment is run metadata, not a change to the core.

## Run

1. Codex creates a scene packet from approved book artifacts.
2. Validate the packet against `contracts/scene-packet.schema.json`.
3. Compile the author prompt with `scripts/build_prompt.py author`.
4. Record the packet and prompt SHA-256 values in a run record.
5. Invoke Claude with the compiled prompt and access limited to the book
   worktree. Claude writes only the declared draft and author-report paths.
6. Validate the author report. Confirm no unexpected paths changed.
7. Compile the editor prompt from the same packet after the draft exists.
8. Invoke Codex in a fresh context. Codex writes one editor report and does not
   modify the manuscript.
9. Verify proposed findings before sending any to a repair run.
10. Create a new packet with `job` set to the appropriate repair type and copy
    each verified finding's ID, severity, gate, evidence, consequence, and
    repair target into `verified_findings`.
11. Advance `loop-state.json` using `scripts/advance_loop.py`; continue until
    the scene and larger-scope audits close or the bounded retry policy blocks.

## Isolation requirements

- Use a clean branch or worktree for each author run.
- Diff the worktree after each seat finishes.
- Reject modifications outside declared output paths.
- Freeze canon and state revisions for the duration of a run.
- Never pass editorial chat history into the author; pass verified findings as
  artifacts.

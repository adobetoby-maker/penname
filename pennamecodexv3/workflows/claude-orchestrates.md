# Workflow — Claude Orchestrates, Codex Edits

## Seat assignment

- Orchestrator: Claude Code
- Author: Claude Fable or the selected Claude writing model in a fresh context
- Editor: Codex using the compiled editor prompt
- Verifier: deterministic checks plus Claude, Codex, or a human as appropriate

The orchestrator must not silently add chat context to either seat. The compiled
prompt and frozen files are the run contract.

## Run

1. Claude Code creates a scene packet from approved book artifacts.
2. Validate the packet against `contracts/scene-packet.schema.json`.
3. Compile the author prompt with `scripts/build_prompt.py author`.
4. Record packet and prompt SHA-256 values in a run record.
5. Start the Fable author in a clean context with only the compiled prompt and
   limited book-worktree access.
6. Validate the author report. Confirm no unexpected paths changed.
7. Compile the editor prompt from the same packet after the draft exists.
8. Invoke Codex with that exact prompt in a fresh context. Codex produces an
   editor report without modifying the manuscript.
9. Verify proposed findings before repair.
10. Give the author the complete verified finding payload through a repair
    packet. Recompile rather than continuing the drafting conversation.
11. Advance `loop-state.json` using `scripts/advance_loop.py`; continue until
    the scene and larger-scope audits close or the bounded retry policy blocks.

## Equivalence check

For the same repository revision, packet, and role, `build_prompt.py` must emit
the same SHA-256 value whether Claude or Codex launches it. If hashes differ,
the runs are not equivalent and must not be compared as model-only differences.

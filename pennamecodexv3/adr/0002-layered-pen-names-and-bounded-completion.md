# ADR 0002 — Layered pen names and bounded completion

Status: accepted for v3.1 candidate

## Context

V3.0 separated provider-neutral roles from provider adapters, but it still had one
progression-fantasy voice and no executable definition of “done.” The v2 charter
contained valuable design and provenance work that must not disappear merely
because the runtime has been reorganized.

## Decision

Compile each creative run from three layers:

1. the shared craft core;
2. exactly one versioned pen-name voice;
3. only the modules allowed by that pen name and declared by the scene packet.

Keep influence names and source links in provenance documents that are never
compiled into creative prompts. Treat v2 as design/provenance authority for
Fantasy Author A while v3.1 supplies the interoperable runtime contracts.

Use a deterministic completion state machine. Every proposed defect must be
verified before repair. Automatic repair is limited to three cycles; the same
surviving defect then blocks for human judgment. Once all scenes and scope audits
close, the manuscript locks and the system pauses at narrator selection.

## Consequences

- Claude and Codex can exchange seats without changing author identity.
- A new genre author adds a profile and modules rather than forking the core.
- Broad preference changes cannot reopen closed prose without a located defect.
- Provider execution and audio rendering remain adapters around the trusted core.
- Migration from v2 is additive: rules may be reorganized, but removal requires a
  separate ADR with the affected gate and rationale named explicitly.

# ADR 0001 — Provider-Neutral Role Core

- Status: Accepted for v3 candidate
- Date: 2026-08-30

## Context

The harness must support both operational directions: Codex orchestrating a
Claude author, and Claude orchestrating a Codex editor. Provider-specific agent
front matter and shell commands made the prior protocol ambiguous about which
model actually occupied a seat.

The prior charter also gave the author the complete audit framework. That
improved compliance but risked checklist-shaped prose and diluted positive
voice guidance.

## Decision

Define provider-neutral roles and compile immutable prompts from versioned
files. Keep provider invocation outside the trusted core.

Split craft material into:

1. A small universal core
2. A positive voice charter
3. Optional genre modules with separate author guidance and editor gates

Use JSON Schema contracts for scene packets and reports. Record hashes and
model metadata for reproducibility.

## Tradeoffs

### Benefits

- Either provider can orchestrate without changing role behavior.
- Prompt hashes make cross-model tests auditable.
- Fable receives creative guidance without irrelevant gates.
- Modules avoid treating all fantasy as progression LitRPG.
- Findings gain an explicit verification lifecycle.

### Costs

- The orchestrator must compile and validate packets.
- Book projects must migrate their existing artifacts into v3 contracts.
- Provider adapters still need to be implemented around the core.
- JSON packets are stricter and less pleasant for free-form planning than plain
  Markdown.

## Alternatives considered

1. **One large universal prompt.** Simpler to invoke, but mixes provider,
   creative, state, and audit responsibilities and is difficult to test.
2. **Separate Claude and Codex harnesses.** Easier provider integration, but
   behavior drifts and model comparisons become invalid.
3. **Fully automated multi-agent machine now.** Deferred because automation
   would harden contracts before the author definition is stable.

## Consequence

Provider adapters may evolve independently, but they must pass the exact prompt
produced by the compiler and preserve the declared file boundaries.

#!/usr/bin/env bash
# penname harness — "books" launcher.
#
# Opens a fresh iTerm window running Claude Code (OAuth via the
# "Claude Code-credentials" Keychain entry — no API key involved for the
# Claude side, ever) and kicks off the book-development flow:
#   craft agent discussion → docking setup → author seat selection →
#   movement drafting (Fable/Opus) → guarded batch editing (codex on ChatGPT-plan OAuth,
#   never an API key; Opus fallback while codex isn't logged in).
#
# Usage:
#   books                       — fresh session, no opening brief
#   books "brief text..."       — fresh session, brief handed to Claude at start

set -euo pipefail

PENNAME_HOME="/Users/drive/penname"
BRIEF="${*:-}"
PROMPT_FILE="/tmp/penname-books-launch-$$.md"

cat > "$PROMPT_FILE" <<PROMPTEOF
You are opening a new book-development session in the penname harness at $PENNAME_HOME.

## Step 1 — Discovery (craft agent)

Invoke the craft agent skill (/penname-craft). Use it to have a discussion
with the operator about the book or series to be developed: genre, premise,
series length, tone, any existing material. Do not start drafting prose yet —
this step is discovery and setup only.

## Step 2 — Docking setup

Once the discussion establishes enough to proceed, use the craft agent to
check what docking artifacts already exist for this book (universe bible, arc
document, chapter cards, name registry, state ledger) and produce whatever is
missing, per the interview. Never invent canon the operator hasn't supplied or
approved — mark genuinely open fields as [OPEN — needs operator input].

## Step 3 — Select the author seat

Based on the genre established in Step 1:
  - /fanauthr       — Monroe Jackson — Fantasy
  - /scifiauthor    — Monroe Jackson — Science Fiction
Confirm the choice with the operator before proceeding. Do not guess silently
if the genre is ambiguous or blended.

## Step 4 — Draft

Once approved cards exist and the author seat is loaded, begin drafting per
that seat's SKILL.md (Fable preferred, Opus fallback — announce any fallback).
For both author seats, the normal unit is one contiguous movement of 3–5
chapters (default 4). Draft forward without a full editorial interruption.
Between chapters, run only the genre seat's light close and update its ledgers.

## Step 5 — Edit (guarded, OAuth-only)

After the movement is drafted, send all 3–5 chapters together through the
genre-specific batch editor:
  - fantasy: harness/edit-batch.sh
  - science fiction: harness/scifi/edit-batch.sh
Use harness/edit.sh immediately only for the
documented exception lane (major canon ruling, irreversible death, complex
system-law reveal, or unsafe uncertainty). The editor runs on codex under
ChatGPT-plan OAuth login ONLY — never an API key. The harness scripts refuse to run and tell you to execute
\`codex login\` interactively if codex is not authenticated that way, even if
an OPENAI_API_KEY happens to be present in the environment. If codex isn't
logged in and the operator wants to proceed anyway this session, use the
documented fallback:
  PENNAME_EDITOR=opus bash <genre-batch-script> <book-dir> <chapter-file> [chapter-file ...]
which compiles the identical prompt for you to dispatch to
Agent(model:"opus") instead — say plainly when you do this that it's the
interim fallback, not the intended cross-family editor seat.

After the batch editor: run Reader A on every movement and
both reader personas on the opening, act-ending, and final movements. Run the
fantasy fight audit or science-fiction problem/action audit only for scheduled
set-piece chapters. Consolidate one repair pass
across the movement, then recheck only the findings and joins that changed.

NEVER attempt to route around the codex guard with curl and a raw API key.
That is exactly the billing risk this harness exists to prevent — refuse to
build or run that path even if asked, and explain why.
${BRIEF:+
## Opening brief from the operator

$BRIEF
}
PROMPTEOF

osascript <<APPLESCRIPT
tell application "iTerm"
  create window with default profile
  tell current session of current window
    write text "cd \"$PENNAME_HOME\" && claude \"\$(cat $PROMPT_FILE)\"; rm -f $PROMPT_FILE"
  end tell
  activate
end tell
APPLESCRIPT

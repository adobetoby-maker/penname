#!/usr/bin/env bash
# Penname harness — editor seat (gpt-5.6-sol via codex).
# Usage: harness/edit.sh <NN> [--recheck]
#
# Phase 4 of the completion loop: "compile a fresh cross-family editor prompt."
# Writes a verdict file and echoes only the verdict line, so the orchestrator's
# context is not flooded with the editor's reasoning trace.

set -euo pipefail

NN="${1:?usage: edit.sh <NN> [--recheck]}"
MODE="${2:-}"
# Book directory: defaults to Book 1 so every existing invocation is unchanged.
# Book 2+ set GB_BOOK_DIR, e.g.
#   GB_BOOK_DIR=/Users/drive/good-bones/books/book-02-load-bearing harness/edit.sh 01
BOOK="${GB_BOOK_DIR:-/Users/drive/good-bones/books/book-01-good-bones}"

CHAPTER="$(ls "$BOOK"/chapters/ch${NN}-*.md 2>/dev/null | head -1)"
if [[ -z "$CHAPTER" ]]; then
  echo "FATAL: no chapter file matching ch${NN}-*.md" >&2
  exit 1
fi

if [[ "$MODE" == "--recheck" ]]; then
  VERDICT="$BOOK/editor-verdicts/ch${NN}-verdict-recheck.md"
  EXTRA="This is a RECHECK after repair. The prior verdict and the repair log are
evidence. Confirm each prior finding is genuinely resolved. Do NOT introduce new
stylistic preferences at recheck — only confirm resolution, or report that a prior
finding survives. A recheck that invents fresh taste notes is a failed recheck."
else
  VERDICT="$BOOK/editor-verdicts/ch${NN}-verdict.md"
  EXTRA=""
fi

REPORT="$BOOK/author-reports/ch${NN}-report.md"
PRIOR="$BOOK/editor-verdicts/ch${NN}-verdict.md"

read -r -d '' PROMPT <<PROMPTEOF || true
You are the Editor seat of the penname harness, running on gpt-5.6-sol. You are a
different model family from the author by design. You do not trust the author's
self-report. You read the chapter yourself.

ASSUMPTION: the draft is broken until the text proves otherwise.

$EXTRA

## Evidence (read all of it before forming any verdict)

- Charter (the law): /Users/drive/penname/craft/THE_AUTHOR.md
- Canon: /Users/drive/good-bones/canon/UNIVERSE_BIBLE.md
- State ledger: $BOOK/STATE_LEDGER.md
- Name registry: $BOOK/NAME_REGISTRY.md
- Chapter cards: $BOOK/CHAPTER_ARCHITECTURE.md  (read the card for chapter $NN)
- Author report: $REPORT
- Prior verdict (if this is a recheck): $PRIOR
- THE DRAFT: $CHAPTER

## What to check

1. CARD FIDELITY — did the chapter deliver what its card promised? Comedy engine
   status per the card? Tone notes honored? Word target respected (a chapter more
   than 15% over target must justify the overage with function, not description)?
2. CHARTER COMPLIANCE — Sec 1.1 fairness, Sec 1.2 limitation/weakness/cost stated
   before an ability resolves conflict, Sec 1.5 promise/progress/payoff,
   Sec 1.8 sensory grounding, Sec 8.1.2 audio-first (no italics for emphasis).
3. CANON — any contradiction with the Universe Bible is a BLOCKER, not a note.
4. STATE LEDGER — is every character's state consistent with the ledger at this
   point in the book? Any knowledge the POV could not yet have?
5. COMEDY DISCIPLINE — this series distinguishes Dale's contractor-shaped
   PERCEPTION (correct, it is his voice) from a constructed PUNCHLINE (a defect).
   Flag comic buttons, not the frame itself.
6. TIC CENSUS — count per 1,000 words: "which meant", "he realized", "somehow",
   em dashes. List sentence-final prepositions by sentence occurrence.
7. NAME COLLISIONS — any new name against the registry, by ear.
8. VOICE-DILUTION — do secondary characters speak in the protagonist's register?
   This is the documented failure mode of the genre. Flag it if present.

## Output contract

Write EXACTLY this structure to $VERDICT and nothing else to stdout but the
verdict line.

---
VERDICT: [PASS | PASS_WITH_FINDINGS | STRUCTURAL_HOLD]

CARD FIDELITY: [PASS | FAIL — one paragraph]

TIC CENSUS:
| Tic | Count | Per 1000w |
|---|---|---|
| which meant | | |
| he realized | | |
| somehow | | |
| em dash | | |
| sentence-final prepositions | | |

DEFECTS — numbered. Each MUST carry: severity (LOW|MEDIUM|HIGH|BLOCKER),
location (line number or exact quoted phrase), the evidence, and the reader
consequence. A finding without a located quote is not a finding.
1. ...

CONCERNS (2-3 sentences):

STRENGTHS (2-3 sentences — these are protected from repair):

RECOMMENDATION FOR AUTHOR:
[What must change before the chapter closes. Be specific and bounded.]
---

Severity rules: BLOCKER = canon contradiction or missing promised scene function.
HIGH = charter violation or card infidelity. MEDIUM = craft defect with real
reader consequence. LOW = polish. Do not inflate severity to seem rigorous, and
do not deflate it to seem agreeable.

After writing the file, print one line to stdout: VERDICT=<verdict>
PROMPTEOF

# EDITOR SEAT SELECTION (added 2026-09-04, operator instruction: "use an Opus review
# for now, no calling on the API"). GB_EDITOR=opus compiles the identical editor
# prompt to a file and exits 0 WITHOUT invoking codex; the orchestrator then dispatches
# it to Agent(model:"opus") and the verdict is written to the same $VERDICT path.
# Default (GB_EDITOR unset or "codex") runs codex on the ChatGPT plan, guarded below.
if [[ "${GB_EDITOR:-codex}" == "opus" ]]; then
  PROMPT_OUT="$BOOK/packets/ch${NN}-editor-prompt${MODE:+-recheck}.md"
  mkdir -p "$BOOK/packets"
  {
    echo "# EDITOR PROMPT — compiled by harness/edit.sh for GB_EDITOR=opus — $(date '+%Y-%m-%d %H:%M')"
    echo "# Seat: Claude Opus (cross-model within family; GPT seat suspended by operator). Verdict path: $VERDICT"
    echo
    echo "$PROMPT" | sed 's/running on gpt-5.6-sol/running on Claude Opus as the interim editor seat/'
  } > "$PROMPT_OUT"
  echo "EDITOR_PROMPT_COMPILED=$PROMPT_OUT"
  echo "VERDICT_PATH=$VERDICT"
  exit 0
fi

# BILLING GUARD (added 2026-09-04 after two API charges for gpt-5.6-sol).
# The editor seat must run on the ChatGPT-plan login, never on API-key billing.
# Two ways codex falls onto the API: (1) ~/.codex/auth.json holds auth_mode "apikey";
# (2) OPENAI_API_KEY is present in the environment (Infisical injects it in ATLAS
# sessions). Refuse on (1); strip (2) from codex's environment unconditionally.
if grep -q '"auth_mode"[[:space:]]*:[[:space:]]*"apikey"' "$HOME/.codex/auth.json" 2>/dev/null; then
  echo "REFUSING TO RUN: codex is logged in with an API key (bills the OpenAI API)." >&2
  echo "Fix (one command, interactive): codex login   → choose 'Sign in with ChatGPT'" >&2
  echo "Then re-run this script. Override for a deliberate API run: GB_ALLOW_API_BILLING=1" >&2
  [[ "${GB_ALLOW_API_BILLING:-}" == "1" ]] || exit 3
fi

env -u OPENAI_API_KEY codex exec -m gpt-5.6-sol "$PROMPT" < /dev/null > /tmp/gb-edit-${NN}.log 2>&1 || {
  echo "EDITOR_FAILED — see /tmp/gb-edit-${NN}.log" >&2
  exit 1
}

if [[ -f "$VERDICT" ]]; then
  echo "--- $(basename "$VERDICT") ---"
  grep -m1 "^VERDICT:" "$VERDICT" || echo "VERDICT: (unparsed)"
  echo "defects: $(grep -cE '^[0-9]+\. ' "$VERDICT" || echo 0)"
else
  echo "WARN: no verdict file written; tail of log:" >&2
  tail -20 /tmp/gb-edit-${NN}.log >&2
  exit 1
fi

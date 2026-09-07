#!/usr/bin/env bash
# Penname harness (fantasyau1.1) — editor seat (gpt-5.6-sol via codex).
# Usage: harness/fantasyau1.1/edit.sh <NN> [--recheck]
#
# Phase 4 of the 1.1 completion loop: compile a fresh cross-family editor
# prompt from pen-names/fantasyau1.1/seats/editor-prompt-1.1.md, attach this
# chapter's sentence-variance figures (variance.py), and run it. Writes a
# verdict file and echoes only the verdict line plus the two-track finding
# counts, so the orchestrator's context is not flooded with the editor's
# reasoning trace.
#
# Carried forward unchanged from the 1.0 harness/edit.sh: the API-billing
# guard, `env -u OPENAI_API_KEY`, `< /dev/null`, and the GB_EDITOR=opus
# fallback that compiles the prompt to a file instead of calling codex.

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: edit.sh <NN> [--recheck]

Compiles the fantasyau1.1 two-track editor prompt (editor-prompt-1.1.md) for
chapter NN, attaches that chapter's sentence-variance figures, and runs it
on codex (gpt-5.6-sol, ChatGPT-plan OAuth only -- never an API key).

Writes:
  $BOOK/editor-verdicts/chNN-verdict.md            (default)
  $BOOK/editor-verdicts/chNN-verdict-recheck.md    (--recheck)

Prints to stdout: the verdict line, the DEFECTS count, and the PULL findings
count (parsed from the two-track output structure).

Environment:
  GB_BOOK_DIR            Book directory. Defaults to
                         /Users/drive/good-bones/books/book-01-good-bones
  GB_EDITOR=opus         Compile the identical prompt to a file and exit 0
                         WITHOUT invoking codex (operator instruction: run
                         the interim editor seat on Claude Opus instead of
                         the API-billed GPT seat). The orchestrator then
                         dispatches Agent(model:"opus") at the printed path.
  GB_ALLOW_API_BILLING=1 Override the billing guard for a deliberate API run.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

NN="${1:?usage: edit.sh <NN> [--recheck] (--help for details)}"
MODE="${2:-}"
if ! [[ "$NN" =~ ^[0-9]{1,2}$ ]]; then
  echo "FATAL: NN must be a one- or two-digit chapter number, got: $NN" >&2
  exit 1
fi
NN="$(printf "%02d" "$((10#$NN))")"
if [[ -n "$MODE" && "$MODE" != "--recheck" ]]; then
  echo "FATAL: second argument, if given, must be --recheck; got: $MODE" >&2
  exit 1
fi

# Book directory: defaults to Book 1 so every existing invocation is unchanged.
# Book 2+ set GB_BOOK_DIR, e.g.
#   GB_BOOK_DIR=/Users/drive/good-bones/books/book-02-load-bearing harness/fantasyau1.1/edit.sh 01
BOOK="${GB_BOOK_DIR:-/Users/drive/good-bones/books/book-01-good-bones}"
SEATS_DIR="/Users/drive/penname/pennamecodexv3/pen-names/fantasyau1.1/seats"
EDITOR_PROMPT_SRC="$SEATS_DIR/editor-prompt-1.1.md"
VARIANCE_PY="/Users/drive/penname/pennamecodexv3/scripts/fantasyau1.1/variance.py"
CHARTER="/Users/drive/penname/craft/THE_AUTHOR-1.1.md"
CANON="/Users/drive/good-bones/canon/UNIVERSE_BIBLE.md"

for f in "$EDITOR_PROMPT_SRC" "$VARIANCE_PY" "$CHARTER"; do
  if [[ ! -f "$f" ]]; then
    echo "FATAL: missing required input: $f" >&2
    exit 1
  fi
done

CHAPTER="$(ls "$BOOK"/chapters/ch${NN}-*.md 2>/dev/null | head -1)"
if [[ -z "$CHAPTER" ]]; then
  echo "FATAL: no chapter file matching ch${NN}-*.md" >&2
  exit 1
fi

if [[ "$MODE" == "--recheck" ]]; then
  VERDICT="$BOOK/editor-verdicts/ch${NN}-verdict-recheck.md"
  EXTRA="This is a RECHECK after repair. The prior verdict and the repair log are
evidence. Confirm each prior finding (on EITHER track) is genuinely resolved.
Do NOT introduce new stylistic preferences at recheck -- only confirm
resolution, or report that a prior finding survives. A recheck that invents
fresh taste notes is a failed recheck."
else
  VERDICT="$BOOK/editor-verdicts/ch${NN}-verdict.md"
  EXTRA=""
fi

REPORT="$BOOK/author-reports/ch${NN}-report.md"
PRIOR="$BOOK/editor-verdicts/ch${NN}-verdict.md"
BRIEF="$BOOK/packets/ch${NN}-brief.md"
NN_PREV_NUM=$((10#$NN - 1))
if [[ "$NN_PREV_NUM" -ge 1 ]]; then
  NN_PREV="$(printf "%02d" "$NN_PREV_NUM")"
  PREV_LEDGER_NOTE="STATE_LEDGER.md entry for chapter ${NN_PREV} (the entry immediately preceding this chapter)"
else
  PREV_LEDGER_NOTE="STATE_LEDGER.md's seeded pre-chapter-1 state (this is the book's first chapter)"
fi

# Sentence-variance figures for THIS chapter, attached verbatim so the editor
# does not have to recompute them (Gate 32).
VARIANCE_JSON="$(python3 "$VARIANCE_PY" "$CHAPTER" 2>/tmp/gb-variance-${NN}.log)" || {
  echo "FATAL: variance.py failed on $CHAPTER — see /tmp/gb-variance-${NN}.log" >&2
  exit 1
}

EDITOR_PROMPT_BODY="$(cat "$EDITOR_PROMPT_SRC")"

read -r -d '' PROMPT <<PROMPTEOF || true
You are the Editor seat of the penname harness (fantasyau1.1), running on
gpt-5.6-sol -- a different model family from the author by design. You do not
trust the author's self-report. You read the chapter yourself, twice: once as
an editor, once as a reader.

ASSUMPTION: the draft is broken until the text proves otherwise.

$EXTRA

## Evidence (read all of it before forming any verdict)

- Charter: $CHARTER, especially §9 gates 1–27 and §10 gates 28–37
- Canon: $CANON
- State ledger: $BOOK/STATE_LEDGER.md ($PREV_LEDGER_NOTE)
- Name registry: $BOOK/NAME_REGISTRY.md
- Chapter architecture / canon walls (read the card for chapter $NN): $BOOK/CHAPTER_ARCHITECTURE.md
- Chapter brief (what the author drafted from): $BRIEF
- Author report: $REPORT
- Prior verdict (if this is a recheck): $PRIOR
- THE DRAFT (the manuscript): $CHAPTER

## Sentence-variance figures for this chapter (produced by variance.py; Gate 32 -- use these, do not recompute)

\`\`\`json
$VARIANCE_JSON
\`\`\`

## Instructions

$EDITOR_PROMPT_BODY

Write the verdict to $VERDICT and nothing else to stdout but the verdict
line. After writing the file, print one line to stdout: VERDICT=<verdict>
PROMPTEOF

# EDITOR SEAT SELECTION (carried from the 1.0 script, operator instruction:
# "use an Opus review for now, no calling on the API"). GB_EDITOR=opus
# compiles the identical editor prompt to a file and exits 0 WITHOUT invoking
# codex; the orchestrator then dispatches it to Agent(model:"opus") and the
# verdict is written to the same $VERDICT path.
# Default (GB_EDITOR unset or "codex") runs codex on the ChatGPT plan, guarded below.
if [[ "${GB_EDITOR:-codex}" == "opus" ]]; then
  PROMPT_OUT="$BOOK/packets/ch${NN}-editor-prompt${MODE:+-recheck}.md"
  mkdir -p "$BOOK/packets"
  {
    echo "# EDITOR PROMPT — compiled by harness/fantasyau1.1/edit.sh for GB_EDITOR=opus — $(date '+%Y-%m-%d %H:%M')"
    echo "# Seat: Claude Opus (cross-model within family; GPT seat suspended by operator). Verdict path: $VERDICT"
    echo
    echo "$PROMPT" | sed 's/running on gpt-5.6-sol/running on Claude Opus as the interim editor seat/'
  } > "$PROMPT_OUT"
  echo "EDITOR_PROMPT_COMPILED=$PROMPT_OUT"
  echo "VERDICT_PATH=$VERDICT"
  exit 0
fi

# BILLING GUARD (carried from the 1.0 script, added after two API charges for
# gpt-5.6-sol). The editor seat must run on the ChatGPT-plan login, never on
# API-key billing. Two ways codex falls onto the API: (1) ~/.codex/auth.json
# holds auth_mode "apikey"; (2) OPENAI_API_KEY is present in the environment
# (Infisical injects it in ATLAS sessions). Refuse on (1); strip (2) from
# codex's environment unconditionally.
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

if [[ ! -f "$VERDICT" ]]; then
  echo "WARN: no verdict file written; tail of log:" >&2
  tail -20 /tmp/gb-edit-${NN}.log >&2
  exit 1
fi

echo "--- $(basename "$VERDICT") ---"
grep -m1 "^VERDICT:" "$VERDICT" || echo "VERDICT: (unparsed)"

# Two-track summary: DEFECTS numbered findings, and PULL's own numbered
# "Findings:" block (the PULL section's narrative fields -- Hook/Want/
# Action/etc. -- are not findings and must not be counted). A chapter edited
# under the 1.0 single-track format has no "PULL" section at all -- the
# DEFECTS block then simply runs to CONCERNS, and PULL_FINDINGS_COUNT is 0.
# Headings are matched loosely ("DEFECTS —" or "DEFECTS:") since both
# separators appear across filed verdicts.
DEFECTS_BLOCK="$(awk '/^DEFECTS/{flag=1; next} /^PULL:/{flag=0} /^CONCERNS/{flag=0} flag' "$VERDICT")"
DEFECTS_COUNT="$(printf '%s\n' "$DEFECTS_BLOCK" | grep -cE '^[0-9]+\. ' || true)"

PULL_FINDINGS_BLOCK="$(awk '/^Findings:/{flag=1; next} /^CONCERNS/{flag=0} flag' "$VERDICT")"
PULL_FINDINGS_COUNT="$(printf '%s\n' "$PULL_FINDINGS_BLOCK" | grep -cE '^[0-9]+\. ' || true)"

echo "defects: ${DEFECTS_COUNT:-0}"
echo "pull_findings: ${PULL_FINDINGS_COUNT:-0}"

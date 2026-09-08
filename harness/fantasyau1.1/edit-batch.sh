#!/usr/bin/env bash
# fantasyau1.1 — cross-family editor for a 3–5 chapter movement.
# Usage: edit-batch.sh <START> <END> [--recheck]

set -euo pipefail

usage() {
  echo "Usage: edit-batch.sh <START> <END> [--recheck]"
  echo "Environment: GB_BOOK_DIR=<book>; GB_EDITOR=opus compiles without calling Codex."
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then usage; exit 0; fi

START_RAW="${1:?$(usage)}"
END_RAW="${2:?$(usage)}"
MODE="${3:-}"
if ! [[ "$START_RAW" =~ ^[0-9]{1,2}$ && "$END_RAW" =~ ^[0-9]{1,2}$ ]]; then
  echo "FATAL: START and END must be chapter numbers" >&2; exit 1
fi
if [[ -n "$MODE" && "$MODE" != "--recheck" ]]; then
  echo "FATAL: third argument, if present, must be --recheck" >&2; exit 1
fi

START_NUM=$((10#$START_RAW))
END_NUM=$((10#$END_RAW))
if (( END_NUM < START_NUM )); then echo "FATAL: END precedes START" >&2; exit 1; fi
COUNT=$((END_NUM - START_NUM + 1))
if (( COUNT < 3 || COUNT > 5 )); then
  echo "NOTICE: movement contains $COUNT chapters; normal range is 3–5." >&2
fi

START="$(printf '%02d' "$START_NUM")"
END="$(printf '%02d' "$END_NUM")"
BOOK="${GB_BOOK_DIR:-/Users/drive/good-bones/books/book-01-good-bones}"
SEATS="/Users/drive/penname/pennamecodexv3/pen-names/fantasyau1.1/seats"
PROMPT_SRC="$SEATS/batch-editor-prompt.md"
CHARTER="/Users/drive/penname/craft/THE_AUTHOR-1.1.md"
VARIANCE="/Users/drive/penname/pennamecodexv3/scripts/fantasyau1.1/variance.py"
CANON="$BOOK/UNIVERSE_BIBLE.md"
[[ -f "$CANON" ]] || CANON="/Users/drive/good-bones/canon/UNIVERSE_BIBLE.md"

for REQUIRED in "$PROMPT_SRC" "$CHARTER" "$VARIANCE"; do
  [[ -f "$REQUIRED" ]] || { echo "FATAL: missing $REQUIRED" >&2; exit 1; }
done
[[ -d "$BOOK" ]] || { echo "FATAL: missing book directory $BOOK" >&2; exit 1; }

mkdir -p "$BOOK/editor-verdicts" "$BOOK/packets"
if [[ "$MODE" == "--recheck" ]]; then
  VERDICT="$BOOK/editor-verdicts/batch-ch${START}-ch${END}-verdict-recheck.md"
  PRIOR="$BOOK/editor-verdicts/batch-ch${START}-ch${END}-verdict.md"
  EXTRA="This is a targeted recheck. Confirm prior findings and changed seams only. Do not introduce new taste notes."
else
  VERDICT="$BOOK/editor-verdicts/batch-ch${START}-ch${END}-verdict.md"
  PRIOR="(none — first movement review)"
  EXTRA=""
fi

EVIDENCE=""
METRICS=""
CHAPTER_OUTPUTS=""
for N in $(seq "$START_NUM" "$END_NUM"); do
  NN="$(printf '%02d' "$N")"
  CHAPTER="$(find "$BOOK/chapters" -maxdepth 1 -type f -name "ch${NN}-*.md" -print | head -1)"
  [[ -n "$CHAPTER" ]] || { echo "FATAL: no chapter ch${NN}-*.md" >&2; exit 1; }
  BRIEF="$BOOK/packets/ch${NN}-brief.md"
  REPORT="$BOOK/author-reports/ch${NN}-report.md"
  EVIDENCE="${EVIDENCE}- Chapter ${NN}: ${CHAPTER}
  Brief: ${BRIEF}
  Author report: ${REPORT}
"
  CHAPTER_METRICS="$(python3 "$VARIANCE" "$CHAPTER")"
  METRICS="${METRICS}
Chapter ${NN}:
${CHAPTER_METRICS}
"
  if [[ "$MODE" == "--recheck" ]]; then
    CHAPTER_VERDICT="$BOOK/editor-verdicts/ch${NN}-verdict-recheck.md"
  else
    CHAPTER_VERDICT="$BOOK/editor-verdicts/ch${NN}-verdict.md"
  fi
  CHAPTER_OUTPUTS="${CHAPTER_OUTPUTS}- Chapter ${NN}: ${CHAPTER_VERDICT}
"
done

PROMPT_BODY="$(<"$PROMPT_SRC")"
read -r -d '' PROMPT <<PROMPTEOF || true
You are reviewing fantasyau1.1 chapters ${START}–${END} as a frozen movement.
$EXTRA

Evidence:
- Charter: $CHARTER
- Canon: $CANON
- Architecture: $BOOK/CHAPTER_ARCHITECTURE.md
- State ledger: $BOOK/STATE_LEDGER.md
- Name registry: $BOOK/NAME_REGISTRY.md
- Prior batch verdict: $PRIOR
$EVIDENCE
Sentence metrics are diagnostics, not automatic fixed-window findings. Gate 10
governs carded combat sustain:
$METRICS

$PROMPT_BODY

Write the full movement report to $VERDICT. Also write a compact companion
verdict for every chapter so progress reporting remains chapter-addressable:
$CHAPTER_OUTPUTS
Each companion contains VERDICT, DEFECTS, and PULL sections. Under PULL include
Hook, Action, `Humor beats: N`, and numbered Findings with severities. Do not run
another edit; derive these companions from the single movement review.

Print only VERDICT=<verdict> after writing all files.
PROMPTEOF

if [[ "${GB_EDITOR:-codex}" == "opus" ]]; then
  OUT="$BOOK/packets/batch-ch${START}-ch${END}-editor-prompt${MODE:+-recheck}.md"
  {
    echo "# fantasyau1.1 BATCH EDITOR PROMPT — $(date '+%Y-%m-%d %H:%M')"
    echo "# Opus fallback; verdict path: $VERDICT"
    echo
    echo "$PROMPT"
  } > "$OUT"
  echo "EDITOR_PROMPT_COMPILED=$OUT"
  echo "VERDICT_PATH=$VERDICT"
  exit 0
fi

if ! codex login status &>/dev/null; then
  echo "REFUSING TO RUN: Codex is not logged in through ChatGPT." >&2
  echo "Run 'codex login', or use GB_EDITOR=opus to compile the fallback packet." >&2
  exit 3
fi

LOG="/tmp/fantasyau11-batch-${START}-${END}-$$.log"
env -u OPENAI_API_KEY codex exec -m gpt-5.6-sol "$PROMPT" < /dev/null > "$LOG" 2>&1 || {
  echo "EDITOR_FAILED — see $LOG" >&2; exit 1;
}
[[ -f "$VERDICT" ]] || { echo "FATAL: editor did not write $VERDICT" >&2; exit 1; }
grep -m1 '^VERDICT:' "$VERDICT" || echo "VERDICT: (unparsed)"
echo "BATCH_VERDICT=$VERDICT"

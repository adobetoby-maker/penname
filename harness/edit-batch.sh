#!/usr/bin/env bash
# Fantasy Author A movement editor — cross-family batch review.
#
# Usage:
#   harness/edit-batch.sh <book-dir> <chapter-file> [chapter-file ...] [--recheck]
#
# Three to five contiguous chapters is the intended unit. The script accepts a
# different count for opening/closing fragments but announces the deviation.

set -euo pipefail

BOOK_DIR="${1:?usage: edit-batch.sh <book-dir> <chapter-file> [chapter-file ...] [--recheck]}"
shift

MODE=""
CHAPTERS=()
for ARG in "$@"; do
  if [[ "$ARG" == "--recheck" ]]; then
    MODE="--recheck"
  else
    CHAPTERS+=("$ARG")
  fi
done

COUNT="${#CHAPTERS[@]}"
if (( COUNT == 0 )); then
  echo "FATAL: supply at least one chapter file" >&2
  exit 1
fi
if (( COUNT < 3 || COUNT > 5 )); then
  echo "NOTICE: movement has $COUNT chapters; the normal batch is 3–5 (default 4)." >&2
fi

for CHAPTER in "${CHAPTERS[@]}"; do
  [[ -f "$CHAPTER" ]] || { echo "FATAL: chapter file not found: $CHAPTER" >&2; exit 1; }
done

CHARTER="/Users/drive/penname/craft/THE_AUTHOR.md"
SOUL="/Users/drive/penname/pennamecodexv3/pen-names/fantasy-author-a/SOUL.md"
VOICE="/Users/drive/penname/pennamecodexv3/pen-names/fantasy-author-a/VOICE.md"
PIPELINE="/Users/drive/penname/pennamecodexv3/pen-names/fantasy-author-a/PIPELINE.md"
for REQUIRED in "$CHARTER" "$SOUL" "$VOICE" "$PIPELINE"; do
  [[ -f "$REQUIRED" ]] || { echo "FATAL: required author file not found: $REQUIRED" >&2; exit 1; }
done

FIRST_BASE="$(basename "${CHAPTERS[0]}" .md)"
LAST_INDEX=$((COUNT - 1))
LAST_BASE="$(basename "${CHAPTERS[$LAST_INDEX]}" .md)"
RANGE="${FIRST_BASE}-${LAST_BASE}"
VERDICT_DIR="$BOOK_DIR/editor-verdicts"
PACKET_DIR="$BOOK_DIR/packets"
mkdir -p "$VERDICT_DIR" "$PACKET_DIR"

if [[ "$MODE" == "--recheck" ]]; then
  VERDICT="$VERDICT_DIR/batch-${RANGE}-verdict-recheck.md"
  PRIOR="$VERDICT_DIR/batch-${RANGE}-verdict.md"
  EXTRA="This is a targeted RECHECK. Confirm only the prior findings and the
changed seams. Do not introduce new preferences. A newly visible canon or safety
failure may be reported; ordinary new taste notes may not."
else
  VERDICT="$VERDICT_DIR/batch-${RANGE}-verdict.md"
  PRIOR="(none — first movement review)"
  EXTRA=""
fi

CHAPTER_LIST=""
for CHAPTER in "${CHAPTERS[@]}"; do
  CHAPTER_LIST="${CHAPTER_LIST}- ${CHAPTER}
"
done


read -r -d '' PROMPT <<PROMPTEOF || true
You are the cross-family Editor for Fantasy Author A. Read this batch as one
continuous movement before judging any chapter alone. The author drafted forward
without a full edit between chapters so that you can diagnose flow and connection
that an isolated chapter review cannot see.

$EXTRA

## Governing material

- Soul: $SOUL
- Voice: $VOICE
- Charter, including §10 movement gates: $CHARTER
- Movement pipeline: $PIPELINE
- Universe bible: $BOOK_DIR/UNIVERSE_BIBLE.md (or $BOOK_DIR/canon/UNIVERSE_BIBLE.md)
- Chapter architecture/cards: $BOOK_DIR/CHAPTER_ARCHITECTURE.md
- State ledger: $BOOK_DIR/STATE_LEDGER.md
- Name registry: $BOOK_DIR/NAME_REGISTRY.md
- Prior verdict: $PRIOR

## Manuscript movement, in reading order

$CHAPTER_LIST
Read the chapter immediately before this movement if it exists, and read the
next approved card after the movement. Use them only to judge the incoming and
outgoing handoffs; do not demand that this batch deliver later material early.

## Review pathways

1. DEFECTS: card delivery, charter gates 1–27, canon, state, injuries/resources,
   name collisions, reader standard, and audio readability.
2. CONNECTION: chronology, causal handoffs, emotional carryover, repeated
   explanations, forgotten questions, knowledge leaks, and whether each ending
   creates the next chapter's pressure.
3. PULL AND CADENCE: §10 gates 28–32; progression delivery; action spacing;
   scheduled set-piece scale and delivered word span; humor opportunities by
   chapter; cold runs; distinct dialogue; opening pressure; and whether the
   movement escalates and turns.
4. REPAIR SHAPE: prefer one repair that fixes both sides of a seam. Distinguish
   ADD, RECAST, MOVE, and CUT. Do not prescribe replacement prose.

Every finding must quote a location and state the reader consequence. Do not
turn a frequency target into forced jokes or arbitrary fights. Physical set
pieces include fights, chases, rescues, trials, collapses, escapes, and other
body-under-a-clock problems. Major set pieces normally run 1,500–2,500 words,
minor kinetic sequences 600–1,000, and climaxes may span scenes or chapters.
Judge function and immersion rather than rewarding padding. Preserve the
original progression-fantasy voice.

## Write exactly this report to $VERDICT

VERDICT: [PASS | PASS_WITH_FINDINGS | STRUCTURAL_HOLD]

MOVEMENT: [one paragraph: entry pressure → escalation → turn]

CHAPTER DELIVERY:
| Chapter | Card promise | Delivered? | Opening pressure | Action scale/span | Progression/power-cost | Humor opportunities |
|---|---|---|---|---|---|---|

SEAMS:
| Join | Causal handoff | State/knowledge continuity | Repetition | Finding |
|---|---|---|---|---|

ACTION AND PULL: [spacing across this batch and adjacent cards; cold-reader risks]

DEFECTS: numbered. Each includes severity (LOW/MEDIUM/HIGH/BLOCKER), chapter and
line/quote, evidence, reader consequence, and repair shape (ADD/RECAST/MOVE/CUT).

PROTECTED STRENGTHS: [specific passages or effects the repair must preserve]

CONSOLIDATED REPAIR ORDER: [one bounded list in reading order]

READER ROUTING: [A thirteen-year-old | B adult genre | BOTH] and why.

After writing the file, print one line to stdout: VERDICT=<verdict>
PROMPTEOF

if [[ "${PENNAME_EDITOR:-codex}" == "opus" ]]; then
  PROMPT_OUT="$PACKET_DIR/batch-${RANGE}-editor-prompt${MODE:+-recheck}.md"
  {
    echo "# BATCH EDITOR PROMPT — compiled $(date '+%Y-%m-%d %H:%M')"
    echo "# Seat: Claude Opus fallback. Verdict path: $VERDICT"
    echo
    echo "$PROMPT"
  } > "$PROMPT_OUT"
  echo "EDITOR_PROMPT_COMPILED=$PROMPT_OUT"
  echo "VERDICT_PATH=$VERDICT"
  exit 0
fi

if ! codex login status &>/dev/null; then
  echo "REFUSING TO RUN: codex is not logged in through ChatGPT." >&2
  echo "Run 'codex login' interactively, or compile the Opus fallback with:" >&2
  echo "PENNAME_EDITOR=opus harness/edit-batch.sh ..." >&2
  echo "A raw API-key route is intentionally unavailable." >&2
  exit 3
fi

LOG_PATH="/tmp/penname-batch-edit-$$.log"
env -u OPENAI_API_KEY codex exec "$PROMPT" > "$LOG_PATH" 2>&1 || {
  echo "EDITOR_FAILED — see $LOG_PATH" >&2
  exit 1
}

if [[ -f "$VERDICT" ]]; then
  grep -m1 "^VERDICT:" "$VERDICT" || echo "VERDICT: (unparsed)"
  echo "BATCH_VERDICT=$VERDICT"
else
  echo "WARN: no batch verdict file written; tail of log:" >&2
  tail -20 "$LOG_PATH" >&2
  exit 1
fi

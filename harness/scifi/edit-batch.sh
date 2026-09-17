#!/usr/bin/env bash
# Monroe Jackson — Science Fiction movement editor.
# Usage: harness/scifi/edit-batch.sh <book-dir> <chapter-file> [...] [--recheck]

set -euo pipefail

BOOK_DIR="${1:?usage: edit-batch.sh <book-dir> <chapter-file> [...] [--recheck]}"
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
(( COUNT > 0 )) || { echo "FATAL: supply at least one chapter file" >&2; exit 1; }
if (( COUNT < 3 || COUNT > 5 )); then
  echo "NOTICE: movement has $COUNT chapters; normal is 3–5 (default 4)." >&2
fi
for CHAPTER in "${CHAPTERS[@]}"; do
  [[ -f "$CHAPTER" ]] || { echo "FATAL: chapter file not found: $CHAPTER" >&2; exit 1; }
done

ROOT="/Users/drive/penname"
CHARTER="$ROOT/craft/THE_SCIFI_AUTHOR.md"
SOUL="$ROOT/pennamecodexv3/pen-names/science-fiction-author-b/SOUL.md"
VOICE="$ROOT/pennamecodexv3/pen-names/science-fiction-author-b/VOICE.md"
PIPELINE="$ROOT/pennamecodexv3/pen-names/science-fiction-author-b/PIPELINE.md"
for REQUIRED in "$CHARTER" "$SOUL" "$VOICE" "$PIPELINE"; do
  [[ -f "$REQUIRED" ]] || { echo "FATAL: required file not found: $REQUIRED" >&2; exit 1; }
done

FIRST_BASE="$(basename "${CHAPTERS[0]}" .md)"
LAST_INDEX=$((COUNT - 1))
LAST_BASE="$(basename "${CHAPTERS[$LAST_INDEX]}" .md)"
RANGE="${FIRST_BASE}-${LAST_BASE}"
VERDICT_DIR="$BOOK_DIR/editor-verdicts"
PACKET_DIR="$BOOK_DIR/packets"
mkdir -p "$VERDICT_DIR" "$PACKET_DIR"

if [[ "$MODE" == "--recheck" ]]; then
  VERDICT="$VERDICT_DIR/scifi-batch-${RANGE}-verdict-recheck.md"
  PRIOR="$VERDICT_DIR/scifi-batch-${RANGE}-verdict.md"
  EXTRA="This is a targeted RECHECK. Confirm prior findings and changed joins only.
Report a newly exposed canon, safety, or causality failure; do not add taste notes."
else
  VERDICT="$VERDICT_DIR/scifi-batch-${RANGE}-verdict.md"
  PRIOR="(none — first movement review)"
  EXTRA=""
fi

CHAPTER_LIST=""
for CHAPTER in "${CHAPTERS[@]}"; do
  CHAPTER_LIST="${CHAPTER_LIST}- ${CHAPTER}
"
done

read -r -d '' PROMPT <<PROMPTEOF || true
You are the cross-family Editor for Monroe Jackson — Science Fiction, author
standard 1.1.1. Read this batch as one continuous movement before judging a
chapter alone. The author drafted forward so you can see causality, flow, and
connection that an isolated review misses.

$EXTRA

## Governing material

- Soul: $SOUL
- Voice: $VOICE
- Charter, all 21 gates: $CHARTER
- Movement pipeline: $PIPELINE
- Universe bible and speculative allowances: $BOOK_DIR/UNIVERSE_BIBLE.md
- Arc/cards: $BOOK_DIR/CHAPTER_ARCHITECTURE.md
- State ledger: $BOOK_DIR/STATE_LEDGER.md
- Name registry: $BOOK_DIR/NAME_REGISTRY.md
- Prior verdict: $PRIOR

## Manuscript movement

$CHAPTER_LIST
Read the chapter immediately before this movement if it exists and the next
approved card after it. Use them only to judge incoming and outgoing handoffs.

## Review pathways

1. DEFECTS: card delivery, charter gates 1–16, canon, state, MICE threads,
   speculative allowances, plant/payoff fairness, reader standard, and audio.
2. CONNECTION: causal and emotional handoffs, chronology, knowledge, injuries,
   resources, repeated explanations, forgotten questions, and exit pressure.
3. PULL: gates 17–21; problem-engine progress; pressure-set-piece target seven
   or eight per twenty (floor five, no gap over four); scheduled scale and
   sustain; rolling two-chapter humor/warmth (aim four, acceptable three to
   five); cold-reader trends; and substantive dialogue ownership.
4. TECHNICAL FAIRNESS: every solution follows reader-legible rules; an invented
   premise pays its limitation, weakness, or cost; no joke or jargon hides a
   causal step; consequences persist.
5. REPAIR SHAPE: prefer one repair that fixes both sides of a seam. Label ADD,
   RECAST, MOVE, or CUT. Do not write replacement prose.

Pressure set pieces include EVA, chase, rescue, dangerous testing, failure
cascade, repair under a clock, survival, confrontation, or combat. MINOR
normally runs 600–1,000 words; MAJOR 1,500–2,500; CLIMAX has room for escalation,
choice, cost, and aftermath. A MAJOR chapter normally has a higher target,
often 6,000–6,500 words when ordinary chapters are near 5,000. Judge function,
not padding. Sample dialogue only if it has at least eight words or carries a
position, decision, evasion, or conflict.

Every finding quotes a location and names the reader consequence. Protect the
humane, clear, problem-solving voice.

## Write exactly this report to $VERDICT

VERDICT: [PASS | PASS_WITH_FINDINGS | STRUCTURAL_HOLD]

MOVEMENT: [entry pressure → escalation → turn]

CHAPTER DELIVERY:
| Chapter | Card/problem promise | Delivered? | Problem-engine step | Pressure scale/span | Technical/moral consequence | Humor/warmth |
|---|---|---|---|---|---|---|

SEAMS:
| Join | Causal handoff | State/knowledge | Relationship carryover | Repetition | Finding |
|---|---|---|---|---|---|

ACTION, DISCOVERY, AND PULL: [cadence, scale, rolling humor, reader trend]

TECHNICAL FAIRNESS: [allowance, constraint, plants, causal legibility]

DEFECTS: numbered; each includes severity (LOW/MEDIUM/HIGH/BLOCKER), chapter
and line/quote, evidence, reader consequence, and repair shape.

PROTECTED STRENGTHS: [specific passages/effects]

CONSOLIDATED REPAIR ORDER: [bounded list in reading order]

READER ROUTING: [A | B | BOTH] and why.

After writing the file, print one line to stdout: VERDICT=<verdict>
PROMPTEOF

if [[ "${PENNAME_EDITOR:-codex}" == "opus" ]]; then
  PROMPT_OUT="$PACKET_DIR/scifi-batch-${RANGE}-editor-prompt${MODE:+-recheck}.md"
  {
    echo "# SCI-FI BATCH EDITOR PROMPT — compiled $(date '+%Y-%m-%d %H:%M')"
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
  echo "Run 'codex login', or use PENNAME_EDITOR=opus harness/scifi/edit-batch.sh ..." >&2
  echo "A raw API-key route is intentionally unavailable." >&2
  exit 3
fi

LOG_PATH="/tmp/penname-scifi-batch-edit-$$.log"
env -u OPENAI_API_KEY codex exec "$PROMPT" > "$LOG_PATH" 2>&1 || {
  echo "EDITOR_FAILED — see $LOG_PATH" >&2
  exit 1
}

if [[ -f "$VERDICT" ]]; then
  grep -m1 "^VERDICT:" "$VERDICT" || echo "VERDICT: (unparsed)"
  echo "BATCH_VERDICT=$VERDICT"
else
  echo "WARN: no verdict file written; tail of log:" >&2
  tail -20 "$LOG_PATH" >&2
  exit 1
fi

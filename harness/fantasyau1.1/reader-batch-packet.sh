#!/usr/bin/env bash
# fantasyau1.1 — compile a manuscript-only cold-reader movement packet.
# Usage: reader-batch-packet.sh <START> <END> <A|B>

set -euo pipefail

usage() { echo "Usage: reader-batch-packet.sh <START> <END> <A|B>"; }
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then usage; exit 0; fi

START_RAW="${1:?$(usage)}"
END_RAW="${2:?$(usage)}"
PERSONA="$(printf '%s' "${3:?$(usage)}" | tr '[:lower:]' '[:upper:]')"
if ! [[ "$START_RAW" =~ ^[0-9]{1,2}$ && "$END_RAW" =~ ^[0-9]{1,2}$ ]]; then
  echo "FATAL: START and END must be chapter numbers" >&2; exit 1
fi
[[ "$PERSONA" == "A" || "$PERSONA" == "B" ]] || { echo "FATAL: persona must be A or B" >&2; exit 1; }

START_NUM=$((10#$START_RAW))
END_NUM=$((10#$END_RAW))
(( END_NUM >= START_NUM )) || { echo "FATAL: END precedes START" >&2; exit 1; }
START="$(printf '%02d' "$START_NUM")"
END="$(printf '%02d' "$END_NUM")"
BOOK="${GB_BOOK_DIR:-/Users/drive/good-bones/books/book-01-good-bones}"
PROMPT_SRC="/Users/drive/penname/pennamecodexv3/pen-names/fantasyau1.1/seats/cold-reader-batch-prompt.md"
[[ -f "$PROMPT_SRC" ]] || { echo "FATAL: missing $PROMPT_SRC" >&2; exit 1; }
[[ -d "$BOOK/chapters" ]] || { echo "FATAL: missing chapters directory $BOOK/chapters" >&2; exit 1; }

CHAPTERS=""
PREV_NUM=$((START_NUM - 1))
if (( PREV_NUM >= 1 )); then
  PREV="$(printf '%02d' "$PREV_NUM")"
  PREV_PATH="$(find "$BOOK/chapters" -maxdepth 1 -type f -name "ch${PREV}-*.md" -print | head -1)"
  [[ -n "$PREV_PATH" ]] && CHAPTERS="Prior seam chapter: $PREV_PATH
"
fi
for N in $(seq "$START_NUM" "$END_NUM"); do
  NN="$(printf '%02d' "$N")"
  CH="$(find "$BOOK/chapters" -maxdepth 1 -type f -name "ch${NN}-*.md" -print | head -1)"
  [[ -n "$CH" ]] || { echo "FATAL: no chapter ch${NN}-*.md" >&2; exit 1; }
  CHAPTERS="${CHAPTERS}Chapter ${NN}: ${CH}
"
done

mkdir -p "$BOOK/packets" "$BOOK/reader-reports" "$BOOK/reader-notes"
OUT="$BOOK/packets/batch-ch${START}-ch${END}-reader-${PERSONA}.md"
SUMMARY="$BOOK/reader-reports/batch-ch${START}-ch${END}-reader-${PERSONA}.md"
NOTES="$BOOK/reader-notes/${PERSONA}-notes.md"

{
  echo "# COLD READER MOVEMENT — persona $PERSONA — chapters $START–$END"
  echo "Read only the manuscript paths below and your own notes. Do not open any other book files."
  echo
  echo "MANUSCRIPT:"
  echo "$CHAPTERS"
  echo "ROLLING NOTES: $NOTES"
  echo "Write one chapter report per chapter to $BOOK/reader-reports/chNN-reader-${PERSONA}.md."
  echo "Write the movement summary to $SUMMARY and update $NOTES."
  echo
  echo "Assigned persona: $PERSONA."
  echo
  sed -n '1,$p' "$PROMPT_SRC"
} > "$OUT"

echo "READER_PACKET_COMPILED=$OUT"
echo "PERSONA=$PERSONA"
echo "MOVEMENT_REPORT=$SUMMARY"

#!/usr/bin/env bash
# Penname harness (fantasyau1.1) — compile a COLD READER packet (phase 5) for
# a chapter. No model is called here; the orchestrator dispatches the
# compiled packet to a clean-context Agent.
#
# Usage: harness/fantasyau1.1/reader-packet.sh <NN> <A|B>
#
# Writes <book>/packets/chNN-reader-A.md (or -B.md) from
# pennamecodexv3/pen-names/fantasyau1.1/seats/cold-reader-prompt.md with the
# persona and paths filled in. Creates <book>/reader-reports/ and
# <book>/reader-notes/ if they do not already exist, since the persona
# writes into both.
#
# Respects GB_BOOK_DIR, defaulting to Book 1 of Good Bones so an unset
# invocation behaves like the other fantasyau1.1 harness scripts.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: reader-packet.sh <NN> <A|B>

Compiles <book>/packets/chNN-reader-<A|B>.md from the fantasyau1.1
cold-reader prompt template, with {{A|B}}, {{book}}, and {{NN}} filled in.
Creates <book>/reader-reports/ and <book>/reader-notes/ if missing. Does not
call any model.

Environment:
  GB_BOOK_DIR   Book directory. Defaults to
                /Users/drive/good-bones/books/book-01-good-bones
                Example:
                  GB_BOOK_DIR=/Users/drive/good-bones/books/book-02-load-bearing \
                    harness/fantasyau1.1/reader-packet.sh 03 A
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

NN_RAW="${1:?usage: reader-packet.sh <NN> <A|B> (--help for details)}"
PERSONA_RAW="${2:?usage: reader-packet.sh <NN> <A|B> (--help for details)}"

if ! [[ "$NN_RAW" =~ ^[0-9]{1,2}$ ]]; then
  echo "FATAL: NN must be a one- or two-digit chapter number, got: $NN_RAW" >&2
  exit 1
fi
NN="$(printf "%02d" "$((10#$NN_RAW))")"

PERSONA="$(printf '%s' "$PERSONA_RAW" | tr '[:lower:]' '[:upper:]')"
if [[ "$PERSONA" != "A" && "$PERSONA" != "B" ]]; then
  echo "FATAL: persona must be A or B, got: $PERSONA_RAW" >&2
  exit 1
fi

BOOK="${GB_BOOK_DIR:-/Users/drive/good-bones/books/book-01-good-bones}"
SEATS_DIR="/Users/drive/penname/pennamecodexv3/pen-names/fantasyau1.1/seats"
PROMPT_SRC="$SEATS_DIR/cold-reader-prompt.md"

if [[ ! -f "$PROMPT_SRC" ]]; then
  echo "FATAL: missing required input: $PROMPT_SRC" >&2
  exit 1
fi
if [[ ! -d "$BOOK" ]]; then
  echo "FATAL: book directory does not exist: $BOOK" >&2
  exit 1
fi

CH="$(ls "$BOOK"/chapters/ch${NN}-*.md 2>/dev/null | head -1 || true)"
if [[ -z "$CH" ]]; then
  echo "FATAL: no chapter file matching ch${NN}-*.md in $BOOK/chapters" >&2
  exit 1
fi

mkdir -p "$BOOK/packets" "$BOOK/reader-reports" "$BOOK/reader-notes"

OUT="$BOOK/packets/ch${NN}-reader-${PERSONA}.md"

{
  echo "# COLD READER PACKET — persona ${PERSONA} — chapter ${NN}"
  echo "Phase 5 of the completion loop. Compiled $(date '+%Y-%m-%d %H:%M') by harness/reader-packet.sh. No canon, no cards -- manuscript only."
  echo
  PERSONA_LOWER="$(printf '%s' "$PERSONA" | tr '[:upper:]' '[:lower:]')"
  sed "s/{{A|B}}/${PERSONA}/g; s/{{persona}}/${PERSONA_LOWER}/g; s/{{book}}/${BOOK//\//\\/}/g; s/{{NN}}/${NN}/g" "$PROMPT_SRC"
} > "$OUT"

echo "READER_PACKET_COMPILED=$OUT"
echo "PERSONA=$PERSONA"
echo "REPORT_PATH=$BOOK/reader-reports/ch${NN}-reader-${PERSONA}.md"

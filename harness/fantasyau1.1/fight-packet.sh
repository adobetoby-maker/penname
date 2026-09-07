#!/usr/bin/env bash
# Penname harness (fantasyau1.1) — compile the FIGHT AUDITOR packet (phase 6)
# for a set-piece chapter. No model is called here; the orchestrator
# dispatches the compiled packet to a clean-context Agent.
#
# Usage: harness/fantasyau1.1/fight-packet.sh <NN>
#
# Writes <book>/packets/chNN-fight-audit-prompt.md from
# pennamecodexv3/pen-names/fantasyau1.1/seats/fight-audit-prompt.md, with
# {{book}}/{{NN}} filled in and a best-effort "open injuries at chapter
# start" list appended -- extracted by grepping the ledger's latest
# "Post-Chapter" entry for lines mentioning "injur", "shin", "wrist", "knee",
# "shoulder", or "strain". This list is a starting point, not a ruling: the
# orchestrator edits it before dispatch.
#
# Respects GB_BOOK_DIR, defaulting to Book 1 of Good Bones so an unset
# invocation behaves like the other fantasyau1.1 harness scripts.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: fight-packet.sh <NN>

Compiles <book>/packets/chNN-fight-audit-prompt.md from the fantasyau1.1
fight-audit prompt template, with {{book}} and {{NN}} filled in, plus a
best-effort open-injuries list grepped from the ledger's latest
"Post-Chapter" entry (lines matching injur|shin|wrist|knee|shoulder|strain,
case-insensitive). The orchestrator edits this list before dispatch -- it is
a starting point, not a ruling. Does not call any model.

Environment:
  GB_BOOK_DIR   Book directory. Defaults to
                /Users/drive/good-bones/books/book-01-good-bones
                Example:
                  GB_BOOK_DIR=/Users/drive/good-bones/books/book-02-load-bearing \
                    harness/fantasyau1.1/fight-packet.sh 08
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

NN_RAW="${1:?usage: fight-packet.sh <NN> (--help for details)}"
if ! [[ "$NN_RAW" =~ ^[0-9]{1,2}$ ]]; then
  echo "FATAL: NN must be a one- or two-digit chapter number, got: $NN_RAW" >&2
  exit 1
fi
NN="$(printf "%02d" "$((10#$NN_RAW))")"

BOOK="${GB_BOOK_DIR:-/Users/drive/good-bones/books/book-01-good-bones}"
SEATS_DIR="/Users/drive/penname/pennamecodexv3/pen-names/fantasyau1.1/seats"
PROMPT_SRC="$SEATS_DIR/fight-audit-prompt.md"
ARCH="$BOOK/CHAPTER_ARCHITECTURE.md"
LEDGER="$BOOK/STATE_LEDGER.md"

for f in "$PROMPT_SRC" "$ARCH" "$LEDGER"; do
  if [[ ! -f "$f" ]]; then
    echo "FATAL: missing required input: $f" >&2
    exit 1
  fi
done

CH="$(ls "$BOOK"/chapters/ch${NN}-*.md 2>/dev/null | head -1 || true)"
if [[ -z "$CH" ]]; then
  echo "FATAL: no chapter file matching ch${NN}-*.md in $BOOK/chapters" >&2
  exit 1
fi

mkdir -p "$BOOK/packets"
OUT="$BOOK/packets/ch${NN}-fight-audit-prompt.md"

# book name, from the architecture's H1 (matches compile-brief.sh)
BOOK_NAME="$(grep -m1 -E '^#[[:space:]]*CHAPTER ARCHITECTURE' "$ARCH" | sed -E 's/^#[[:space:]]*CHAPTER ARCHITECTURE[[:space:]]*[—-][[:space:]]*//')"
[[ -n "$BOOK_NAME" ]] || BOOK_NAME="$(basename "$BOOK")"

# Latest ledger entry: from the LAST "## Post-Chapter N" heading to the next
# "## " heading or end of file.
LAST_LINE="$(grep -n '^## Post-Chapter' "$LEDGER" | tail -1 | cut -d: -f1 || true)"
INJURY_LINES=""
if [[ -n "$LAST_LINE" ]]; then
  TOTAL_LINES="$(wc -l < "$LEDGER" | tr -d ' ')"
  SECTION="$(sed -n "$((LAST_LINE + 1)),\$p" "$LEDGER" | awk '/^## /{exit} {print}')"
  INJURY_LINES="$(printf '%s\n' "$SECTION" | grep -inE 'injur|shin|wrist|knee|shoulder|strain' || true)"
fi

{
  echo "# FIGHT AUDITOR PACKET — ${BOOK_NAME} — Chapter ${NN}"
  echo "Phase 6 of the completion loop. Compiled $(date '+%Y-%m-%d %H:%M') by harness/fight-packet.sh. Runs only on chapters the architecture schedules as set pieces."
  echo
  sed "s/{{book}}/${BOOK//\//\\/}/g; s/{{NN}}/${NN}/g" "$PROMPT_SRC"
  echo
  echo "---"
  echo
  echo "## Open injuries at chapter start (best-effort extraction — EDIT before dispatch)"
  echo "Grepped from the ledger's latest Post-Chapter entry for injur|shin|wrist|knee|shoulder|strain."
  echo "This is a starting point, not a ruling: confirm each against the full ledger and drop anything resolved."
  echo
  if [[ -n "$INJURY_LINES" ]]; then
    printf '%s\n' "$INJURY_LINES" | while IFS= read -r line; do
      echo "- $line"
    done
  else
    echo "- (none found by the grep — confirm manually; the ledger may record injuries with different wording)"
  fi
} > "$OUT"

echo "FIGHT_PACKET_COMPILED=$OUT"
echo "OPEN_INJURY_CANDIDATES=$(printf '%s\n' "$INJURY_LINES" | grep -c . || true)"

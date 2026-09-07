#!/usr/bin/env bash
# Penname harness (fantasyau1.1) — compile the CHAPTER BRIEF (phase 2) for a
# chapter. No model is called here; this only assembles what can be derived
# mechanically from files already on disk and leaves the rest as {{...}}
# placeholders for the orchestrator.
#
# Usage: harness/fantasyau1.1/compile-brief.sh <NN>
#
# Writes <book>/packets/chNN-brief.md from the template
# pennamecodexv3/pen-names/fantasyau1.1/seats/chapter-brief.template.md,
# filling mechanically: book, title, NN, date, the card text for chapter NN
# (verbatim from CHAPTER_ARCHITECTURE.md), the word target, the output
# filename slug, the previous chapter's filename, and the board delta (the
# ledger's last "Post-Chapter" entry, first 200 words). Everything the
# architecture and ledger do not mechanically encode -- the want line, the
# five floors, the five walls -- is left as {{...}} for the orchestrator.
#
# Respects GB_BOOK_DIR, defaulting to Book 1 of Good Bones so an unset
# invocation behaves like the other fantasyau1.1 harness scripts.
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: compile-brief.sh <NN>

Compiles <book>/packets/chNN-brief.md from the fantasyau1.1 chapter-brief
template.

Filled mechanically:
  - book, title, chapter number, compile date
  - the card text for chapter NN, verbatim from CHAPTER_ARCHITECTURE.md
  - the word target (parsed off the card's "Word target:" line)
  - the previous chapter's filename
  - the output filename's slug (kebab-cased from the title)
  - the board delta: the ledger's last "Post-Chapter" entry, first 200 words

Left as {{...}} for the orchestrator to fill (require judgment the
architecture/ledger files do not mechanically encode):
  - the want line
  - the five floors (hook, action floor, humor, plain statement, names)
  - the five walls
  - tic ceilings

Environment:
  GB_BOOK_DIR   Book directory. Defaults to
                /Users/drive/good-bones/books/book-01-good-bones
                Example:
                  GB_BOOK_DIR=/Users/drive/good-bones/books/book-02-load-bearing \
                    harness/fantasyau1.1/compile-brief.sh 02
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

NN_RAW="${1:?usage: compile-brief.sh <NN> (--help for details)}"
if ! [[ "$NN_RAW" =~ ^[0-9]{1,2}$ ]]; then
  echo "FATAL: NN must be a one- or two-digit chapter number, got: $NN_RAW" >&2
  exit 1
fi
NN="$(printf "%02d" "$((10#$NN_RAW))")"

BOOK="${GB_BOOK_DIR:-/Users/drive/good-bones/books/book-01-good-bones}"
SEATS_DIR="/Users/drive/penname/pennamecodexv3/pen-names/fantasyau1.1/seats"
TEMPLATE="$SEATS_DIR/chapter-brief.template.md"
ARCH="$BOOK/CHAPTER_ARCHITECTURE.md"
LEDGER="$BOOK/STATE_LEDGER.md"

for f in "$TEMPLATE" "$ARCH" "$LEDGER"; do
  if [[ ! -f "$f" ]]; then
    echo "FATAL: missing required input: $f" >&2
    exit 1
  fi
done

mkdir -p "$BOOK/packets"
OUT="$BOOK/packets/ch${NN}-brief.md"

PREV_NUM=$((10#$NN - 1))
PREV_NN=""
PREV_BASENAME=""
if [[ "$PREV_NUM" -ge 1 ]]; then
  PREV_NN="$(printf "%02d" "$PREV_NUM")"
  PREV_PATH="$(ls "$BOOK"/chapters/ch${PREV_NN}-*.md 2>/dev/null | head -1 || true)"
  [[ -n "$PREV_PATH" ]] && PREV_BASENAME="$(basename "$PREV_PATH")"
fi

DATE="$(date '+%Y-%m-%d')"

# All templating logic lives in this python3 helper (stdlib only) rather than
# fragile multi-line sed, since {{card}} and {{ledger_delta}} substitute in
# whole paragraphs of extracted text.
python3 - "$TEMPLATE" "$ARCH" "$LEDGER" "$OUT" "$NN" "$PREV_NN" "$PREV_BASENAME" "$DATE" <<'PYEOF'
import re
import sys

template_path, arch_path, ledger_path, out_path, nn, prev_nn, prev_basename, date = sys.argv[1:9]
nn_int = str(int(nn))

template = open(template_path, encoding="utf-8").read()
arch = open(arch_path, encoding="utf-8").read()
ledger = open(ledger_path, encoding="utf-8").read()

# --- book name, from the architecture's H1: "# CHAPTER ARCHITECTURE — Book 2: Load-Bearing"
m = re.search(r"^#\s*CHAPTER ARCHITECTURE\s*[—-]\s*(.+?)\s*$", arch, re.MULTILINE)
if not m:
    print(f"FATAL: could not find a '# CHAPTER ARCHITECTURE — <book>' heading in {arch_path}", file=sys.stderr)
    sys.exit(1)
book = m.group(1).strip()

# --- this chapter's card block: from "**Chapter N — Title**" to the next
# line that is exactly "---" (or end of file if the last chapter has none).
card_re = re.compile(
    r"\*\*Chapter\s+" + re.escape(nn_int) + r"\s*[—-]\s*(.+?)\*\*\n(.*?)(?:\n---\s*\n|\Z)",
    re.DOTALL,
)
m = re.search(card_re, arch)
if not m:
    print(f"FATAL: no '**Chapter {nn_int} — <title>**' card found in {arch_path}", file=sys.stderr)
    sys.exit(1)
title = m.group(1).strip()
card_body = m.group(2).strip()
card_full = f"**Chapter {nn_int} — {title}**\n{card_body}"

# --- word target, from the card's own "*Word target: N*" line
tm = re.search(r"Word target:\s*([\d,]+)", card_body)
target = tm.group(1).strip() if tm else "{{target}}"

# --- slug: kebab-case the title
slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
if not slug:
    slug = "chapter"

# --- board delta: the LAST "## Post-Chapter N" entry, first 200 words of
# its body (everything after the heading line, up to the next "## " heading
# or end of file).
headings = list(re.finditer(r"^##\s*Post-Chapter\s+(\d+).*$", ledger, re.MULTILINE))
if not headings:
    print(f"FATAL: no '## Post-Chapter N' entries found in {ledger_path}", file=sys.stderr)
    sys.exit(1)
last = headings[-1]
body_start = last.end()
next_heading = re.search(r"^##\s", ledger[body_start:], re.MULTILINE)
body_end = body_start + next_heading.start() if next_heading else len(ledger)
delta_body = ledger[body_start:body_end].strip()
words = delta_body.split()
delta_200 = " ".join(words[:200])
if len(words) > 200:
    delta_200 += " …"

out = template

# Simple literal placeholders (safe to blanket-replace: their meaning is
# the same at every occurrence in this template).
out = out.replace("{{book}}", book)
out = out.replace("{{title}}", title)
out = out.replace("{{NN}}", nn)
out = out.replace("{{date}}", date)
out = out.replace("{{slug}}", slug)
out = out.replace("{{target}}", target)

# {{NN-1}} / the previous-chapter Load line: chapter 1 has no previous
# chapter, so replace the whole bullet rather than leave a malformed path.
if prev_nn:
    out = out.replace("{{NN-1}}", prev_nn)
else:
    out = re.sub(
        r"^\d+\.\s*`chapters/ch\{\{NN-1\}\}-\*\.md`.*$",
        "3. N/A — this is the book's first chapter; there is no previous chapter to load.",
        out,
        flags=re.MULTILINE,
    )

# {{ledger_delta — ...}} — replace the full brace span (it carries its own
# instructional text inside the braces) with the extracted board delta.
out = re.sub(r"\{\{ledger_delta[^}]*\}\}", delta_200.replace("\\", "\\\\"), out, count=1)

# {{card}} — verbatim card block from the architecture.
out = out.replace("{{card}}", card_full.replace("\\", "\\\\"), 1)

open(out_path, "w", encoding="utf-8").write(out)

remaining = len(re.findall(r"\{\{[a-zA-Z_]", out))
print(f"BRIEF_COMPILED={out_path}")
print(f"book={book!r} title={title!r} target={target} prev_chapter={prev_basename or 'N/A'}")
print(f"placeholders_remaining_for_orchestrator={remaining}")
PYEOF

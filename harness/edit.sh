#!/usr/bin/env bash
# penname harness — single-chapter exception editor (codex on the ChatGPT plan; Opus fallback).
# Genre-aware: loads the correct charter (fantasy vs sci-fi) instead of assuming one.
#
# Usage: harness/edit.sh <book-dir> <chapter-file> <fantasy|scifi> [--recheck]
#
# Modeled directly on good-bones/harness/edit.sh (2026-09-04) — same billing
# guard, same env-strip, same opus-fallback escape valve — generalized to any
# docked book instead of one hardcoded series.

set -euo pipefail

BOOK_DIR="${1:?usage: edit.sh <book-dir> <chapter-file> <fantasy|scifi> [--recheck]}"
CHAPTER="${2:?usage: edit.sh <book-dir> <chapter-file> <fantasy|scifi> [--recheck]}"
GENRE="${3:?usage: edit.sh <book-dir> <chapter-file> <fantasy|scifi> [--recheck]}"
MODE="${4:-}"

case "$GENRE" in
  fantasy) CHARTER=/Users/drive/penname/craft/THE_AUTHOR.md ;;
  scifi)   CHARTER=/Users/drive/penname/craft/THE_SCIFI_AUTHOR.md ;;
  *) echo "FATAL: genre must be 'fantasy' or 'scifi', got '$GENRE'" >&2; exit 1 ;;
esac

[[ -f "$CHAPTER" ]] || { echo "FATAL: chapter file not found: $CHAPTER" >&2; exit 1; }
[[ -f "$CHARTER" ]] || { echo "FATAL: charter not found: $CHARTER" >&2; exit 1; }

CH_BASENAME="$(basename "$CHAPTER" .md)"
VERDICT_DIR="$BOOK_DIR/editor-verdicts"
mkdir -p "$VERDICT_DIR"

if [[ "$MODE" == "--recheck" ]]; then
  VERDICT="$VERDICT_DIR/${CH_BASENAME}-verdict-recheck.md"
  PRIOR="$VERDICT_DIR/${CH_BASENAME}-verdict.md"
  EXTRA="This is a RECHECK after repair. The prior verdict and the repair log are
evidence. Confirm each prior finding is genuinely resolved. Do NOT introduce new
stylistic preferences at recheck — only confirm resolution, or report that a prior
finding survives. A recheck that invents fresh taste notes is a failed recheck."
else
  VERDICT="$VERDICT_DIR/${CH_BASENAME}-verdict.md"
  PRIOR="(none — first pass)"
  EXTRA=""
fi

REPORT="$BOOK_DIR/author-reports/${CH_BASENAME}-report.md"
[[ -f "$REPORT" ]] || REPORT="(no author report found at expected path — note this as a finding, do not invent its content)"

read -r -d '' PROMPT <<PROMPTEOF || true
You are the Editor seat of the penname harness. You are a different model
family from the author (Fable/Claude) by design — that is the point of this
seat. You do not trust the author's self-report. You read the chapter yourself.

ASSUMPTION: the draft is broken until the text proves otherwise.

$EXTRA

## Evidence (read all of it before forming any verdict)

- Charter (the law, genre: $GENRE): $CHARTER
- Universe bible: $BOOK_DIR/UNIVERSE_BIBLE.md (or canon/UNIVERSE_BIBLE.md)
- Arc document: $BOOK_DIR/ARC.md (or series/*.md)
- State ledger: $BOOK_DIR/STATE_LEDGER.md
- Name registry: $BOOK_DIR/NAME_REGISTRY.md
- Chapter card: $BOOK_DIR/CHAPTER_ARCHITECTURE.md (find this chapter's card)
- Author report: $REPORT
- Prior verdict (if this is a recheck): $PRIOR
- THE DRAFT: $CHAPTER

## What to check

Run every gate applicable to this genre's charter (32 gates if fantasy per
THE_AUTHOR.md §9; 21 gates if sci-fi per THE_SCIFI_AUTHOR.md §8). At minimum:

1. CARD FIDELITY — did the chapter deliver what its card promised? Word target
   respected (more than 15% over must justify the overage with function, not
   description)?
2. CHARTER COMPLIANCE — run the genre's binary gates against the draft.
3. CANON — any contradiction with the universe bible is a BLOCKER, not a note.
4. STATE LEDGER — is every character's state consistent with the ledger at this
   point in the book? Any knowledge the POV could not yet have?
5. TIC CENSUS — count per 1,000 words against the charter's hard caps.
6. NAME COLLISIONS — any new name against the registry, checked by ear.
7. VOICE-DILUTION — do secondary characters speak in the protagonist's
   register? This is a documented failure mode — flag it if present.
8. FANTASY PULL — for fantasy, run §10 gates 28–32: opening pressure,
   action/progression cadence against adjacent cards, humor distribution,
   cold-reader continuity if reports exist, and dialogue ownership.
9. SCIENCE-FICTION PULL — for science fiction, run gates 17–21: opening
   pressure; problem/action cadence; scheduled scale and sustain; rolling humor
   and warmth; cold-reader continuity; and substantive dialogue ownership.

## Report format

Write EXACTLY this structure to $VERDICT and nothing else to stdout but the
verdict line.

---
VERDICT: [PASS | PASS_WITH_FINDINGS | STRUCTURAL_HOLD]

CARD FIDELITY: [PASS | FAIL — one paragraph]

TIC CENSUS:
| Tic | Count | Per 1000w |
|---|---|---|

DEFECTS — numbered. Each MUST carry: severity (LOW|MEDIUM|HIGH|BLOCKER),
location (line number or exact quoted phrase), the evidence, and the reader
consequence. A finding without a located quote is not a finding.
1. ...

CONCERNS (2-3 sentences):

STRENGTHS (2-3 sentences — these are protected from repair):

RECOMMENDATION FOR AUTHOR:
[What must change before the chapter closes. Be specific and bounded.]
---

Severity rules: BLOCKER = canon contradiction or missing promised scene
function. HIGH = charter gate violation or card infidelity. MEDIUM = craft
defect with real reader consequence. LOW = polish. Do not inflate severity to
seem rigorous, and do not deflate it to seem agreeable.

After writing the file, print one line to stdout: VERDICT=<verdict>
PROMPTEOF

# ── ESCAPE VALVE: interim Opus editor (no codex call at all) ─────────────────
# PENNAME_EDITOR=opus compiles the identical prompt to a file and exits 0
# WITHOUT invoking codex. The orchestrator then dispatches it to
# Agent(model:"opus") and the verdict is written to the same $VERDICT path.
# Default (unset or "codex") runs codex on the ChatGPT plan, guarded below.
if [[ "${PENNAME_EDITOR:-codex}" == "opus" ]]; then
  PROMPT_OUT="$BOOK_DIR/packets/${CH_BASENAME}-editor-prompt${MODE:+-recheck}.md"
  mkdir -p "$BOOK_DIR/packets"
  {
    echo "# EDITOR PROMPT — compiled by harness/edit.sh for PENNAME_EDITOR=opus — $(date '+%Y-%m-%d %H:%M')"
    echo "# Seat: Claude Opus (cross-model within family; GPT seat not used this run). Verdict path: $VERDICT"
    echo
    echo "$PROMPT"
  } > "$PROMPT_OUT"
  echo "EDITOR_PROMPT_COMPILED=$PROMPT_OUT"
  echo "VERDICT_PATH=$VERDICT"
  exit 0
fi

# ── BILLING GUARD — never let this seat bill the OpenAI API ─────────────────
# Two ways codex can fall onto API billing: (1) not logged in via ChatGPT, in
# which case codex falls back to OPENAI_API_KEY if present in the environment;
# (2) OPENAI_API_KEY present even when logged in (Infisical injects it into
# ATLAS-derived sessions). Refuse on (1) unless explicitly overridden; strip
# (2) from codex's environment unconditionally regardless of login state.
if ! codex login status &>/dev/null; then
  echo "REFUSING TO RUN: codex is not logged in via ChatGPT (bills the OpenAI API on OPENAI_API_KEY if present)." >&2
  echo "Fix (one command, interactive): codex login   → choose 'Sign in with ChatGPT'" >&2
  echo "Then re-run this script. Meanwhile: PENNAME_EDITOR=opus harness/edit.sh ..." >&2
  echo "Override for a deliberate API run: PENNAME_ALLOW_API_BILLING=1" >&2
  [[ "${PENNAME_ALLOW_API_BILLING:-}" == "1" ]] || exit 3
fi

env -u OPENAI_API_KEY codex exec "$PROMPT" > "/tmp/penname-edit-$$.log" 2>&1 || {
  echo "EDITOR_FAILED — see /tmp/penname-edit-$$.log" >&2
  exit 1
}

if [[ -f "$VERDICT" ]]; then
  echo "--- $(basename "$VERDICT") ---"
  grep -m1 "^VERDICT:" "$VERDICT" || echo "VERDICT: (unparsed)"
  echo "defects: $(grep -cE '^[0-9]+\. ' "$VERDICT" || echo 0)"
else
  echo "WARN: no verdict file written; tail of log:" >&2
  tail -20 "/tmp/penname-edit-$$.log" >&2
  exit 1
fi

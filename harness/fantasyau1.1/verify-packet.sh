#!/usr/bin/env bash
# Penname harness — compile the VERIFIER packet (phase 5) for a chapter.
# Usage: GB_BOOK_DIR=/path/to/book harness/verify-packet.sh <NN> "<Chapter Title>" "<chronology line>"
# Writes $BOOK/packets/chNN-verifier-prompt.md and prints its path. The orchestrator
# then dispatches Agent(model:"sonnet") pointing at that file. No model is called here.
set -euo pipefail
NN="${1:?usage: verify-packet.sh <NN> \"<Title>\" \"<chronology line>\"}"
TITLE="${2:?chapter title required}"
CHRONO="${3:-No precise day-count claims expected; confirm every interval on the page is arithmetically consistent with the ledger.}"
BOOK="${GB_BOOK_DIR:-/Users/drive/good-bones/books/book-02-load-bearing}"
CH="$(ls "$BOOK"/chapters/ch${NN}-*.md 2>/dev/null | head -1)"
[[ -n "$CH" ]] || { echo "FATAL: no chapter file ch${NN}-*.md" >&2; exit 1; }
PREV=$(printf "%02d" $((10#$NN - 1)))
PREVCH="$(ls "$BOOK"/chapters/ch${PREV}-*.md 2>/dev/null | head -1 || true)"
[[ -n "$PREVCH" ]] || PREVCH="/Users/drive/good-bones/books/book-01-good-bones/chapters/ch20-the-first-job.md"
OUT="$BOOK/packets/ch${NN}-verifier-prompt.md"
mkdir -p "$BOOK/packets"
cat > "$OUT" <<EOF
# VERIFIER PACKET — Good Bones Book 2, Chapter ${NN} "${TITLE}"
Phase 5 of the completion loop. Seat: sonnet, independent of author and editor. Compiled $(date '+%Y-%m-%d %H:%M') by harness/verify-packet.sh.

You are the VERIFIER seat. You are independent of both the author (Fable) and the
editor (Opus, interim; or gpt-5.6-sol when the GPT seat is restored). You do not trust
either. You verify every proposed finding in the editor's verdict against the frozen
evidence, and you hold the editor to its own prior rulings and to the charter.
Verification cuts both ways: a finding may be REJECTED (taste presented as defect; cites
no charter/canon provision; contradicts a protected strength, a prior ruling, or a fact
you can disprove by grep), DOWNGRADED or UPGRADED in severity, or CONFIRMED. You may
report a finding the editor MISSED only if it is a BLOCKER-class canon or firewall breach.

## Evidence (read all of it)
- Charter: /Users/drive/penname/craft/THE_AUTHOR.md
- Canon: /Users/drive/good-bones/canon/UNIVERSE_BIBLE.md (entire; every Book 2 section at the end is binding, including any ruling dated after the editor's verdict — such rulings may resolve or reframe a finding)
- Ledger: ${BOOK}/STATE_LEDGER.md (through the previous chapter)
- Registry: ${BOOK}/NAME_REGISTRY.md
- Architecture (this chapter's card, the mechanism firewall, Protected motifs, standing rules): ${BOOK}/CHAPTER_ARCHITECTURE.md
- Loop state (standing rules 1–12, Fairness precedent, prior verifier precedents): ${BOOK}/LOOP_STATE.md
- Author report: ${BOOK}/author-reports/ch${NN}-report.md
- EDITOR VERDICT: ${BOOK}/editor-verdicts/ch${NN}-verdict.md
- THE DRAFT: ${CH}
- Previous chapter, for voice/state continuity: ${PREVCH}

## Method
For EACH numbered defect in the verdict:
1. Locate the quoted text in the draft (line number). Quote not in the draft → REJECTED as unlocated.
2. Reproduce the editor's evidence yourself — grep/wc for every count, reading for canon and rule-10 claims. Do not accept the editor's arithmetic or its premises; grep the files it makes claims about.
3. Test against: the specific charter section or canon rule cited (none cited and none applies → taste → REJECT); any post-verdict ruling in the Bible or architecture; the author report's protected strengths and stated deviations; Book 1 and Book 2 verifier precedents in LOOP_STATE.
4. Verdict per finding: CONFIRMED (severity as given) | CONFIRMED-DOWNGRADED to X | CONFIRMED-UPGRADED to X | REJECTED — one evidence paragraph each.
Then run the orchestrator's checks regardless of what the editor found:
- Mechanism firewall grep on the draft: resonance|substrate|permanent|calibrat|lineage|selected|chosen|directed|Welby|Keld|Hollow — report counts; justify any nonzero against the chapter's card (Welby/Keld are page-gated to Ch5/Ch7 and later).
- "central": must never be defined or located before Ch12.
- "Mark" (capital): must match the card (zero unless the card schedules Mark activity).
- Close-POV: any sentence reporting another character's interior state is a defect (Ch2 precedent).
- Rule 10 spot-check: the five most confident declarative sentences where Dale concludes something about this world — was each page-earned?
- Chronology: ${CHRONO}

## Output
Write to: ${BOOK}/editor-verdicts/ch${NN}-verification.md
Structure:
---
VERIFICATION: [n findings reviewed; c CONFIRMED, d DOWNGRADED, u UPGRADED, r REJECTED; m MISSED-BLOCKERS added]
Per finding: number, editor severity → verified severity, location, evidence paragraph, repair instruction if CONFIRMED (bounded: what to change and what must not change).
Orchestrator checks: firewall counts; central; Mark; close-POV; rule-10 spot-check; chronology table.
REPAIR PACKET: the CONFIRMED findings only, ordered by severity, each with a bounded instruction, plus the protected strengths that must survive (from the verdict's STRENGTHS section and the architecture's Protected motifs).
RECOMMENDATION: CLOSE (no verified BLOCKER/HIGH and no MEDIUM worth a cycle) | REPAIR (list) | BLOCKED (why)
---
Write nothing else anywhere; do not edit the draft.
Final message: the VERIFICATION headline line and the RECOMMENDATION only.
EOF
echo "$OUT"

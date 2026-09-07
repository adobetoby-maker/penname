# fantasyau1.1 harness

Scripts for the bounded book-completion loop defined in
`pennamecodexv3/workflows/completion-loop-1.1.md`. None of them call a model
except `edit.sh` (guarded, ChatGPT-plan OAuth only) — the others compile
packets/prompts and do bookkeeping for the orchestrator to dispatch by hand
(`Agent(model:"...")`). All are `bash 3.2` compatible, take `-h`/`--help`,
and exit non-zero with a clear message on missing inputs. All respect
`GB_BOOK_DIR` (default: `/Users/drive/good-bones/books/book-01-good-bones`).

| Script | Loop phase | Inputs | Output |
|---|---|---|---|
| `compile-brief.sh NN` | 2. Brief | `CHAPTER_ARCHITECTURE.md`, `STATE_LEDGER.md`, `chapter-brief.template.md` | `$BOOK/packets/chNN-brief.md` — book/title/NN/date, the card, the word target, the previous chapter's filename, and the board delta (last ledger entry, 200 words) filled in; want/floors/walls left as `{{...}}` for the orchestrator |
| `edit.sh NN [--recheck]` | 4. Editor | `editor-prompt-1.1.md`, `variance.py`, the chapter, brief, report, canon | `$BOOK/editor-verdicts/chNN-verdict[-recheck].md` — two-track verdict (DEFECTS + PULL); stdout prints the verdict line, defects count, and pull-findings count. `GB_EDITOR=opus` compiles the prompt to a file instead of calling codex |
| `reader-packet.sh NN A\|B` | 5. Readers | `cold-reader-prompt.md` | `$BOOK/packets/chNN-reader-<A\|B>.md`; creates `reader-reports/` and `reader-notes/` |
| `fight-packet.sh NN` | 6. Fight audit | `fight-audit-prompt.md`, `STATE_LEDGER.md` | `$BOOK/packets/chNN-fight-audit-prompt.md`, with a best-effort open-injuries list grepped from the ledger's latest entry (`injur\|shin\|wrist\|knee\|shoulder\|strain`) appended for the orchestrator to edit |
| `verify-packet.sh NN "Title" "chrono"` | 7. Verify | (pre-existing, unchanged) | `$BOOK/packets/chNN-verifier-prompt.md` |

Not model-dispatching scripts, but part of the same phase-9 reporting step
("progress.json updated ... dashboard re-rendered"):

| Script | Loop phase | Purpose |
|---|---|---|
| `../../pennamecodexv3/scripts/fantasyau1.1/variance.py <chapter.md>` | 4 (attached to the editor prompt) | Narration-only sentence-variance JSON: histogram, 120-word windows missing a short sentence, chained-sentence runs, `" for "` conjunctions, define-by-negation count, em dashes |
| `../../pennamecodexv3/scripts/fantasyau1.1/progress.py` | 9. Close and report | `init` / `update` / `rollup` / `render` — see that file's docstring; fills `progress.json` from filed seat reports only (never invents a figure) and renders the self-contained HTML dashboard |

## Typical order for one chapter (NN)

```bash
export GB_BOOK_DIR=/Users/drive/good-bones/books/book-02-load-bearing

harness/fantasyau1.1/compile-brief.sh 03                 # phase 2 — orchestrator fills want/floors/walls, dispatches the author
# ... author drafts chapters/ch03-*.md + author-reports/ch03-report.md ...
harness/fantasyau1.1/edit.sh 03                            # phase 4 — editor-verdicts/ch03-verdict.md
harness/fantasyau1.1/reader-packet.sh 03 A                 # phase 5 — dispatch to a clean-context Agent
harness/fantasyau1.1/reader-packet.sh 03 B
harness/fantasyau1.1/fight-packet.sh 03                    # phase 6, set-piece chapters only
# ... verifier writes editor-verdicts/ch03-verification.md; repairs run; edit.sh 03 --recheck ...
python3 pennamecodexv3/scripts/fantasyau1.1/progress.py update "$GB_BOOK_DIR" 3   # phase 9
python3 pennamecodexv3/scripts/fantasyau1.1/progress.py render "$GB_BOOK_DIR" --out "$GB_BOOK_DIR/progress.html"
```

## Parser limitations (defensive, not exhaustive)

`progress.py update` and `edit.sh`'s two-track summary parse real filed text,
not a fixed grammar, so a few shapes are known to fall through to a null
field rather than a wrong figure:

- A chapter whose verification was an "orchestrator adjudication (no
  verifier seat dispatched)" note, not the standard verify-packet.sh output,
  has no CONFIRMED/DOWNGRADED/REJECTED counts to parse — `verifier` stays
  absent for that chapter (seen in Book 2's Ch19–20 fixture).
- `author.words`/`target` try four phrasings in order ("N words against a
  target of M", "M (filed) ... Delta vs T", "Word count: N by wc -w ...
  Delta vs T", "After: N ... band of A–B" with T derived as the band's
  midpoint); a fifth report shape would need a fifth pattern added.
- `humor_beats_claimed`, `action_item`, `cold`, `hook_line`, `want_line`,
  and `variance_breaches` are 1.1-brief concepts with no equivalent field in
  1.0-format author reports — they are simply absent on a 1.0 fixture, not
  a parser failure.
- `fight` parsing (gates table, new injuries, terrain beats, fairness) is
  implemented against the `fight-audit-prompt.md` output contract but has
  no real filed example in the Book 2 fixture to test against (no chapter
  there has a fight-audit file).

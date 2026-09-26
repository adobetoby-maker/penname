# fantasyau1.1 harness

Scripts for the movement-based book-completion loop defined in
`pennamecodexv3/workflows/completion-loop-1.1.md`. None of them call a model
except `edit.sh` and `edit-batch.sh` (guarded, ChatGPT-plan OAuth only) — the others compile
packets/prompts and do bookkeeping for the orchestrator to dispatch by hand
(`Agent(model:"...")`). All are `bash 3.2` compatible, take `-h`/`--help`,
and exit non-zero with a clear message on missing inputs. All respect
`GB_BOOK_DIR` (default: `/Users/drive/good-bones/books/book-01-good-bones`).

| Script | Loop phase | Inputs | Output |
|---|---|---|---|
| `compile-brief.sh NN` | 2. Brief | `CHAPTER_ARCHITECTURE.md`, `STATE_LEDGER.md`, `chapter-brief.template.md` | `$BOOK/packets/chNN-brief.md` — book/title/NN/date, the card, the word target, the previous chapter's filename, and the board delta (last ledger entry, 200 words) filled in; want/floors/walls left as `{{...}}` for the orchestrator |
| `edit-batch.sh START END [--recheck]` | 4. Batch editor | movement chapters, briefs, reports, `batch-editor-prompt.md`, `variance.py`, canon | `$BOOK/editor-verdicts/batch-chSTART-chEND-verdict[-recheck].md` — DEFECTS + PULL + SEAMS. `GB_EDITOR=opus` compiles the prompt without calling Codex |
| `reader-batch-packet.sh START END A\|B` | 5. Readers | `cold-reader-batch-prompt.md`, manuscript paths, reader's own notes | one report per chapter plus `$BOOK/reader-reports/batch-chSTART-chEND-reader-<A\|B>.md` |
| `edit.sh NN [--recheck]` | Exception editor | one high-risk chapter | Single-chapter two-track verdict; use for a major canon ruling or when continued drafting is unsafe |
| `reader-packet.sh NN A\|B` | Exception reader | one chapter | Single-chapter reader packet for a specifically flagged chapter |
| `fight-packet.sh NN` | 6. Fight audit | `fight-audit-prompt.md`, `STATE_LEDGER.md` | `$BOOK/packets/chNN-fight-audit-prompt.md`, with a best-effort open-injuries list grepped from the ledger's latest entry (`injur\|shin\|wrist\|knee\|shoulder\|strain`) appended for the orchestrator to edit |
| `verify-packet.sh NN "Title" "chrono"` | 7. Verify | (pre-existing, unchanged) | `$BOOK/packets/chNN-verifier-prompt.md` |

Not model-dispatching scripts, but part of the same phase-9 reporting step
("progress.json updated ... dashboard re-rendered"):

| Script | Loop phase | Purpose |
|---|---|---|
| `../../pennamecodexv3/scripts/fantasyau1.1/variance.py <chapter.md>` | 4 (attached to the editor prompt) | Narration-only sentence-variance JSON: histogram, 120-word windows missing a short sentence, chained-sentence runs, `" for "` conjunctions, define-by-negation count, em dashes |
| `../../pennamecodexv3/scripts/fantasyau1.1/progress.py` | 9. Close and report | `init` / `update` / `rollup` / `render` — see that file's docstring; fills `progress.json` from filed seat reports only (never invents a figure) and renders the self-contained HTML dashboard |

## Typical order for one four-chapter movement

```bash
export GB_BOOK_DIR=/Users/drive/good-bones/books/book-02-load-bearing

harness/fantasyau1.1/compile-brief.sh 01
harness/fantasyau1.1/compile-brief.sh 02
harness/fantasyau1.1/compile-brief.sh 03
harness/fantasyau1.1/compile-brief.sh 04
# ... Fable drafts chapters 01–04 forward in one session with light closes ...
harness/fantasyau1.1/edit-batch.sh 01 04
harness/fantasyau1.1/reader-batch-packet.sh 01 04 A
harness/fantasyau1.1/reader-batch-packet.sh 01 04 B       # opening/act-end/final or flagged movement
harness/fantasyau1.1/fight-packet.sh 03                  # only if chapter 03 is a set piece
# ... selectively verify serious/disputed findings; repair once across the movement ...
harness/fantasyau1.1/edit-batch.sh 01 04 --recheck
python3 pennamecodexv3/scripts/fantasyau1.1/progress.py update "$GB_BOOK_DIR" 1
python3 pennamecodexv3/scripts/fantasyau1.1/progress.py update "$GB_BOOK_DIR" 2
python3 pennamecodexv3/scripts/fantasyau1.1/progress.py update "$GB_BOOK_DIR" 3
python3 pennamecodexv3/scripts/fantasyau1.1/progress.py update "$GB_BOOK_DIR" 4
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
- `humor_beats_claimed` and `variance_breaches` remain legacy fields for early
  1.1 reports. In 1.1.1, humor and sentence distribution come from the editor/
  measurement pass; absent author values are intentional, not parser failures.
- `fight` parsing (gates table, new injuries, terrain beats, fairness) is
  implemented against the `fight-audit-prompt.md` output contract but has
  no real filed example in the Book 2 fixture to test against (no chapter
  there has a fight-audit file).

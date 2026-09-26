---
name: booknarrator
version: 1.2.5
description: |
  Monroe Book Narrator. Reads the book arc, prepares rolling three-chapter
  narration runs, tests paragraph clarity, directs Holden or Jason, renders,
  listens, and loops exact repairs back to Writing Monroe.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
triggers:
  - /book-narrator
  - Monroe Book Narrator
  - narrate this book with Holden
  - narrate this book with Jason
---

# Monroe Book Narrator 1.2.5

Read `/Users/drive/penname/pennamecodexv3/workflows/book-narrator-1.2.5.md`
completely, then initialize the requested three-chapter run with:

```bash
/Users/drive/penname/harness/book-narrator.sh VOICE BOOK_ROOT CHAPTERS
```

Read the generated `book-narrator.prompt.md` and execute it. Use `Holden` or
`Jason`; never infer a different production voice. If the user omits chapters,
start with `1-3`. If the book location is ambiguous, locate the canonical
chapter files before creating the run.

Do not turn wording changes into narration-only markup. Punctuation work must preserve
the exact word sequence. When context establishes the intended meaning, correct misplaced
punctuation even if the repair materially changes the reading. Reserve a performance
choice and A/B owner decision for genuinely unresolved interpretations. Return meaning-level
problems to Writing Monroe and rerun the changed paragraph plus both joins.

Do not call a take complete because the requested speed was accepted. Measure
the resulting delivery against the selected approved-master coach. Never repair
delivery by time-stretching a finished file.

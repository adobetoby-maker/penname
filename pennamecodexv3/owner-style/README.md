# Monroe owner-style memory

This directory holds the approved owner layer and derived evidence used by Monroe
Jackson 1.2.0.

- `OWNER_VOICE.md` is the short, owner-approved behavioral layer compiled into
  movement prompts.
- `edits.jsonl` is the append-only raw event archive created by
  `scripts/owner_style.py ingest`.
- `events/` contains one canonical JSON file per event.
- `examples/all.jsonl` is a rebuildable view of currently active voice examples.
- `examples/shared.jsonl`, `fantasy.jsonl`, and `science-fiction.jsonl` are
  rebuildable scope views.
- `protections.jsonl` is the current set of locked passages for repair compilers.
- `queues/` separates canon, mechanical, local, pending-revision, and conflict
  work from prose-style learning.
- `candidates/` receives reviewable voice-profile candidates. Candidate generation
  never overwrites `OWNER_VOICE.md`.

Raw events are evidence. Derived example files may be rebuilt at any time. The
approved voice document changes only through deliberate review.

Typical loop:

```bash
python3 -B pennamecodexv3/scripts/owner_style.py ingest pwa-export.jsonl
python3 -B pennamecodexv3/scripts/owner_style.py status
python3 -B pennamecodexv3/scripts/owner_style.py distill-prompt \
  --output pennamecodexv3/owner-style/candidates/distill.prompt.md
```

Give the compiled prompt to the voice-librarian model. Review its returned
`OWNER_VOICE.md` candidate before replacing the approved profile.

## Automatic intake

The Boundary Universe PWA mirrors immutable evidence to
`edits/events/<book>/<chapter>/<eventId>.json` on its application repository.
The trainer can fetch that Git ref, translate the deployed flat event shape,
ingest only unseen IDs, and save its source commit as a cursor:

```bash
harness/monroe-trainer.sh sync
```

When new voice examples arrive, sync also refreshes
`candidates/distill.prompt.md`. It does not replace `OWNER_VOICE.md`. The local
LaunchAgent installed by `harness/install-monroe-watch.sh` runs this sync once an
hour. Cursor state lives under `owner-style/sync/` and is intentionally not
committed.

An explicit PWA **Send to Monroe** event uses `eventType: voice_example`. It may
carry either an original/revised pair or the same text in both fields for a
passage the owner likes unchanged. Explicit examples are labeled and ranked
above inferred correction pairs. If `requestEventId` names the direct edit being
endorsed, selectors use the explicit event instead of duplicating both.

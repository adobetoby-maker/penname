# Monroe Jackson 1.3.0 cloud environment

This repository contains the Monroe Jackson 1.3.0 author harness. In Codex Cloud,
work from the repository root and use repository-relative paths. Do not rely on
`/Users/drive/penname`, iTerm, AppleScript, LaunchAgents, or other macOS-only
launchers.

## Canonical seat

- Public byline: Monroe Jackson.
- Default seat: Monroe Jackson 1.3.0 Light.
- Progression-adventure seat: O'Connor 1.3.0.
- Read `pennamecodexv3/skills/oconnor/SKILL.md` before O'Connor work, followed by
  the files that skill requires.
- The private source-book transcript is local research and must never be copied,
  committed, uploaded, or used as drafting text.

## Roles and model integrity

Codex coordinates, compiles prompts, checks continuity, runs tests, and maintains
maps. Claude Opus 5.5 is the default prose author. Fable is used only when the
owner explicitly names it. Never silently substitute Codex or another model for
the requested manuscript author.

The cloud environment does not inherit the Mac's Claude subscription login. If
the requested author runtime is unavailable, compile and save the prompt, record
the blocker, and stop before drafting. Do not switch to a paid Anthropic API or
request/store an API key unless the owner explicitly chooses that route.

## Portable commands

Run the O'Connor compiler from the repository root:

```bash
bash harness/oconnor.sh formula --output /tmp/monroe-oconnor-formula.md
bash harness/oconnor.sh plan --root ../kindling --author opus --idea-file ../kindling/IDEA.md
bash harness/oconnor.sh movement --root ../kindling --author opus \
  --packet packets/MOVEMENT-001.md --start 1 --count 8
```

The compiler creates prompts and never invokes a model. For Monroe Light, invoke
`python3 -B pennamecodexv3/scripts/build_movement_prompt.py` directly rather than
the macOS launcher.

## Writing loop

- Draft six or more contiguous chapters per creative movement; eight is the
  default and there is no upper cap.
- Do not add chapter-by-chapter editorial gates.
- After a full movement, run continuity/story plus formula review, a separate
  reader/clarity pass, and one consolidated same-author repair with at most three
  priorities.
- Preserve owner decisions, protected wording, provenance, living maps, and the
  recoverable pre-repair edition.
- Keep `kindling` story files in the connected Kindling repository. Do not copy
  manuscript files into this harness repository.

## Verification

Before using the seat, run:

```bash
python3 -m unittest discover -s pennamecodexv3/tests -p 'test_*.py'
bash harness/oconnor.sh formula --output /tmp/monroe-cloud-smoke.md
test -s /tmp/monroe-cloud-smoke.md
```

Delete only the temporary smoke-test output after inspection. Do not modify or
publish the private transcript.

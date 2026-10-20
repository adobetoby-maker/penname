#!/usr/bin/env bash
# Compile a Codex O'Connor seat prompt; no API calls or model subprocesses.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -B "$SCRIPT_DIR/../pennamecodexv3/scripts/build_oconnor_prompt.py" "$@"

#!/bin/zsh
# Persistent four-worker runner for the resumable library punctuation pass.

set -u

script_dir=${0:A:h}
pass_root=/Users/drive/penname/outputs/punctuation-review/codex-pass-v1
pids=()

for shard in 01 02 03 04; do
  "$script_dir/punctuation_review.py" \
    --manifest "$pass_root/manifests-high-final/shard-$shard.json" \
    --output-root "$pass_root/results-high-final/shard-$shard" \
    --backend codex \
    --model gpt-5.6-sol \
    --reasoning-effort high &
  pids+=($!)
done

function stop_workers {
  for pid in $pids; do
    kill "$pid" 2>/dev/null || true
  done
}

trap stop_workers INT TERM

exit_code_value=0
for pid in $pids; do
  wait "$pid" || exit_code_value=1
done

exit "$exit_code_value"

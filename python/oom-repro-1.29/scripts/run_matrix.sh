#!/usr/bin/env bash
# Run all 4 combos and print a comparison table.
#
# Assumes `temporal server start-dev` is running on localhost:7233.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WORKFLOWS="${WORKFLOWS:-40}"
CACHE="${CACHE:-20}"
DURATION="${DURATION:-180}"
SIGNAL_INTERVAL="${SIGNAL_INTERVAL:-1}"

COMBOS=(
  "3.10 1.23.0"
  "3.10 1.29.0"
  "3.12 1.23.0"
  "3.12 1.29.0"
)

for combo in "${COMBOS[@]}"; do
  # shellcheck disable=SC2086
  ./scripts/run_combo.sh $combo "$WORKFLOWS" "$CACHE" "$DURATION" "$SIGNAL_INTERVAL"
  echo
done

echo "==================== FINAL COMPARISON ===================="
for combo in "${COMBOS[@]}"; do
  read -r py sdk <<< "$combo"
  csv="results/py${py}-sdk${sdk}/rss.csv"
  if [[ -f "$csv" ]]; then
    ./.venvs/py${py}-sdk${sdk}/bin/python scripts/summarize.py "$csv" --label "py${py}/sdk${sdk}"
  fi
done

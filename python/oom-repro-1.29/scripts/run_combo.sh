#!/usr/bin/env bash
# Run a single (python, sdk) combo.
#
# Assumes `temporal server start-dev` is already listening on localhost:7233.
#
# Usage:
#   ./scripts/run_combo.sh <py_version> <sdk_version> <workflows> <cache_size> <duration_s> <signal_interval_s>
#
# Example:
#   ./scripts/run_combo.sh 3.12 1.29.0 40 20 180 1
set -euo pipefail

PY="${1:-3.12}"
SDK="${2:-1.29.0}"
WORKFLOWS="${3:-100}"
CACHE="${4:-500}"
DURATION="${5:-300}"
SIGNAL_INTERVAL="${6:-1}"
NO_SHUTDOWN="${NO_SHUTDOWN:-1}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMBO="py${PY}-sdk${SDK}"
VENV=".venvs/${COMBO}"
RESULT_DIR="results/${COMBO}"
mkdir -p "$RESULT_DIR"
RSS_CSV="${RESULT_DIR}/rss.csv"
WORKER_LOG="${RESULT_DIR}/worker.log"
STARTER_LOG="${RESULT_DIR}/starter.log"
PID_FILE="${RESULT_DIR}/worker.pid"

echo "==> Combo: $COMBO  (workflows=$WORKFLOWS cache=$CACHE duration=${DURATION}s interval=${SIGNAL_INTERVAL}s)"

RUN_START=$(date +%s)
echo "$RUN_START" > "${RESULT_DIR}/run.start"

if [[ ! -x "${VENV}/bin/python" ]]; then
  echo "==> Creating venv"
  uv venv --python "$PY" "$VENV"
fi

echo "==> Installing temporalio==$SDK + local package"
uv pip install --python "${VENV}/bin/python" \
  --quiet \
  "temporalio==${SDK}" \
  "psutil>=5.9" \
  --refresh-package temporalio

uv pip install --python "${VENV}/bin/python" \
  --quiet --no-deps -e .

"${VENV}/bin/python" -c "import temporalio, sys; print(f'    temporalio={temporalio.__version__} python={sys.version_info.major}.{sys.version_info.minor}')"

rm -f "$PID_FILE"

echo "==> Starting worker"
"${VENV}/bin/python" scripts/worker.py \
  --max-cached-workflows "$CACHE" \
  --pid-file "$PID_FILE" \
  --tag "$COMBO" \
  > "$WORKER_LOG" 2>&1 &
WORKER_PID=$!

for _ in {1..50}; do
  [[ -f "$PID_FILE" ]] && break
  sleep 0.2
done

if [[ ! -f "$PID_FILE" ]]; then
  echo "worker never wrote pid file; tail of log:"
  tail -40 "$WORKER_LOG" || true
  kill "$WORKER_PID" 2>/dev/null || true
  exit 1
fi

echo "==> Starting RSS monitor"
"${VENV}/bin/python" scripts/monitor_rss.py \
  --pid-file "$PID_FILE" \
  --out "$RSS_CSV" \
  --interval 1 &
MON_PID=$!

SHUTDOWN_FLAG=""
if [[ "$NO_SHUTDOWN" == "1" ]]; then
  SHUTDOWN_FLAG="--no-shutdown"
fi

echo "==> Starting $WORKFLOWS workflows, signaling for ${DURATION}s (no_shutdown=$NO_SHUTDOWN)"
# shellcheck disable=SC2086
"${VENV}/bin/python" scripts/starter.py \
  --workflows "$WORKFLOWS" \
  --duration-s "$DURATION" \
  --signal-interval-s "$SIGNAL_INTERVAL" \
  $SHUTDOWN_FLAG \
  > "$STARTER_LOG" 2>&1

echo "==> Starter finished; keeping worker up 10s for RSS tail"
sleep 10

echo "==> Stopping worker"
kill "$WORKER_PID" 2>/dev/null || true
wait "$WORKER_PID" 2>/dev/null || true
wait "$MON_PID" 2>/dev/null || true

RUN_END=$(date +%s)
echo "$RUN_END" > "${RESULT_DIR}/run.end"

echo "==> RSS-CSV summary:"
"${VENV}/bin/python" scripts/summarize.py "$RSS_CSV" --label "$COMBO"

echo "==> Prometheus summary (label combo=$COMBO):"
"${VENV}/bin/python" scripts/prom_compare.py "$COMBO" --window-s $((RUN_END - RUN_START + 30)) --slices 12

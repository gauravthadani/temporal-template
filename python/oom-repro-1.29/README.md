# oom-repro-1.29

Attempts to reproduce a memory cliff observed on `temporalio` workers
after upgrading `temporalio` 1.23 → 1.29 together with Python 3.10 → 3.12.

See [`REPORT.md`](REPORT.md) for the write-up of findings.

## What we're testing

The reported signal: working-set p50 doubled and pods sitting at
low-single-GiB jumped several GiB inside a couple of minutes. OOMs
happened at sticky cache sizes as low as 5–20, ruling out cache growth
as the direct cause. Two variables moved in the same release:
`temporalio` 1.23 → 1.29 and Python 3.10 → 3.12.

## Approach: lean first

We start with the **minimum** workflow shape (4-activity
`document_processing` pipeline, sandboxed runner) and check whether the
py3.12 / 1.29 combination shows unbounded RSS growth on its own — no
import padding, no registry padding.

- If a leak appears here → clean SDK-attributable finding.
- If not → we escalate by adding an import surface (a registry that
  transitively pulls more modules) and see whether that unlocks it. That
  would point at a per-instance retention issue that scales with import
  size rather than a raw leak.

## Layout

```
docproc_bench/
├── workflows/
│   └── document_processing.py  # 4-activity pipeline, signaled, long-lived
├── activities/
│   └── docproc.py              # classify → extract → chunk_embed → index
└── data_model/                 # small dataclasses used across the pipeline
```

## Running one combo

```
./scripts/run_combo.sh 3.12 1.29.0 100 500 300 1
# py + sdk + workflows + cache_size + duration_s + signal_interval_s
```

## Running the matrix

```
./scripts/run_matrix.sh
```

Runs the four (Python × SDK) combos in sequence and prints per-combo
summaries.

## Metrics

Worker exposes SDK + custom gauges on `http://localhost:8079/metrics`
(labelled by `combo`). Prometheus + Grafana are expected on
`localhost:9090` / `localhost:3000` — see `REPORT.md` for the dashboard
screenshot.

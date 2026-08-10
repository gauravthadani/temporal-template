"""Query Prometheus for a given combo label, produce a trajectory summary.

Usage:
    python scripts/prom_compare.py <combo_label> [--window-s 300] [--slices 12]

Combines these signals into one output:
    - worker_rss_bytes (custom gauge from the worker)
    - worker_uss_bytes
    - temporal_sticky_cache_size
    - temporal_sticky_cache_hit (counter; we compute rate)
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.parse
import urllib.request
from typing import Any


PROM = "http://localhost:9090"


def query_range(query: str, start: float, end: float, step: float) -> list[dict[str, Any]]:
    url = (
        f"{PROM}/api/v1/query_range?"
        f"query={urllib.parse.quote(query)}"
        f"&start={start}"
        f"&end={end}"
        f"&step={step}"
    )
    with urllib.request.urlopen(url, timeout=10) as fh:
        return json.loads(fh.read())["data"]["result"]


def instant(query: str) -> list[dict[str, Any]]:
    url = f"{PROM}/api/v1/query?query={urllib.parse.quote(query)}"
    with urllib.request.urlopen(url, timeout=10) as fh:
        return json.loads(fh.read())["data"]["result"]


def series_stats(values: list[tuple[float, float]]) -> dict[str, float]:
    ys = [y for _, y in values]
    if not ys:
        return {}
    return {
        "first": ys[0],
        "last": ys[-1],
        "p50": statistics.median(ys),
        "p90": statistics.quantiles(ys, n=10)[-1] if len(ys) >= 10 else max(ys),
        "peak": max(ys),
        "trough": min(ys),
        "n": len(ys),
    }


def fetch(combo: str, metric: str, start: float, end: float, step: float, agg: str | None = None) -> list[tuple[float, float]]:
    if agg:
        q = f'{agg}({metric}{{combo="{combo}"}})'
    else:
        q = f'{metric}{{combo="{combo}"}}'
    results = query_range(q, start, end, step)
    if not results:
        return []
    # single series expected
    return [(float(t), float(v)) for t, v in results[0]["values"]]


def fetch_no_combo(metric: str, start: float, end: float, step: float, agg: str | None = None) -> list[tuple[float, float]]:
    """For SDK metrics that don't carry the combo label."""
    q = f"{agg}({metric})" if agg else metric
    results = query_range(q, start, end, step)
    if not results:
        return []
    return [(float(t), float(v)) for t, v in results[0]["values"]]


def mib(n: float) -> float:
    return n / (1024 * 1024)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("combo")
    parser.add_argument("--window-s", type=int, default=300)
    parser.add_argument("--slices", type=int, default=12)
    parser.add_argument("--step-s", type=int, default=5)
    args = parser.parse_args()

    end = time.time()
    start = end - args.window_s

    rss = fetch(args.combo, "worker_rss_bytes", start, end, args.step_s)
    uss = fetch(args.combo, "worker_uss_bytes", start, end, args.step_s)

    if not rss:
        print(f"no worker_rss_bytes samples for combo={args.combo!r} in last {args.window_s}s", file=sys.stderr)
        sys.exit(2)

    # SDK metrics don't carry combo, but the run is exclusive so filtering by
    # time window is sufficient
    cache_size = fetch_no_combo("temporal_sticky_cache_size", start, end, args.step_s, agg="sum")
    cache_hit = fetch_no_combo(
        "rate(temporal_sticky_cache_hit[15s])", start, end, args.step_s, agg="sum"
    )
    wft_latency_p90 = fetch_no_combo(
        "histogram_quantile(0.9, sum by(le) (rate(temporal_workflow_task_execution_latency_bucket[30s])))",
        start,
        end,
        args.step_s,
    )

    print(f"\n=== combo={args.combo}  window={args.window_s}s ===\n")
    for label, series in (
        ("worker_rss (MiB)", rss),
        ("worker_uss (MiB)", uss),
    ):
        s = series_stats(series)
        if s:
            print(
                f"{label:22s} first={mib(s['first']):7.1f}  "
                f"p50={mib(s['p50']):7.1f}  p90={mib(s['p90']):7.1f}  "
                f"peak={mib(s['peak']):7.1f}  last={mib(s['last']):7.1f}  n={s['n']}"
            )

    s = series_stats(cache_size)
    if s:
        print(
            f"{'sticky_cache_size':22s} first={s['first']:7.1f}  p50={s['p50']:7.1f}  "
            f"peak={s['peak']:7.1f}  last={s['last']:7.1f}  n={s['n']}"
        )
    s = series_stats(cache_hit)
    if s:
        print(
            f"{'sticky_cache_hit/s':22s} p50={s['p50']:7.1f}  peak={s['peak']:7.1f}  "
            f"avg={sum(y for _, y in cache_hit)/max(len(cache_hit),1):7.1f}"
        )
    s = series_stats(wft_latency_p90)
    if s:
        print(f"{'wft_exec_latency p90':22s} p50={s['p50']:.3f}  peak={s['peak']:.3f} s")

    # trajectory
    print(f"\ntrajectory (worker_rss_bytes, {args.slices} slices):")
    step = len(rss) // args.slices if len(rss) >= args.slices else 1
    for i in range(0, len(rss), max(step, 1)):
        t, y = rss[i]
        rel = t - rss[0][0]
        print(f"  t=+{rel:6.0f}s  RSS={mib(y):7.1f} MiB")


if __name__ == "__main__":
    main()

"""Summarize a single RSS trace: baseline, p50, p90, max, delta, growth rate."""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--label", default=None)
    args = parser.parse_args()

    path = Path(args.csv_path)
    label = args.label or path.stem

    ts: list[float] = []
    rss: list[int] = []
    with path.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            ts.append(float(row["t_seconds"]))
            rss.append(int(row["rss_bytes"]))

    if not rss:
        print(f"{label}: no samples")
        return

    def mib(n: int | float) -> float:
        return n / (1024 * 1024)

    baseline = rss[0]
    peak = max(rss)
    final = rss[-1]
    p50 = statistics.median(rss)
    p90 = statistics.quantiles(rss, n=10)[-1] if len(rss) >= 10 else max(rss)
    growth = final - baseline
    duration = ts[-1] - ts[0] if len(ts) > 1 else 1.0
    growth_per_min = growth / max(duration, 1e-6) * 60

    print(
        f"{label:40s} baseline={mib(baseline):7.1f} MiB  "
        f"p50={mib(p50):7.1f}  p90={mib(p90):7.1f}  "
        f"peak={mib(peak):7.1f}  final={mib(final):7.1f}  "
        f"Δfinal-base={mib(growth):+7.1f}  "
        f"growth/min={mib(growth_per_min):+7.1f} MiB/min  "
        f"samples={len(rss)}  duration={duration:.0f}s"
    )


if __name__ == "__main__":
    main()

"""Show RSS trajectory: samples at even intervals through the run."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--label", default=None)
    parser.add_argument("--slices", type=int, default=12)
    args = parser.parse_args()

    path = Path(args.csv_path)
    label = args.label or path.stem

    rows: list[tuple[float, int]] = []
    with path.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append((float(row["t_seconds"]), int(row["rss_bytes"])))

    if len(rows) < 2:
        print(f"{label}: not enough samples")
        return

    def mib(n: float) -> float:
        return n / (1024 * 1024)

    print(f"{label}:")
    t_end = rows[-1][0]
    step = t_end / args.slices
    idx = 0
    for slice_i in range(args.slices + 1):
        target = slice_i * step
        while idx + 1 < len(rows) and rows[idx + 1][0] < target:
            idx += 1
        t, rss = rows[idx]
        print(f"  t={t:6.1f}s  RSS={mib(rss):7.1f} MiB")


if __name__ == "__main__":
    main()

"""Sample worker RSS every second and write to CSV until the worker exits."""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import psutil


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid-file", default="results/worker.pid")
    parser.add_argument("--out", required=True)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--timeout-s", type=float, default=600.0)
    args = parser.parse_args()

    pid_path = Path(args.pid_file)
    deadline = time.time() + args.timeout_s
    while not pid_path.exists() and time.time() < deadline:
        time.sleep(0.2)
    if not pid_path.exists():
        print(f"pid file {pid_path} never appeared", file=sys.stderr)
        sys.exit(1)

    pid = int(pid_path.read_text().strip())
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print(f"process {pid} vanished before monitor started", file=sys.stderr)
        sys.exit(1)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["t_seconds", "rss_bytes", "vms_bytes", "num_threads"])
        t0 = time.time()
        try:
            while True:
                try:
                    mem = proc.memory_info()
                    writer.writerow(
                        [
                            round(time.time() - t0, 3),
                            mem.rss,
                            mem.vms,
                            proc.num_threads(),
                        ]
                    )
                    fh.flush()
                except psutil.NoSuchProcess:
                    print("worker exited; monitor stopping", file=sys.stderr)
                    return
                time.sleep(args.interval)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()

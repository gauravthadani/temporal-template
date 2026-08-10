"""Worker with configurable sticky-cache size, sandboxed runner.

Writes its PID to `results/worker.pid` so the RSS sampler can find it.
Exposes SDK metrics on `--metrics-port` for Prometheus scraping.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

import psutil
from temporalio.client import Client
from temporalio.runtime import PrometheusConfig, Runtime, TelemetryConfig
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner

from docproc_bench.activities.docproc import (
    chunk_embed_activity,
    classify_document_activity,
    extract_document_activity,
    index_documents_activity,
)
from docproc_bench.workflows.document_processing import DocumentProcessingWorkflow


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="localhost:7233")
    parser.add_argument("--namespace", default="default")
    parser.add_argument("--task-queue", default="docproc-bench-tq")
    parser.add_argument("--max-cached-workflows", type=int, default=20)
    parser.add_argument("--max-concurrent-workflow-tasks", type=int, default=100)
    parser.add_argument("--max-concurrent-activities", type=int, default=100)
    parser.add_argument("--pid-file", default="results/worker.pid")
    parser.add_argument("--tag", default="unnamed", help="tag for logging only")
    parser.add_argument(
        "--metrics-bind",
        default="0.0.0.0:8079",
        help="host:port for SDK Prometheus metrics endpoint (empty to disable)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format=f"[worker/{args.tag}] %(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger = logging.getLogger("worker")

    pid_file = Path(args.pid_file)
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(os.getpid()))
    logger.info(
        "starting worker pid=%s cache=%s wft_slots=%s act_slots=%s metrics=%s",
        os.getpid(),
        args.max_cached_workflows,
        args.max_concurrent_workflow_tasks,
        args.max_concurrent_activities,
        args.metrics_bind or "disabled",
    )

    runtime: Runtime | None = None
    if args.metrics_bind:
        # OTel-aligned naming so metrics match the "Temporal Go SDK (OTel)"
        # Grafana chart: `_total` counters, unit suffixes, seconds durations.
        runtime = Runtime(
            telemetry=TelemetryConfig(
                metrics=PrometheusConfig(
                    bind_address=args.metrics_bind,
                    counters_total_suffix=True,
                    unit_suffix=True,
                    durations_as_seconds=True,
                ),
            )
        )

    client = await Client.connect(args.target, namespace=args.namespace, runtime=runtime)

    stop_event = asyncio.Event()

    def _signal_stop(*_):
        logger.info("stop signal received")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _signal_stop)

    worker = Worker(
        client,
        task_queue=args.task_queue,
        workflows=[DocumentProcessingWorkflow],
        activities=[
            classify_document_activity,
            extract_document_activity,
            chunk_embed_activity,
            index_documents_activity,
        ],
        workflow_runner=SandboxedWorkflowRunner(),
        max_cached_workflows=args.max_cached_workflows,
        max_concurrent_workflow_tasks=args.max_concurrent_workflow_tasks,
        max_concurrent_activities=args.max_concurrent_activities,
    )

    proc = psutil.Process(os.getpid())
    rss_gauge = None
    uss_gauge = None
    threads_gauge = None
    if runtime is not None:
        meter = runtime.metric_meter.with_additional_attributes({"combo": args.tag})
        # Put the unit in the name explicitly — SDK's unit_suffix flag only
        # rewrites built-in metrics, not custom gauges.
        rss_gauge = meter.create_gauge_float(
            "worker_rss_bytes", description="Worker process RSS in bytes"
        )
        uss_gauge = meter.create_gauge_float(
            "worker_uss_bytes", description="Worker process USS in bytes"
        )
        threads_gauge = meter.create_gauge_float(
            "worker_threads", description="Worker OS thread count"
        )

    async def sample_memory() -> None:
        while not stop_event.is_set():
            try:
                mem = proc.memory_full_info()
                if rss_gauge is not None:
                    rss_gauge.set(float(mem.rss))
                if uss_gauge is not None:
                    uss_gauge.set(float(mem.uss))
                if threads_gauge is not None:
                    threads_gauge.set(float(proc.num_threads()))
            except psutil.NoSuchProcess:
                return
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                pass

    mem_task = asyncio.create_task(sample_memory())

    async with worker:
        await stop_event.wait()

    mem_task.cancel()
    try:
        await mem_task
    except asyncio.CancelledError:
        pass

    try:
        pid_file.unlink()
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)

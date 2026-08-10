"""Start N long-lived workflows, signal them repeatedly to force cache
reactivations, then shut them down.

- With N > cache_size, some workflows are always being evicted and re-hydrated
  from history when they receive a signal.
- With N <= cache_size, all workflows stay warm and every signal reactivates
  a cached instance in place. That's the pathway where per-cached-instance
  state accumulation shows up.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import time
import uuid
from typing import Any

from temporalio.client import Client, WorkflowHandle

from docproc_bench.data_model import DocumentRequest
from docproc_bench.workflows.document_processing import DocumentProcessingWorkflow


async def start_one(client: Client, task_queue: str, i: int) -> WorkflowHandle[Any, Any]:
    req = DocumentRequest(
        document_id=f"doc-{i:06d}",
        workspace_id="ws-1",
        user_id=str(uuid.uuid4()),
        correlation_id=str(uuid.uuid4()),
        storage_account="bucket-a",
        container_name="backend",
        blob_region="region-a",
        blob_site="site-a",
    )
    return await client.start_workflow(
        DocumentProcessingWorkflow.run,
        req,
        id=f"docproc-{i}-{uuid.uuid4().hex[:12]}",
        task_queue=task_queue,
    )


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="localhost:7233")
    parser.add_argument("--namespace", default="default")
    parser.add_argument("--task-queue", default="docproc-bench-tq")
    parser.add_argument("--workflows", type=int, default=40, help="how many workflows to start")
    parser.add_argument("--duration-s", type=float, default=180.0, help="how long to keep signaling")
    parser.add_argument("--signal-interval-s", type=float, default=1.0, help="per-workflow signal interval")
    parser.add_argument("--start-concurrency", type=int, default=40)
    parser.add_argument(
        "--no-shutdown",
        action="store_true",
        help="leave workflows running when the signal phase ends",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[starter] %(asctime)s %(message)s")
    logger = logging.getLogger("starter")

    client = await Client.connect(args.target, namespace=args.namespace)

    logger.info("starting %s long-lived workflows", args.workflows)
    sem = asyncio.Semaphore(args.start_concurrency)

    async def guarded_start(i: int) -> WorkflowHandle[Any, Any]:
        async with sem:
            return await start_one(client, args.task_queue, i)

    handles = await asyncio.gather(*(guarded_start(i) for i in range(args.workflows)))
    logger.info("started; entering signal phase for %ss @ interval=%ss/wf", args.duration_s, args.signal_interval_s)

    stop_at = time.time() + args.duration_s
    total_signals = 0

    async def ping_loop(h: WorkflowHandle[Any, Any]) -> int:
        n = 0
        while time.time() < stop_at:
            try:
                await h.signal(DocumentProcessingWorkflow.ping)
                n += 1
            except Exception as e:
                logger.warning("signal failed for %s: %s", h.id, e)
            await asyncio.sleep(args.signal_interval_s)
        return n

    counts = await asyncio.gather(*(ping_loop(h) for h in handles))
    total_signals = sum(counts)
    logger.info("signal phase done; total signals sent = %s", total_signals)

    if args.no_shutdown:
        logger.info("leaving %s workflows running (no shutdown)", len(handles))
        return

    logger.info("shutting down workflows")
    for h in handles:
        try:
            await h.signal(DocumentProcessingWorkflow.shutdown)
        except Exception as e:
            logger.warning("shutdown signal failed for %s: %s", h.id, e)

    logger.info("waiting for completions")
    results = await asyncio.gather(*(h.result() for h in handles), return_exceptions=True)
    ok = sum(1 for r in results if not isinstance(r, Exception))
    logger.info("completed: %s/%s", ok, len(handles))


if __name__ == "__main__":
    asyncio.run(main())

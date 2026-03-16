import asyncio
from typing import List

from temporalio import workflow
from temporalio.client import Client
from temporalio.envconfig import ClientConfig
from temporalio.worker import Worker


@workflow.defn
class RequestSchedulerWorkflow:
    def __init__(self) -> None:
        self._pending_requests: asyncio.Queue[str] = asyncio.Queue()
        self._exit = False

    @workflow.run
    async def run(self) -> List[str]:
        # Continually handle from queue or wait for exit to be received
        greetings: List[str] = []
        while True:
            # Wait for queue item or exit
            await workflow.wait_condition(
                lambda: not self._pending_requests.empty() or self._exit
            )

            # Drain and process queue
            while not self._pending_requests.empty():
                dequeue = self._pending_requests.get_nowait()
                res = await self.run_child(dequeue)
                greetings.append(f"Hello, {res}")

            # Exit if complete
            if self._exit:
                return greetings

    async def run_child(self, dequeue):
        return await workflow.execute_child_workflow(
            RequestWorkflow.run,
            id=f"{workflow.info().workflow_id}-{dequeue}",
            task_queue="hello-signal-task-queue",
            args=[dequeue],
        )

    @workflow.signal
    async def submit_request(self, name: str) -> None:
        await self._pending_requests.put(name)

    @workflow.signal
    def exit(self) -> None:
        self._exit = True


@workflow.defn
class RequestWorkflow:
    def __init__(self) -> None:
        self._exit = False

    @workflow.run
    async def run(self, request_id: str) -> str:
        await workflow.sleep(30, summary="simulating sleep")
        return request_id


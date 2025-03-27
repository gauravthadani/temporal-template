import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.exceptions import ApplicationError
from temporalio.common import RetryPolicy

from contextlib import suppress

with workflow.unsafe.imports_passed_through():
    from context_propagation.activities import say_hello_activity, random_failing_activity
    from context_propagation.shared import user_id, user
    from datetime import datetime
    from typing import Optional


@workflow.defn
class SayHelloWorkflow:
    def __init__(self) -> None:
        self._complete = False
        self._task: workflow.ActivityHandle = {}

    @workflow.run
    async def run(self, name: str) -> str:
        workflow.logger.info(f"Workflow called by user {user_id.get()}")

        # Wait for signal then run activity

        # asyncio.create_task(workflow.execute_activity(
        #     activity=random_failing_activity, args=[name],
        #     start_to_close_timeout=timedelta(minutes=5),
        #     retry_policy=RetryPolicy(initial_interval=timedelta(seconds=10),
        #                              backoff_coefficient=1.2,
        #                              maximum_interval=timedelta(seconds=30)),
        #
        # ))

        # dump = user.model_dump(include={'id', 'name', 'signup_ts'})
        # workflow.logger.info(f"Workflow user {dump} complete")
        # workflow.up
        await workflow.wait_condition(lambda: self._complete)

        # raise ApplicationError("error", dump)
        return ""

    async def chain(*coroutines):
        results = [await coro for coro in coroutines]
        return results

    async def cancel_task(self) -> None:
        if self._task:
            with suppress(Exception):
                self._task.cancel()
                # await self._task

    @workflow.signal
    async def create_task(self, arg) -> None:

        await asyncio.create_task(self.cancel_task())

        if arg == "continue":
            workflow.continue_as_new("new")
        self._task = workflow.start_activity(
            say_hello_activity, arg,
            start_to_close_timeout=timedelta(minutes=5),
            activity_id=f"activity {arg} expect to cancel",
            cancellation_type=workflow.ActivityCancellationType.WAIT_CANCELLATION_COMPLETED
        )

    @workflow.signal
    async def signal_complete(self) -> None:
        workflow.logger.info(f"Signal called by user {user_id.get()}")
        self._complete = True

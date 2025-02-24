import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from context_propagation.activities import say_hello_activity, random_failing_activity
    from context_propagation.shared import user_id


@workflow.defn
class SayHelloWorkflow:
    def __init__(self) -> None:
        self._complete = False

    @workflow.run
    async def run(self, name: str) -> str:
        workflow.logger.info(f"Workflow called by user {user_id.get()}")

        # Wait for signal then run activity


        asyncio.create_task(workflow.execute_activity(
            activity=random_failing_activity, args=[name],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=10),
                                     backoff_coefficient=1.2,
                                     maximum_interval=timedelta(seconds=30)),

        ))

        # handle = await

        await workflow.wait_condition(lambda: self._complete)
        return await workflow.execute_activity(
            say_hello_activity, name, start_to_close_timeout=timedelta(minutes=5)
        )

    @workflow.signal
    async def signal_complete(self) -> None:
        workflow.logger.info(f"Signal called by user {user_id.get()}")
        self._complete = True

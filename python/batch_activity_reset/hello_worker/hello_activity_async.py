import asyncio
import uuid
from dataclasses import dataclass
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.envconfig import ClientConfig


@dataclass
class ComposeGreetingInput:
    greeting: str
    name: str


@activity.defn
def compose_greeting_2(input: ComposeGreetingInput) -> str:
    raise RuntimeError("Failed")
    return f"{input.greeting}, {input.name}!"


@dataclass
class ComposeGreetingInput:
    greeting: str
    name: str


# Basic workflow that logs and invokes an activity
@workflow.defn
class GreetingWorkflow:
    def __init__(self):
        self.should_complete = None
        self.payload = None

    @workflow.run
    async def run(self, name: str) -> str:

        t1 = await workflow.start_activity(
            compose_greeting_2,
            ComposeGreetingInput("Hello", name),
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(maximum_attempts=50, initial_interval=timedelta(seconds=10),
                                     backoff_coefficient=10),

        )
        return "result"


async def main():
    config = ClientConfig.load_client_connect_config()
    client = await Client.connect(**config)

    for i in range(10):
        await client.start_workflow(
            GreetingWorkflow.run,
            "World",
            id="hello-activity-workflow-id" + uuid.uuid4().hex,
            task_queue="hello-activity-task-queue",
        )


if __name__ == "__main__":
    asyncio.run(main())

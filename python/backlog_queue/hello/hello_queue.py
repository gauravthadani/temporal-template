import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.api.enums.v1 import TaskQueueType
from temporalio.api.taskqueue.v1 import TaskQueue
from temporalio.api.workflowservice.v1 import DescribeTaskQueueRequest
from temporalio.client import Client
from temporalio.envconfig import ClientConfig
from temporalio.worker import Worker


# While we could use multiple parameters in the activity, Temporal strongly
# encourages using a single dataclass instead which can have fields added to it
# in a backwards-compatible way.
@dataclass
class ComposeGreetingInput:
    greeting: str
    name: str


# Basic activity that logs and does string concatenation
@activity.defn
def compose_greeting(input: ComposeGreetingInput) -> str:
    activity.logger.info("Running activity with parameter %s" % input)
    return f"{input.greeting}, {input.name}!"


# Basic workflow that logs and invokes an activity
@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        workflow.logger.info("Running workflow with parameter %s" % name)
        return await workflow.execute_activity(
            compose_greeting,
            ComposeGreetingInput("Hello", name),
            start_to_close_timeout=timedelta(seconds=10),
        )


async def main():
    # Uncomment the lines below to see logging output
    # import logging
    # logging.basicConfig(level=logging.INFO)

    # Load configuration
    config = ClientConfig.load_client_connect_config(profile="gaurav")
    # config.setdefault("target_host", "localhost:7233")

    # Start client
    client = await Client.connect(**config)

    response = await client.workflow_service.describe_task_queue(
        DescribeTaskQueueRequest(
            namespace="gaurav-test.a2dd6",
            task_queue=TaskQueue(name="hello-activity-task-queue"),
            task_queue_types=[
                TaskQueueType.TASK_QUEUE_TYPE_WORKFLOW,
                TaskQueueType.TASK_QUEUE_TYPE_ACTIVITY,
            ],
            report_stats=True,
            report_pollers=True,
        )
    )

    print(response)



if __name__ == "__main__":
    asyncio.run(main())

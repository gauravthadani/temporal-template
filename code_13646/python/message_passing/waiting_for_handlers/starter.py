import asyncio
import uuid

from temporalio import client, common

from message_passing.waiting_for_handlers import (
    TASK_QUEUE,
    WORKFLOW_ID,
)
from message_passing.waiting_for_handlers.workflows import SayHelloWorkflow


async def starter():
    cl = await client.Client.connect("localhost:7233")
    wf_handle = await cl.start_workflow(
        SayHelloWorkflow.run,
        "Gaurav",
        id=WORKFLOW_ID + uuid.uuid4().hex,
        task_queue=TASK_QUEUE
    )

    print("Worfklow started- {}", wf_handle.id)


async def main():
    await starter()


if __name__ == "__main__":
    asyncio.run(main())

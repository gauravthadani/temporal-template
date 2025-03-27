import argparse
import asyncio
import logging
import uuid

from context_propagation import interceptor, shared, workflows
from context_propagation.shared import HEADER_KEY, user_id
from context_propagation.shared import encryption_data_converter
from temporalio.client import Client
from temporalio.common import WorkflowIDConflictPolicy
from temporalio.exceptions import ApplicationError


async def main():
    logging.basicConfig(level=logging.INFO)

    # Set the user ID
    shared.user_id.set("some-user")

    # # Connect client
    # client = await Client.connect(
    #     "localhost:7233",
    #     # Use our interceptor
    #     interceptors=[interceptor.ContextPropagationInterceptor()],
    #     data_converter=encryption_data_converter,
    # )


    parser = argparse.ArgumentParser(description="Use apikey with server")
    parser.add_argument(
        "--target-host", help="Host:port for the server", default="localhost:7233"
    )
    parser.add_argument(
        "--namespace", help="Namespace for the server", default="default"
    )
    parser.add_argument(
        "--api-key", help="api key", required=False
    )

    args = parser.parse_args()
    client = await Client.connect(
        args.target_host,
        namespace=args.namespace,
        rpc_metadata={"temporal-namespace": args.namespace},
        api_key=args.api_key,
        interceptors=[interceptor.ContextPropagationInterceptor()],
        data_converter=encryption_data_converter,
        tls=True,
    )

    # Start workflow, send signal, wait for completion, issue query
    handle = await client.start_workflow(
        workflow=workflows.SayHelloWorkflow.run,
        args=["Temporal"],
        id=f"context-propagation-workflow-id",
        task_queue="context-propagation-task-queue",
        id_conflict_policy=WorkflowIDConflictPolicy.TERMINATE_EXISTING,
    )

    while True:
        user_input = input("Enter something (type 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
        await handle.signal(workflows.SayHelloWorkflow.create_task, user_input.lower())

    await handle.signal(workflows.SayHelloWorkflow.signal_complete)

    try:
        result = await handle.result()
    except Exception as e:
        result = str(e)
        appError = e.__cause__.details

    logging.info(f"Workflow result {result}")
    logging.info(f"custom error {appError}")


if __name__ == "__main__":
    asyncio.run(main())

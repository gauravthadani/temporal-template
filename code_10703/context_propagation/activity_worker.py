import argparse
import asyncio
import logging

from context_propagation import activities, interceptor, workflows
from context_propagation.shared import encryption_data_converter
from temporalio.client import Client
from temporalio.worker import Worker

interrupt_event = asyncio.Event()


async def main():
    logging.basicConfig(level=logging.INFO)

    # # Connect client
    # client = await Client.connect(
    #     "localhost:7233",
    #     # Use our interceptor
    #     interceptors=[interceptor.ContextPropagationInterceptor()],
    #     data_converter=encryption_data_converter,
    # )
    #

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

    # Run a worker for the workflow
    async with Worker(
            client,
            task_queue="context-propagation-task-queue",
            activities=[activities.say_hello_activity, activities.random_failing_activity],
            # workflows=[workflows.SayHelloWorkflow],
            max_concurrent_activities=1
    ):
        # Wait until interrupted
        logging.info("Worker started, ctrl+c to exit")
        await interrupt_event.wait()
        logging.info("Shutting down")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        interrupt_event.set()
        loop.run_until_complete(loop.shutdown_asyncgens())

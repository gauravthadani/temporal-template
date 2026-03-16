import asyncio
import logging

from temporalio.client import Client
from temporalio.envconfig import ClientConfig
from temporalio.worker import Worker

from hello.hello_signal import RequestSchedulerWorkflow, RequestWorkflow

interrupt_event = asyncio.Event()
logging.basicConfig(level=logging.INFO)


async def main():
    config = ClientConfig.load_client_connect_config()
    config.setdefault("target_host", "localhost:7233")

    # Start client
    client = await Client.connect(**config)

    # Run a worker for the workflow
    async with Worker(
            client,
            task_queue="hello-signal-task-queue",
            workflows=[RequestSchedulerWorkflow, RequestWorkflow],
    ):
        print("Worker started")
        print(
            "Prometheus metrics available at http://127.0.0.1:8079/metrics, ctrl+c to exit"
        )
        await interrupt_event.wait()
        print("Shutting down")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        interrupt_event.set()
        loop.run_until_complete(loop.shutdown_asyncgens())

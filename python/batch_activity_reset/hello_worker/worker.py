import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from temporalio.client import Client
from temporalio.envconfig import ClientConfig
from temporalio.runtime import PrometheusConfig, Runtime, TelemetryConfig
from temporalio.worker import Worker, WorkerTuner, PollerBehaviorAutoscaling

from hello_worker.hello_activity_async import GreetingWorkflow, compose_greeting_2

interrupt_event = asyncio.Event()
logging.basicConfig(level=logging.DEBUG)


def init_runtime_with_prometheus(port: int) -> Runtime:
    return Runtime(
        telemetry=TelemetryConfig(
            metrics=PrometheusConfig(bind_address=f"127.0.0.1:{port}"),
        )
    )


async def main():
    runtime = init_runtime_with_prometheus(8079)

    config = ClientConfig.load_client_connect_config()
    client = await Client.connect(**config, runtime=runtime)

    worker = Worker(client, task_queue="hello-activity-task-queue",
                    workflows=[GreetingWorkflow],
                    # tuner=tuner,
                    # workflow_task_poller_behavior=PollerBehaviorAutoscaling(1, 50, 5),
                    # activity_task_poller_behavior=PollerBehaviorAutoscaling(10, 50, 10),
                    activities=[compose_greeting_2],
                    activity_executor=ThreadPoolExecutor(100),
                    max_concurrent_activities=100,
                    # max_concurrent_workflow_tasks=1,
                    )

    async with worker:
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

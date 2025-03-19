import asyncio
from dataclasses import dataclass
from datetime import timedelta

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.contrib.opentelemetry import TracingInterceptor
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import SandboxRestrictions, SandboxedWorkflowRunner

# with workflow.unsafe.imports_passed_through():
#     from ddtrace.opentracer import Tracer, set_global_tracer


# While we could use multiple parameters in the activity, Temporal strongly
# encourages using a single dataclass instead which can have fields added to it
# in a backwards-compatible way.
@dataclass
class ComposeGreetingInput:
    greeting: str
    name: str


# Basic activity that logs and does string concatenation
@activity.defn
async def compose_greeting(input: ComposeGreetingInput) -> str:
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

# def init_tracer(service_name):
#     config = {
#       'agent_hostname': 'localhost',
#       'agent_port': 8126,
#     }
#     tracer = Tracer(service_name, config=config)
#     set_global_tracer(tracer)
#     return tracer


def init_tracer(service_name):
    config = {
      'agent_hostname': 'localhost',
      'agent_port': 4317,
    }
    # tracer = Tracer(service_name, config=config)
    # set_global_tracer(tracer)

    provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "my-service"}))
    exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    # return tracer
#
# def init_runtime_with_telemetry() -> Runtime:
#     # Setup global tracer for workflow traces
#     provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "my-service"}))
#     exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
#     provider.add_span_processor(BatchSpanProcessor(exporter))
#     trace.set_tracer_provider(provider)
#
#
#     # Setup SDK metrics to OTel endpoint
#     return Runtime(
#         telemetry=TelemetryConfig(
#             metrics=OpenTelemetryConfig(url="http://localhost:4317")
#         )
#     )


async def main():
    # Uncomment the lines below to see logging output
    # import logging
    # logging.basicConfig(level=logging.INFO)

    # runtime = init_runtime_with_telemetry()

    init_tracer("hello_activity")

    # Start client
    client = await Client.connect("localhost:7233",
                                  interceptors=[TracingInterceptor()],
                                  # runtime=runtime,
                                  )

    await Worker(
        client,
        task_queue="hello-activity-task-queue",
        workflows=[GreetingWorkflow],
        activities=[compose_greeting],
        workflow_runner=SandboxedWorkflowRunner(
            restrictions=SandboxRestrictions.default.with_passthrough_modules("opentelemetry", "ddtrace")
        )
    ).run()
    # Run a worker for the workflow
    # async with Worker(
    #         client,
    #         task_queue="hello-activity-task-queue",
    #         workflows=[GreetingWorkflow],
    #         activities=[compose_greeting],
    #         workflow_runner=SandboxedWorkflowRunner(
    #             restrictions=SandboxRestrictions.default.with_passthrough_modules("opentelemetry", "ddtrace")
    #         )
    # ):
    #     # While the worker is running, use the client to run the workflow and
    #     # print out its result. Note, in many production setups, the client
    #     # would be in a completely separate process from the worker.
    #     result = await client.execute_workflow(
    #         GreetingWorkflow.run,
    #         "World",
    #         id="hello-activity-workflow-id",
    #         task_queue="hello-activity-task-queue",
    #     )
    #     print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())

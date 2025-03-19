import os

import uvicorn
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from temporalio.client import Client
from temporalio.contrib.opentelemetry import TracingInterceptor

from hello.hello_activity import GreetingWorkflow, init_tracer
from opentelemetry import trace
class Item(BaseModel):
    name: str
    description: str | None = None

app = FastAPI()
router = APIRouter()
init_tracer("hello_activity")


@router.post("/items/")
async def create_item(item: Item):
    otel_tracer = trace.get_tracer(__name__)

    with otel_tracer.start_as_current_span("POSTAPI") as span:
        span.set_attribute("key", "value")
        client = await Client.connect("localhost:7233",
                                      interceptors=[TracingInterceptor()],
                                      # runtime=runtime,
                                      )
        result = await client.execute_workflow(
            GreetingWorkflow.run,
            "World",
            id="hello-activity-workflow-id",
            task_queue="hello-activity-task-queue",
        )
    return {"message": "Item created"}


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

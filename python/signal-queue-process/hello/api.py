from contextlib import asynccontextmanager

from fastapi import FastAPI, Request as FastAPIRequest
from pydantic import BaseModel
from temporalio.client import Client
from temporalio.envconfig import ClientConfig

from hello.hello_signal import RequestSchedulerWorkflow


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = ClientConfig.load_client_connect_config()
    config.setdefault("target_host", "localhost:7233")
    app.state.temporal_client = await Client.connect(**config)
    yield


app = FastAPI(lifespan=lifespan)


class Request(BaseModel):
    lz_id: str
    request_id: str


@app.post("/request")
async def handle_request(body: Request, req: FastAPIRequest) -> dict:
    client: Client = req.app.state.temporal_client

    await client.start_workflow(
        RequestSchedulerWorkflow.run,
        id=body.lz_id,
        task_queue="hello-signal-task-queue",
        start_signal="submit_request",
        start_signal_args=[body.request_id],
    )

    return {"request_id": body.request_id, "status": "received"}

from temporalio import activity
import asyncio
from context_propagation import shared


@activity.defn
async def say_hello_activity(name: str) -> str:
    activity.logger.info(f"Activity called by user {shared.user_id.get()}")
    await asyncio.sleep(30)
    return f"Hello, {name}"



@activity.defn
async def random_failing_activity(name: str) -> str:
    activity.logger.info(f"Failing Activity called by user {shared.user_id.get()}")
    # await asyncio.sleep(10)
    raise Warning("As defined, this activity was meant to fail")
    # return f"Hello, {name}"

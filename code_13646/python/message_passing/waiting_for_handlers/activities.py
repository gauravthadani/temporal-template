from temporalio import activity

@activity.defn
async def compose_greeting(input: str) -> str:
    info = activity.info()

    return f"hello , {input}!"

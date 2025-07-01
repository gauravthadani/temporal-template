from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from message_passing.waiting_for_handlers.activities import compose_greeting

@workflow.defn
class SayHelloWorkflow:
    def __init__(self) -> None:
        self._complete = False
        self._count = 0

    @workflow.update(name="increment")
    async def increment(self) -> str:
        self._count = self._count + 1
        return "Workflow status updated"

    @workflow.update(name="close")
    async def close(self) -> str:
        self._complete = True
        workflow.logger.info(f"is complete? {self._complete}")
        return "Workflow status updated"

    @workflow.run
    async def run(self, name: str) -> str:
        workflow.logger.info(f"Workflow Started")

        # i = 0
        # while True:
        #     i += 1

        await workflow.execute_activity(compose_greeting, name, start_to_close_timeout=timedelta(minutes=5))

        await workflow.wait_condition(lambda: self._complete == True)

        return  "hi"


from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from docproc_bench.activities.docproc import (
        chunk_embed_activity,
        classify_document_activity,
        extract_document_activity,
        index_documents_activity,
    )
    from docproc_bench.data_model import DocumentRequest, DocumentResponse


@workflow.defn(name="document_processing")
class DocumentProcessingWorkflow:
    """4-activity docproc pipeline, but the workflow stays open after the
    pipeline runs and only exits on an explicit `shutdown` signal.

    Between the initial pipeline and shutdown, callers fire `ping` signals
    which flip `_pinged` inside a `wait_condition` loop. Each signal is a
    fresh workflow task that reactivates the (cached) workflow instance —
    which is exactly the pathway where per-cached-instance memory leaks
    would surface.
    """

    def __init__(self) -> None:
        self._pinged = False
        self._shutdown = False
        self._ping_count = 0
        self._response: DocumentResponse | None = None

    @workflow.signal
    def ping(self) -> None:
        self._ping_count += 1
        self._pinged = True

    @workflow.signal
    def shutdown(self) -> None:
        self._shutdown = True

    @workflow.query
    def ping_count(self) -> int:
        return self._ping_count

    @workflow.run
    async def run(self, req: DocumentRequest) -> DocumentResponse:
        classify = await workflow.execute_activity(
            classify_document_activity,
            req,
            start_to_close_timeout=timedelta(seconds=30),
        )
        extract = await workflow.execute_activity(
            extract_document_activity,
            req,
            start_to_close_timeout=timedelta(seconds=30),
        )
        chunk = await workflow.execute_activity(
            chunk_embed_activity,
            extract,
            start_to_close_timeout=timedelta(seconds=30),
        )
        index = await workflow.execute_activity(
            index_documents_activity,
            chunk,
            start_to_close_timeout=timedelta(seconds=30),
        )
        self._response = DocumentResponse(
            document_id=req.document_id,
            classify=classify,
            extract=extract,
            chunk_embed=chunk,
            index=index,
        )

        while not self._shutdown:
            await workflow.wait_condition(lambda: self._pinged or self._shutdown)
            self._pinged = False

        return self._response

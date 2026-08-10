import asyncio

from temporalio import activity

from docproc_bench.data_model import (
    ChunkEmbedResult,
    ClassifyResult,
    DocumentRequest,
    ExtractResult,
    IndexResult,
)


@activity.defn(name="classify_document_activity")
async def classify_document_activity(req: DocumentRequest) -> ClassifyResult:
    await asyncio.sleep(0.01)
    return ClassifyResult(document_id=req.document_id, doc_type="contract", confidence=0.94)


@activity.defn(name="extract_document_activity")
async def extract_document_activity(req: DocumentRequest) -> ExtractResult:
    await asyncio.sleep(0.01)
    return ExtractResult(
        document_id=req.document_id,
        text_bytes=48_000,
        page_count=12,
        metadata={"lang": "en"},
    )


@activity.defn(name="chunk_embed_activity")
async def chunk_embed_activity(extract: ExtractResult) -> ChunkEmbedResult:
    await asyncio.sleep(0.01)
    return ChunkEmbedResult(
        document_id=extract.document_id,
        chunk_count=42,
        embedding_dim=1536,
    )


@activity.defn(name="index_documents_activity")
async def index_documents_activity(chunk: ChunkEmbedResult) -> IndexResult:
    await asyncio.sleep(0.01)
    return IndexResult(
        document_id=chunk.document_id,
        indexed=True,
        index_name="index-a",
    )

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentRequest:
    document_id: str
    workspace_id: str
    user_id: str
    correlation_id: str
    storage_account: str
    container_name: str
    blob_region: str
    blob_site: str


@dataclass
class ClassifyResult:
    document_id: str
    doc_type: str
    confidence: float


@dataclass
class ExtractResult:
    document_id: str
    text_bytes: int
    page_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ChunkEmbedResult:
    document_id: str
    chunk_count: int
    embedding_dim: int


@dataclass
class IndexResult:
    document_id: str
    indexed: bool
    index_name: str


@dataclass
class DocumentResponse:
    document_id: str
    classify: ClassifyResult
    extract: ExtractResult
    chunk_embed: ChunkEmbedResult
    index: IndexResult

"""Pydantic v2 request and response schemas for the Second Brain AI API."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------


class MessageResponse(BaseModel):
    """Generic message wrapper for simple acknowledgements."""

    message: str = Field(..., description="Human-readable status message.")


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------


class DocumentUploadResponse(BaseModel):
    """Response returned after a file upload is accepted for ingestion."""

    id: str = Field(..., description="Unique identifier assigned to the uploaded document.")
    filename: str = Field(..., description="Original filename of the uploaded file.")
    content_type: str | None = Field(
        default=None,
        description="MIME type reported by the client or inferred from the file.",
    )
    size_bytes: int | None = Field(
        default=None,
        description="Size of the uploaded file in bytes.",
    )
    status: Literal["pending", "processing", "ready", "failed"] = Field(
        default="pending",
        description="Current ingestion status of the document.",
    )
    message: str = Field(..., description="Status message for the upload request.")


class DocumentListItem(BaseModel):
    """Summary row for a document in list views."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique document identifier.")
    filename: str = Field(..., description="Stored or original filename.")
    content_type: str | None = Field(default=None, description="Document MIME type.")
    size_bytes: int | None = Field(default=None, description="File size in bytes.")
    status: Literal["pending", "processing", "ready", "failed"] = Field(
        ...,
        description="Current ingestion/processing status.",
    )
    created_at: datetime = Field(..., description="UTC timestamp when the document was created.")
    updated_at: datetime | None = Field(
        default=None,
        description="UTC timestamp of the last metadata update.",
    )


class DocumentListResponse(BaseModel):
    """Paginated-style list of all tracked documents."""

    documents: list[DocumentListItem] = Field(
        default_factory=list,
        description="Collection of document summaries.",
    )
    total: int = Field(..., description="Total number of documents tracked in the system.")


class DocumentDetailResponse(BaseModel):
    """Full metadata view for a single document."""

    id: str = Field(..., description="Unique document identifier.")
    filename: str = Field(..., description="Stored or original filename.")
    content_type: str | None = Field(default=None, description="Document MIME type.")
    size_bytes: int | None = Field(default=None, description="File size in bytes.")
    status: Literal["pending", "processing", "ready", "failed"] = Field(
        ...,
        description="Current ingestion/processing status.",
    )
    summary: str | None = Field(
        default=None,
        description="LLM-generated summary of the document, if available.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Semantic or user-assigned tags associated with the document.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional structured metadata (page count, source, etc.).",
    )
    created_at: datetime = Field(..., description="UTC timestamp when the document was created.")
    updated_at: datetime | None = Field(
        default=None,
        description="UTC timestamp of the last metadata update.",
    )


class DocumentDeleteResponse(BaseModel):
    """Response returned after a document is removed from the system."""

    id: str = Field(..., description="Identifier of the deleted document.")
    deleted: bool = Field(..., description="Whether the document was successfully removed.")
    message: str = Field(..., description="Human-readable deletion status message.")


class SummaryResponse(BaseModel):
    """Response returned after summarization is triggered or retrieved."""

    document_id: str = Field(..., description="Identifier of the summarized document.")
    summary: str | None = Field(
        default=None,
        description="Generated summary text, if available immediately.",
    )
    status: Literal["pending", "processing", "completed", "failed"] = Field(
        ...,
        description="Summarization job status.",
    )
    message: str = Field(..., description="Human-readable summarization status message.")


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------


class NoteCreateRequest(BaseModel):
    """Payload for creating a new text note."""

    title: str = Field(..., min_length=1, max_length=500, description="Note title.")
    content: str = Field(..., min_length=1, description="Note body content.")
    folder: str | None = Field(
        default=None,
        max_length=255,
        description="Optional folder or collection name for organization.",
    )


class NoteCreateResponse(BaseModel):
    """Response returned after a note is created."""

    id: str = Field(..., description="Unique identifier assigned to the note.")
    title: str = Field(..., description="Note title.")
    folder: str | None = Field(default=None, description="Folder the note was stored under.")
    status: Literal["pending", "processing", "ready", "failed"] = Field(
        default="pending",
        description="Ingestion/indexing status of the note.",
    )
    message: str = Field(..., description="Human-readable creation status message.")


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------


class ChatMessage(BaseModel):
    """A single turn in the conversational history."""

    role: Literal["user", "assistant", "system"] = Field(
        ...,
        description="Speaker role for this message.",
    )
    content: str = Field(..., min_length=1, description="Message text content.")


class ChatQueryRequest(BaseModel):
    """Payload for a RAG-backed chat query."""

    query: str = Field(..., min_length=1, description="User question or prompt.")
    chat_history: list[ChatMessage] = Field(
        default_factory=list,
        description="Prior conversation turns for multi-turn context.",
    )


class ChatSource(BaseModel):
    """A retrieved chunk cited in a chat answer."""

    document_id: str = Field(..., description="Source document identifier.")
    chunk_id: str = Field(..., description="Source chunk identifier within the document.")
    content: str = Field(..., description="Retrieved text snippet.")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score for the chunk.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional chunk metadata (page, section, etc.).",
    )


class ChatQueryResponse(BaseModel):
    """LLM answer with optional retrieved source citations."""

    answer: str = Field(..., description="Generated assistant response.")
    sources: list[ChatSource] = Field(
        default_factory=list,
        description="Retrieved chunks used to ground the answer.",
    )


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


class SearchRequest(BaseModel):
    """Payload for semantic vector search."""

    query: str = Field(..., min_length=1, description="Natural-language search query.")
    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of results to return.",
    )


class SearchResultItem(BaseModel):
    """A single semantic search hit."""

    document_id: str = Field(..., description="Matched document identifier.")
    chunk_id: str = Field(..., description="Matched chunk identifier.")
    content: str = Field(..., description="Matched text snippet.")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity/relevance score.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional chunk metadata (page, filename, etc.).",
    )


class SearchResponse(BaseModel):
    """Semantic search results for a query."""

    query: str = Field(..., description="Echo of the submitted search query.")
    results: list[SearchResultItem] = Field(
        default_factory=list,
        description="Ranked list of matching chunks.",
    )
    total: int = Field(..., description="Number of results returned.")


# ---------------------------------------------------------------------------
# Dashboard & Health
# ---------------------------------------------------------------------------


class DashboardResponse(BaseModel):
    """Aggregate system statistics for the admin dashboard."""

    total_documents: int = Field(..., ge=0, description="Count of tracked documents.")
    total_notes: int = Field(..., ge=0, description="Count of stored notes.")
    total_chunks: int = Field(..., ge=0, description="Count of indexed vector chunks.")
    storage_used_bytes: int = Field(..., ge=0, description="Approximate storage consumed by uploads.")
    documents_by_status: dict[str, int] = Field(
        default_factory=dict,
        description="Document counts grouped by processing status.",
    )


class HealthResponse(BaseModel):
    """Service health and readiness indicators."""

    status: Literal["ok", "degraded", "down"] = Field(
        ...,
        description="Overall service health status.",
    )
    version: str = Field(..., description="API version string.")
    timestamp: datetime = Field(..., description="UTC timestamp of the health check.")

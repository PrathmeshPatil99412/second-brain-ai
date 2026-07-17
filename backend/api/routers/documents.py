"""Document ingestion and management routes."""

from datetime import UTC, datetime

from fastapi import APIRouter, File, UploadFile, status, Depends
from sqlalchemy.orm import Session
from api.schemas import (
    DocumentDeleteResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentUploadResponse,
)
from database.session import get_db
from services.document_service import ingest_document

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a document",
    description=(
        "Accept a file upload and enqueue it for ingestion. "
        "Supported formats will be parsed, chunked, embedded, and indexed asynchronously."
    ),
)
async def upload_document(
    file: UploadFile = File(..., description="Document file to ingest (e.g. PDF)."),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    """
    Accept an uploaded file and register it for background ingestion.

    Implementation will delegate to the ingestion service for parsing,
    chunking, embedding, and persistence.
    """
    result = ingest_document(db, file)
    return DocumentUploadResponse(**result)


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List all documents",
    description="Return metadata summaries for every document tracked in the system.",
)
async def list_documents() -> DocumentListResponse:
    """
    List all tracked documents with lightweight metadata.

    Implementation will query the document repository and return ordered results.
    """
    # TODO: fetch from document repository
    return DocumentListResponse(documents=[], total=0)


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    summary="Get document details",
    description="Fetch metadata, summary, and tags for a specific document by ID.",
)
async def get_document(document_id: str) -> DocumentDetailResponse:
    """
    Retrieve full metadata for a single document.

    Implementation will load the document record, summary, and tags from storage.
    """
    # TODO: fetch document by ID; raise 404 if not found
    return DocumentDetailResponse(
        id=document_id,
        filename="placeholder.pdf",
        status="pending",
        summary=None,
        tags=[],
        metadata={},
        created_at=datetime.now(UTC),
    )


@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
    summary="Delete a document",
    description=(
        "Remove a document and its associated chunks, embeddings, and metadata "
        "from the system."
    ),
)
async def delete_document(document_id: str) -> DocumentDeleteResponse: 
    """
    Delete a document and all derived artifacts.

    Implementation will remove files, vector entries, and database records atomically.
    """
    # TODO: delete from storage, vector DB, and SQLite
    return DocumentDeleteResponse(
        id=document_id,
        deleted=False,
        message="Deletion not yet implemented.",
    )

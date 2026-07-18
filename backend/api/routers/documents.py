"""Document ingestion and management routes."""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from api.schemas import (
    DocumentDeleteResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentUploadResponse,
)
from database import crud
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
    result = ingest_document(db, file)
    return DocumentUploadResponse(**result)


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List all documents",
    description="Return metadata summaries for every document tracked in the system.",
)
async def list_documents(db: Session = Depends(get_db)) -> DocumentListResponse:
    docs = crud.list_documents(db)
    return DocumentListResponse(documents=docs, total=len(docs))


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    summary="Get document details",
    description="Fetch metadata, summary, and tags for a specific document by ID.",
)
async def get_document(document_id: str, db: Session = Depends(get_db)) -> DocumentDetailResponse:
    doc = crud.get_document(db, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentDetailResponse(
        id=doc.id,
        filename=doc.filename,
        content_type=doc.content_type,
        size_bytes=doc.size_bytes,
        status=doc.status,
        summary=doc.summary,
        tags=doc.tags,
        metadata=doc.doc_metadata,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
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
async def delete_document(document_id: str, db: Session = Depends(get_db)) -> DocumentDeleteResponse:
    deleted = crud.delete_document(db, document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentDeleteResponse(id=document_id, deleted=True, message="Document deleted.")
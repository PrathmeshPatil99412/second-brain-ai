"""Document summarization routes."""

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from api.schemas import SummaryResponse
from database import crud
from database.session import get_db
from ingestion.parser import extract_text
from intelligence.summarizer import summarize_text
from intelligence.tagger import generate_tags



router = APIRouter(prefix="/summary", tags=["Summary"])


@router.post(
    "/{document_id}",
    response_model=SummaryResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger document summarization",
    description="Enqueue or run LLM summarization for the specified document.",
)
async def summarize_document(document_id: str, db: Session = Depends(get_db)) -> SummaryResponse:
    doc = crud.get_document(db, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    text = extract_text(doc.file_path)
    summary = summarize_text(text)
    tags = generate_tags(text)

    crud.update_document_summary(db, document_id, summary=summary, tags=tags)

    return SummaryResponse(
        document_id=document_id,
        summary=summary,
        status="completed",
        message=f"Summary generated with {len(tags)} tags.",
    )

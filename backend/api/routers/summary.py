"""Document summarization routes."""

from fastapi import APIRouter, status

from api.schemas import SummaryResponse

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.post(
    "/{document_id}",
    response_model=SummaryResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger document summarization",
    description="Enqueue or run LLM summarization for the specified document.",
)
async def summarize_document(document_id: str) -> SummaryResponse:
    """
    Trigger text summarization for a document.

    Implementation will delegate to the intelligence service using Gemini.
    """
    # TODO: delegate to intelligence/summarization service
    return SummaryResponse(
        document_id=document_id,
        summary=None,
        status="pending",
        message="Summarization not yet implemented.",
    )

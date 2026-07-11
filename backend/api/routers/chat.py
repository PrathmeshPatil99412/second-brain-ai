"""RAG-backed conversational query routes."""

from fastapi import APIRouter

from api.schemas import ChatQueryRequest, ChatQueryResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/query",
    response_model=ChatQueryResponse,
    summary="Chat with the knowledge base",
    description=(
        "Submit a natural-language question with optional chat history. "
        "The system retrieves relevant chunks and generates a grounded answer via Gemini."
    ),
)
async def chat_query(payload: ChatQueryRequest) -> ChatQueryResponse:
    """
    Run a retrieval-augmented chat query.

    Implementation will retrieve context from ChromaDB and call the intelligence service.
    """
    # TODO: retrieval + Gemini generation
    return ChatQueryResponse(
        answer="Chat query handling is not yet implemented.",
        sources=[],
    )

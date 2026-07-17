"""RAG-backed conversational query routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas import ChatQueryRequest, ChatQueryResponse
from database.session import get_db
from services.chat_service import run_chat_query

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
async def chat_query(payload: ChatQueryRequest, db: Session = Depends(get_db)) -> ChatQueryResponse:
    history = [msg.model_dump() for msg in payload.chat_history] if payload.chat_history else None
    result = run_chat_query(db, payload.query, history)
    return ChatQueryResponse(**result)
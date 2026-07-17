"""
Chat orchestration: retrieval + prompt building + Gemini generation + citations + history.
"""
from sqlalchemy.orm import Session

from database import crud
from intelligence.gemini import generate_text
from retrieval.citations import to_chat_sources
from retrieval.prompt_builder import build_chat_prompt, get_system_instruction
from retrieval.retriever import retrieve_top_k
from utils.logger import get_logger

logger = get_logger(__name__)


def run_chat_query(db: Session, query: str, chat_history: list[dict] | None = None) -> dict:
    """
    Full RAG chat pipeline: retrieve -> build prompt -> generate -> format
    citations -> save both turns to history. Returns dict matching
    ChatQueryResponse shape.
    """
    # 1. Retrieve relevant chunks
    retrieved = retrieve_top_k(db, query)

    # 2. Build prompt + call Gemini
    prompt = build_chat_prompt(query, retrieved, chat_history)
    answer = generate_text(prompt, system_instruction=get_system_instruction())

    # 3. Format citations
    sources = to_chat_sources(retrieved)

    # 4. Persist both turns
    crud.save_chat_message(db, role="user", content=query)
    crud.save_chat_message(db, role="assistant", content=answer, sources=sources)

    logger.info(f"Chat query answered with {len(sources)} sources")
    return {"answer": answer, "sources": sources}
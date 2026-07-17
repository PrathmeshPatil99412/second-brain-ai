"""Semantic vector search routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas import SearchRequest, SearchResponse
from database.session import get_db
from retrieval.citations import to_search_results
from retrieval.retriever import retrieve_top_k

router = APIRouter(prefix="/search", tags=["Search"])


@router.post(
    "",
    response_model=SearchResponse,
    summary="Semantic search",
    description=(
        "Perform semantic vector search over indexed document chunks. "
        "Returns the top-k most relevant results for the given query."
    ),
)
async def semantic_search(payload: SearchRequest, db: Session = Depends(get_db)) -> SearchResponse:
    results = retrieve_top_k(db, payload.query, k=payload.top_k)
    formatted = to_search_results(results)
    return SearchResponse(query=payload.query, results=formatted, total=len(formatted))
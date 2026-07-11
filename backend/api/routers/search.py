"""Semantic vector search routes."""

from fastapi import APIRouter

from api.schemas import SearchRequest, SearchResponse

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
async def semantic_search(payload: SearchRequest) -> SearchResponse:
    """
    Execute a semantic search against the vector store.

    Implementation will embed the query and query ChromaDB for nearest neighbors.
    """
    # TODO: embed query and search ChromaDB
    return SearchResponse(
        query=payload.query,
        results=[],
        total=0,
    )

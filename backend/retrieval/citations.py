"""
Formats retrieval results into the citation shapes your API schemas expect.
"""


def to_chat_sources(results: list[dict]) -> list[dict]:
    """
    Convert retriever results into ChatSource-shaped dicts
    (matches api/schemas.py: ChatSource).
    """
    return [
        {
            "document_id": r["document_id"],
            "chunk_id": r["chunk_id"],
            "content": r["content"],
            "score": r["score"],
            "metadata": r["metadata"],
        }
        for r in results
    ]


def to_search_results(results: list[dict]) -> list[dict]:
    """
    Convert retriever results into SearchResultItem-shaped dicts
    (matches api/schemas.py: SearchResultItem).
    Same shape as ChatSource right now, kept as a separate function since
    search and chat citations could diverge later (e.g. search might want
    to omit `score` rounding, or chat might want to trim `content` length).
    """
    return [
        {
            "document_id": r["document_id"],
            "chunk_id": r["chunk_id"],
            "content": r["content"],
            "score": r["score"],
            "metadata": r["metadata"],
        }
        for r in results
    ]
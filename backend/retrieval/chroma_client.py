print("SCRIPT STARTED", flush=True)
"""
ChromaDB client wrapper — persistent local vector store.

WHAT THIS FILE DOES:
Wraps chromadb so ingestion (writing vectors) and retrieval (searching
vectors) both go through the same collection setup, instead of each
creating their own client/collection independently.
"""
import chromadb

from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Persistent client = writes to disk at settings.chroma_dir, survives restarts.
# (Not an in-memory client, and not a client/server setup — just a local folder.)
_client = chromadb.PersistentClient(path=str(settings.chroma_dir))

_COLLECTION_NAME = "second_brain_chunks"


def get_collection():
    """
    Return the single shared collection all chunks live in.
    get_or_create_collection is idempotent — safe to call repeatedly,
    won't wipe existing data if the collection already exists.
    """
    return _client.get_or_create_collection(name=_COLLECTION_NAME)


def add_chunks(
    ids: list[str],
    texts: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
) -> None:
    """
    Insert chunk vectors into Chroma.

    CRITICAL: `ids` here MUST be the exact same UUID strings used as the
    Chunk.id primary key in SQLite (see database/models.py). This is what
    lets retrieval later say "Chroma returned chunk_id=X" and look up the
    full text/metadata for X in SQLite directly, with no separate mapping
    table needed.
    """
    collection = get_collection()
    collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
    logger.info(f"Added {len(ids)} chunks to Chroma collection '{_COLLECTION_NAME}'")


def query_collection(query_embedding: list[float], top_k: int = 5) -> dict:
    """
    Search for the top_k most similar chunks to a query embedding.
    Returns Chroma's raw result dict: {'ids': [[...]], 'documents': [[...]],
    'distances': [[...]], 'metadatas': [[...]]} — note the nested lists,
    Chroma supports batched queries so everything is wrapped one level deep
    even for a single query.
    """
    collection = get_collection()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results


def count_all() -> int:
    """Total number of chunks currently stored in Chroma — useful for sanity checks."""
    return get_collection().count()


if __name__ == "__main__":
    # Standalone test — run from backend/:
    #   python -m retrieval.chroma_client
    print("Testing ChromaDB client with fake data...")

    fake_ids = ["test-id-1", "test-id-2", "test-id-3"]
    fake_texts = [
        "The Eiffel Tower is located in Paris, France.",
        "Python is a popular programming language for data science.",
        "Cats are independent animals that enjoy sleeping most of the day.",
    ]
    # Fake embeddings just for structural testing — NOT using real sentence-transformers
    # here on purpose, to keep this test isolated from embeddings.py.
    import random
    fake_embeddings = [[random.random() for _ in range(384)] for _ in fake_texts]
    fake_metadatas = [{"document_id": "doc-fake", "chunk_index": i} for i in range(len(fake_texts))]

    add_chunks(fake_ids, fake_texts, fake_embeddings, fake_metadatas)

    print(f"\nTotal chunks in collection: {count_all()}")

    # Query using the SAME embedding as chunk 0 — should return test-id-1 as the top/best match
    results = query_collection(fake_embeddings[0], top_k=2)
    print("\nQuery results (searching with chunk 0's own embedding):")
    print("IDs:", results["ids"])
    print("Documents:", results["documents"])
    print("Distances:", results["distances"])
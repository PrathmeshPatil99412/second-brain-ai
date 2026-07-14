"""
Embedding generation using sentence-transformers (fully local, no API calls).

WHAT THIS FILE DOES:
Converts text into vectors (lists of numbers) that capture semantic meaning.
Used in TWO places:
  1. Ingestion: embed each chunk when a document/note is uploaded, before
     storing the vector in ChromaDB.
  2. Retrieval: embed the user's search/chat query the same way, so it can
     be compared against stored chunk vectors.

CRITICAL: both ingestion and retrieval MUST use this exact same function/model.
If you embed chunks with one model and queries with another, the vectors
live in different "spaces" and similarity search returns garbage.
"""
from sentence_transformers import SentenceTransformer

from utils.logger import get_logger

logger = get_logger(__name__)

# Loaded ONCE at import time. Loading this model is slow-ish (reads weights
# from disk into memory) — doing it per-call would make every single
# chunk embed painfully slow. One instance, reused for the app's lifetime.
_MODEL_NAME = "all-MiniLM-L6-v2"  # small, fast, 384-dim vectors, good default for hackathons
_model = SentenceTransformer(_MODEL_NAME)

logger.info(f"Loaded embedding model: {_MODEL_NAME} (dim={_model.get_sentence_embedding_dimension()})")


def embed_text(text: str) -> list[float]:
    """
    Embed a single piece of text (e.g. one search query).
    Returns a list of floats (the vector) — this exact shape is what
    ChromaDB expects when you pass query_embeddings.
    """
    vector = _model.encode(text, convert_to_numpy=True)
    return vector.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """
    Embed multiple texts at once (e.g. all chunks from one uploaded document).
    Batching is significantly faster than calling embed_text() in a loop,
    because the model processes multiple inputs together on the same pass.
    """
    vectors = _model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return vectors.tolist()


if __name__ == "__main__":
    # Standalone test — run from backend/:
    #   python -m ingestion.embeddings
    print("Testing embedding generation...")

    single = embed_text("What is a second brain?")
    print(f"\nSingle embedding length: {len(single)}")
    print(f"First 5 values: {single[:5]}")

    batch = embed_batch([
        "Second brain is a personal knowledge system.",
        "The weather today is sunny.",
    ])
    print(f"\nBatch embedding count: {len(batch)}")
    print(f"Each vector length: {len(batch[0])}")
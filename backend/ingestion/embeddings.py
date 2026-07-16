"""
Embedding generation using sentence-transformers (fully local, no API calls).
Used by BOTH ingestion (embed chunks) and retrieval (embed queries) —
must stay the single source of truth so both sides use the same model.
"""
from sentence_transformers import SentenceTransformer

from utils.logger import get_logger

logger = get_logger(__name__)

_MODEL_NAME = "all-MiniLM-L6-v2"  # 384-dim, fast on CPU
_model = SentenceTransformer(_MODEL_NAME)

logger.info(f"Loaded embedding model: {_MODEL_NAME} (dim={_model.get_embedding_dimension()})")

def embed_text(text: str) -> list[float]:
    """Embed a single string (e.g. one search/chat query)."""
    vector = _model.encode(text, convert_to_numpy=True)
    return vector.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed multiple strings at once (e.g. all chunks from one document) — faster than looping."""
    vectors = _model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return vectors.tolist()


if __name__ == "__main__":
    print("Testing embedding generation...")
    single = embed_text("What is a second brain?")
    print(f"Single embedding length: {len(single)}")
    print(f"First 5 values: {single[:5]}")

    batch = embed_batch([
        "Second brain is a personal knowledge system.",
        "The weather today is sunny.",
    ])
    print(f"Batch embedding count: {len(batch)}")
    print(f"Each vector length: {len(batch[0])}")
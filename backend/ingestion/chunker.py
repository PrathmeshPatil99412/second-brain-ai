"""
Text chunking using LangChain's RecursiveCharacterTextSplitter.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap,
    separators=["\n\n", "\n", ". ", " ", ""],  # tries paragraph breaks first, falls back to smaller units
)


def chunk_text(text: str) -> list[str]:
    """Split a long text into overlapping chunks, sized per config."""
    chunks = _splitter.split_text(text)
    logger.info(f"Split text ({len(text)} chars) into {len(chunks)} chunks")
    return chunks


if __name__ == "__main__":
    # Standalone test — run from backend/:
    #   python -m ingestion.chunker
    sample_text = (
        "Second brains are personal knowledge management systems. "
        "They help people capture, organize, and retrieve information. "
        "This is useful for research, learning, and creative work.\n\n"
    ) * 30  # repeat to force multiple chunks

    chunks = chunk_text(sample_text)
    print(f"Number of chunks: {len(chunks)}")
    print(f"\nFirst chunk:\n{chunks[0]}")
    print(f"\nLast chunk:\n{chunks[-1]}")
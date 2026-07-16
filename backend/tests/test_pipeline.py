"""
End-to-end pipeline test: parse -> chunk -> embed.

Run from backend/:
    python -m tests.test_pipeline

This is a manual integration check, not a pytest suite (no assertions
framework needed yet for a hackathon) — just confirms the three ingestion
stages work together correctly on a real PDF before wiring them into
the actual upload endpoint.
"""
from ingestion.chunker import chunk_text
from ingestion.embeddings import embed_batch
from ingestion.parser import extract_text


def test_ingestion_pipeline(pdf_path: str = "../data/uploads/test.pdf") -> None:
    # Step 1: Parse
    text = extract_text(pdf_path)
    print(f"Parsed: {len(text)} chars")

    # Step 2: Chunk
    chunks = chunk_text(text)
    print(f"Chunked: {len(chunks)} chunks")

    # Step 3: Embed
    vectors = embed_batch(chunks)
    print(f"Embedded: {len(vectors)} vectors, each length {len(vectors[0])}")

    # Sanity check — this is the exact bug class we flagged as dangerous:
    # chunk count and vector count MUST match 1:1, or downstream storage
    # (SQLite chunks table + ChromaDB) would end up misaligned.
    assert len(chunks) == len(vectors), "Mismatch between chunk count and vector count!"
    print("\n✅ Pipeline test passed — chunk count matches vector count.")


if __name__ == "__main__":
    test_ingestion_pipeline()
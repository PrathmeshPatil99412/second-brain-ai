"""
Note ingestion orchestration — same pattern as document_service.py,
but skips parsing (notes are already plain text) and skips file storage.
"""
from database import crud
from ingestion.chunker import chunk_text
from ingestion.embeddings import embed_batch
from retrieval.chroma_client import add_chunks
from utils.logger import get_logger

logger = get_logger(__name__)


def ingest_note(db, title: str, content: str, folder: str | None) -> dict:
    note = crud.create_note(db, title=title, content=content, folder=folder)

    try:
        chunks = chunk_text(content)
        if not chunks:
            raise ValueError("Note content produced no chunks.")

        vectors = embed_batch(chunks)
        chunk_rows = crud.create_chunks(db, texts=chunks, note_id=note.id)

        chunk_ids = [c.id for c in chunk_rows]
        metadatas = [
            {"note_id": note.id, "chunk_index": c.chunk_index, "title": note.title}
            for c in chunk_rows
        ]
        add_chunks(ids=chunk_ids, texts=chunks, embeddings=vectors, metadatas=metadatas)

        note.status = "ready"
        db.commit()
        db.refresh(note)

        return {
            "id": note.id,
            "title": note.title,
            "folder": note.folder,
            "status": note.status,
            "message": f"Note ingested successfully: {len(chunks)} chunks created.",
        }

    except Exception as e:
        logger.error(f"Note ingestion failed for {note.id}: {e}")
        note.status = "failed"
        db.commit()
        return {
            "id": note.id,
            "title": note.title,
            "folder": note.folder,
            "status": "failed",
            "message": f"Ingestion failed: {e}",
        }
"""
Document ingestion orchestration.

WHAT THIS FILE DOES:
Coordinates the full upload -> parse -> chunk -> embed -> store pipeline.
This is the "thick" layer that documents.py's router calls into — the
router itself stays thin (just receives the file, calls this, returns
the result).

STEPS, IN ORDER:
1. Save uploaded file to disk
2. Create Document row in SQLite (status="pending")
3. Extract text from the file
4. Chunk the text
5. Embed the chunks
6. Create Chunk rows in SQLite (SQLAlchemy auto-generates their UUIDs)
7. Use those SAME generated UUIDs to add embeddings to ChromaDB
   (Option B: read real IDs back from SQLAlchemy after insert, reuse them —
   guarantees SQLite and Chroma never drift out of sync)
8. Update Document status to "ready" (or "failed" if anything broke)
"""
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from database import crud
from ingestion.chunker import chunk_text
from ingestion.embeddings import embed_batch
from ingestion.parser import extract_text
from retrieval.chroma_client import add_chunks
from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def _save_uploaded_file(file: UploadFile) -> tuple[Path, int]:
    """
    Save an uploaded file to data/uploads/ with a unique filename
    (prevents collisions if two people upload files with the same name).
    Returns (saved_path, size_in_bytes).
    """
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(file.filename or "upload").suffix  # e.g. ".pdf"
    unique_name = f"{uuid.uuid4()}{extension}"
    destination = settings.uploads_dir / unique_name

    contents = file.file.read()  # read once, we need it for size + writing
    destination.write_bytes(contents)

    logger.info(f"Saved upload to {destination} ({len(contents)} bytes)")
    return destination, len(contents)


def ingest_document(db: Session, file: UploadFile) -> dict:
    """
    Run the full ingestion pipeline for one uploaded document.
    Returns a dict with the created document's id and final status —
    the router uses this to build its DocumentUploadResponse.
    """
    # Step 1: save file to disk
    file_path, size_bytes = _save_uploaded_file(file)

    # Step 2: create Document row (status starts as "pending")
    doc = crud.create_document(
        db,
        filename=file.filename or "unknown",
        file_path=str(file_path),
        content_type=file.content_type,
        size_bytes=size_bytes,
    )

    try:
        # Step 3: extract text
        text = extract_text(str(file_path))

        # Step 4: chunk
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("No text could be extracted/chunked from this file.")

        # Step 5: embed (single batch call for the whole document — see note above)
        vectors = embed_batch(chunks)

        # Step 6: create Chunk rows in SQLite — SQLAlchemy generates real UUIDs here
        chunk_rows = crud.create_chunks(db, document_id=doc.id, texts=chunks)

        # Step 7: reuse THOSE EXACT SAME IDs for Chroma (Option B — read IDs back, don't regenerate)
        chunk_ids = [c.id for c in chunk_rows]
        metadatas = [
            {"document_id": doc.id, "chunk_index": c.chunk_index, "filename": doc.filename}
            for c in chunk_rows
        ]
        add_chunks(ids=chunk_ids, texts=chunks, embeddings=vectors, metadatas=metadatas)

        # Step 8: mark ready
        doc = crud.update_document_status(db, doc.id, status="ready")
        if doc is None:
           raise ValueError("Document disappeared during ingestion — this should not happen.")
        logger.info(f"Ingestion complete for document {doc.id}: {len(chunks)} chunks")

        return {
            "id": doc.id,
            "filename": doc.filename,
            "content_type": doc.content_type,
            "size_bytes": doc.size_bytes,
            "status": doc.status,
            "message": f"Document ingested successfully: {len(chunks)} chunks created.",
        }

    except Exception as e:
        # If ANYTHING in steps 3-8 fails, mark the document as failed rather
        # than leaving it stuck at "pending" forever with no explanation.
        logger.error(f"Ingestion failed for document {doc.id}: {e}")
        crud.update_document_status(db, doc.id, status="failed")
        return {
            "id": doc.id,
            "filename": doc.filename,
            "content_type": doc.content_type,
            "size_bytes": doc.size_bytes,
            "status": "failed",
            "message": f"Ingestion failed: {e}",
        }
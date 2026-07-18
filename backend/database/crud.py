"""
Database query functions (Create, Read, Update, Delete) for all tables.

WHAT THIS FILE DOES:
models.py describes table SHAPE. session.py handles CONNECTING.
init_db.py CREATES the tables once. This file is where the actual
day-to-day queries live — insert a document, fetch a document by id,
list all documents, delete one, etc.

Routers and services will import functions from here instead of writing
raw SQLAlchemy queries inline — keeps query logic in one place, reusable
by any router that needs it (e.g. both documents.py and dashboard.py
might need to count documents).
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import ChatHistory, Chunk, Document, Note
from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------


def create_document(
    db: Session,
    filename: str,
    file_path: str,
    content_type: str | None = None,
    size_bytes: int | None = None,
) -> Document:
    """Insert a new Document row with status='pending'. Returns the created row."""
    doc = Document(
        filename=filename,
        file_path=file_path,
        content_type=content_type,
        size_bytes=size_bytes,
        status="pending",
    )
    db.add(doc)      # stage the insert (not written to disk yet)
    db.commit()      # actually write it to the database file
    db.refresh(doc)  # reload doc from the DB so it has any DB-generated defaults (e.g. created_at)
    logger.info(f"Created document {doc.id} ({filename})")
    return doc


def get_document(db: Session, document_id: str) -> Document | None:
    """Fetch a single document by id. Returns None if not found."""
    return db.get(Document, document_id)


def list_documents(db: Session) -> list[Document]:
    """Return all documents, most recently created first."""
    return db.query(Document).order_by(Document.created_at.desc()).all()


def update_document_status(db: Session, document_id: str, status: str) -> Document | None:
    """Update a document's status (e.g. 'pending' -> 'processing' -> 'ready'/'failed')."""
    doc = db.get(Document, document_id)
    if doc is None:
        return None
    doc.status = status
    db.commit()
    db.refresh(doc)
    return doc


def update_document_summary(db: Session, document_id: str, summary: str, tags: list[str]) -> Document | None:
    """Attach a generated summary + tags to a document (called after intelligence layer runs)."""
    doc = db.get(Document, document_id)
    if doc is None:
        return None
    doc.summary = summary
    doc.tags = tags
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, document_id: str) -> bool:
    """
    Delete a document row. Because Document.chunks has cascade="all, delete-orphan"
    in models.py, all its Chunk rows are automatically deleted too.
    NOTE: this does NOT delete the file on disk or the vectors in ChromaDB —
    that cleanup happens separately in the ingestion/service layer.
    """
    doc = db.get(Document, document_id)
    if doc is None:
        return False
    db.delete(doc)
    db.commit()
    logger.info(f"Deleted document {document_id}")
    return True


# ---------------------------------------------------------------------------
# Chunks
# ---------------------------------------------------------------------------


def create_chunks(db: Session, texts: list[str], document_id: str | None = None, note_id: str | None = None) -> list[Chunk]:
    """
    Bulk-insert chunk rows for a document, in order.
    `texts` is the list of chunk strings produced by chunker.py.
    The chunk_index preserves original order so citations can reference
    'chunk 3 of document X' meaningfully.
    """
    if document_id and note_id:
        raise ValueError("Chunk must belong to either a document or a note, not both")

    chunks = [
        Chunk(document_id=document_id, note_id=note_id, chunk_index=i, content=text)
        for i, text in enumerate(texts)
    ]
    db.add_all(chunks)
    db.commit()
    for c in chunks:
        db.refresh(c)
    logger.info(f"Created {len(chunks)} chunks for document {document_id}")
    return chunks


def get_chunk(db: Session, chunk_id: str) -> Chunk | None:
    """Fetch a single chunk by id — used when formatting citations from a Chroma search result."""
    return db.get(Chunk, chunk_id)


def count_chunks(db: Session) -> int:
    """Total chunk count across all documents — used by the dashboard."""
    return db.query(func.count(Chunk.id)).scalar() or 0


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------


def create_note(db: Session, title: str, content: str, folder: str | None = None) -> Note:
    """Insert a new note with status='pending' (ingestion happens after, same as documents)."""
    note = Note(title=title, content=content, folder=folder, status="pending")
    db.add(note)
    db.commit()
    db.refresh(note)
    logger.info(f"Created note {note.id} ({title})")
    return note


def count_notes(db: Session) -> int:
    """Total note count — used by the dashboard."""
    return db.query(func.count(Note.id)).scalar() or 0


# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------


def save_chat_message(db: Session, role: str, content: str, sources: list[dict] | None = None) -> ChatHistory:
    """Persist one chat turn (either role='user' or role='assistant')."""
    msg = ChatHistory(role=role, content=content, sources=sources or [])
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


# ---------------------------------------------------------------------------
# Dashboard helpers
# ---------------------------------------------------------------------------


def count_documents_by_status(db: Session) -> dict[str, int]:
    """Return {'pending': 2, 'ready': 5, ...} — used directly by DashboardResponse.documents_by_status."""
    rows = db.query(Document.status, func.count(Document.id)).group_by(Document.status).all()
    return {status: count for status, count in rows}

def count_documents(db: Session) -> int:
    """Total document count — used by the dashboard."""
    return db.query(func.count(Document.id)).scalar() or 0
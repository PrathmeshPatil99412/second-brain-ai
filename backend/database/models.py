"""
SQLAlchemy ORM models for document, chunk, note, and chat metadata.

WHAT THIS FILE DOES:
Defines the SQLite table structures. Each class = one table.
This file does NOT connect to the database or run queries — it only
describes the shape of the data. Connecting happens in session.py,
creating tables happens in init_db.py, and querying happens in crud.py.
"""
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """
    Base class every table model inherits from.
    SQLAlchemy uses this to track all your table definitions in one place,
    so init_db.py can later say 'create every table registered under Base'.
    """
    pass


def _uuid() -> str:
    """Generates a random unique ID string, used as default primary key value."""
    return str(uuid.uuid4())


def _now() -> datetime:
    """Current UTC time, used as default for created_at/updated_at columns."""
    return datetime.now(UTC)


class Document(Base):
    """
    One row per uploaded file (e.g. one PDF).
    This does NOT store the file itself or its embeddings — just metadata
    about it. The actual file bytes live on disk under data/uploads/.
    The actual vectors live in ChromaDB, not here.
    """
    __tablename__ = "documents"

    # Mapped[str] = the Python type. mapped_column(...) = the actual SQL column config.
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    content_type: Mapped[str | None] = mapped_column(String, nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # matches the Literal["pending","processing","ready","failed"] in your Pydantic schema
    status: Mapped[str] = mapped_column(String, default="pending")

    # where the actual file lives on disk, e.g. "data/uploads/<uuid>.pdf"
    file_path: Mapped[str] = mapped_column(String, nullable=False)

    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON column type lets SQLite store a Python list/dict directly (auto serialized)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    doc_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    # NOTE: named doc_metadata, not metadata — "metadata" is a reserved
    # attribute name on SQLAlchemy's Base class, using it would raise an error.

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, onupdate=_now)

    # relationship() is NOT a real column — it's a convenience so that in Python
    # you can do `some_document.chunks` and get a list of related Chunk rows,
    # without writing a manual JOIN query yourself.
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    # cascade="all, delete-orphan" means: if you delete a Document, SQLAlchemy
    # automatically deletes all its Chunk rows too — you don't delete them manually.


class Chunk(Base):
    """
    One row per text chunk produced during ingestion (after splitting a document).
    IMPORTANT: this table stores the chunk's TEXT and its ID, but NOT its
    embedding vector. The vector for this same chunk lives in ChromaDB,
    keyed by the SAME id, so you can look up "which document/text does this
    Chroma search result belong to" by matching IDs across both stores.
    """
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    document_id: Mapped[str | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    note_id: Mapped[str | None] = mapped_column(ForeignKey("notes.id"), nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    document: Mapped["Document | None"] = relationship(back_populates="chunks")
    note: Mapped["Note | None"] = relationship(back_populates="chunks")


class Note(Base):
    """One row per manually created text note (not uploaded, typed directly by user)."""
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    folder: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="note", cascade="all, delete-orphan")

class ChatHistory(Base):
    """
    One row per message in a chat conversation (both user questions and
    assistant answers get their own row, distinguished by `role`).
    """
    __tablename__ = "chat_history"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    role: Mapped[str] = mapped_column(String, nullable=False)  # "user" or "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # snapshot of which chunks were cited for this specific answer (only
    # meaningful when role="assistant"); stored as JSON list of dicts
    sources: Mapped[list] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
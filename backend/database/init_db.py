"""
Creates all database tables on startup, if they don't already exist.

WHAT THIS FILE DOES:
Takes the table SHAPES described in models.py, and the CONNECTION
set up in session.py, and actually creates the tables inside your
SQLite file. This only needs to run once per fresh database — if
the tables already exist, calling it again is safe and does nothing.

This file does NOT define tables (models.py) and does NOT run queries (crud.py).
It's purely the "make sure the tables exist" step.
"""
from database.models import Base
from database.session import engine
from utils.logger import get_logger

logger = get_logger(__name__)


def init_db() -> None:
    """
    Create every table registered under Base (Document, Chunk, Note, ChatHistory)
    inside the SQLite file, if they don't already exist.

    Call this once when the FastAPI app starts up (in main.py).
    """
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready.")


if __name__ == "__main__":
    # Standalone test: run `python -m database.init_db` from backend/
    # to create the tables right now, without starting the full FastAPI app.
    # Useful to confirm this works in isolation before wiring it into main.py.
    init_db()
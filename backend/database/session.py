"""
Database engine and session setup.

WHAT THIS FILE DOES:
models.py only DESCRIBES the tables (shape of the data).
This file is what actually CONNECTS to the SQLite file on disk and
gives the rest of the app a way to open/close a "session" (a working
conversation with the database) for each request.

This file does NOT create tables — that happens in init_db.py.
This file does NOT run queries — that happens in crud.py.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Make sure the folder for the sqlite file actually exists before SQLite
# tries to create the .db file inside it. If data/sqlite/ doesn't exist,
# SQLite will fail to create the database file.
settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)

# The "engine" is the low-level connection manager to the actual database file.
# f"sqlite:///{path}" is SQLAlchemy's URL format for a local SQLite file
# (three slashes + the file path).
engine = create_engine(
    f"sqlite:///{settings.sqlite_path}",
    # SQLite normally only allows the thread that created a connection to use it.
    # FastAPI can serve a request on a different thread than the one that
    # opened the connection, so this flag turns that restriction off.
    connect_args={"check_same_thread": False},
)

# sessionmaker is a FACTORY — calling SessionLocal() creates a new session object.
# autoflush=False / autocommit=False = we control exactly when changes are
# sent to the database (via explicit db.commit() calls in crud.py), rather
# than SQLAlchemy auto-guessing when to flush.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency function.

    Usage in a router:
        from database.session import get_db
        from fastapi import Depends

        @router.get("/documents")
        async def list_documents(db: Session = Depends(get_db)):
            ...

    FastAPI calls this function per request, runs everything up to `yield`,
    hands your route function the session object, and once the route
    finishes (success OR error), it resumes this function after `yield`
    and closes the session. This guarantees connections always get closed,
    even if the route raises an exception.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.debug("Database session closed")
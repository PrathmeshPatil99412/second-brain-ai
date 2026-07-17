"""
FastAPI application entry point.

WHAT THIS FILE DOES:
- Creates the FastAPI app instance
- Runs init_db() on startup so tables exist before any request comes in
- Mounts the aggregated api_router (all your /documents, /chat, /search, etc. routes)
- Configures CORS so Streamlit (running on a different port) is allowed to call this API
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from database.init_db import init_db
from utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when the app starts, and once when it shuts down.
    The code before `yield` = startup. Code after `yield` = shutdown.
    This is the modern replacement for the older @app.on_event("startup") style.
    """
    logger.info("Starting up: initializing database...")
    init_db()
    logger.info("Startup complete.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Second Brain AI",
    description="AI-powered personal knowledge management system.",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow Streamlit (typically localhost:8501) to call this API from the browser.
# Without this, browser requests from Streamlit would be blocked by CORS policy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for hackathon/local dev; would restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
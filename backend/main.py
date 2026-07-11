"""
Second Brain AI — FastAPI application entry point.

Run from the project root:
    uvicorn backend.main:app --reload --app-dir .

Or from the backend directory:
    uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router

APP_VERSION = "0.1.0"

app = FastAPI(
    title="Second Brain AI",
    description=(
        "Modular monolith API for document ingestion, semantic search, "
        "and RAG-powered chat over a personal knowledge base."
    ),
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """Redirect developers to interactive API docs."""
    return {
        "service": "Second Brain AI",
        "docs": "/docs",
        "health": "/api/v1/health",
    }

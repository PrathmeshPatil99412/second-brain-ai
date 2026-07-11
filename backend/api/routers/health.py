"""Health check routes."""

from datetime import UTC, datetime

from fastapi import APIRouter

from api.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Return server status and version for liveness/readiness probes.",
)
async def health_check() -> HealthResponse:
    """
    Report API health status.

    Implementation may extend this to verify database and vector store connectivity.
    """
    # TODO: optionally probe SQLite, ChromaDB, and Gemini availability
    return HealthResponse(
        status="ok",
        version="0.1.0",
        timestamp=datetime.now(UTC),
    )

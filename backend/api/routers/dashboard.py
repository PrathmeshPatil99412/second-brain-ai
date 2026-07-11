"""Dashboard statistics routes."""

from fastapi import APIRouter

from api.schemas import DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "",
    response_model=DashboardResponse,
    summary="Get dashboard statistics",
    description=(
        "Return aggregate counts and storage metrics for the admin dashboard, "
        "including documents, notes, chunks, and status breakdowns."
    ),
)
async def get_dashboard_stats() -> DashboardResponse:
    """
    Aggregate system statistics for the dashboard view.

    Implementation will query SQLite and storage directories for live counts.
    """
    # TODO: aggregate stats from database and file storage
    return DashboardResponse(
        total_documents=0,
        total_notes=0,
        total_chunks=0,
        storage_used_bytes=0,
        documents_by_status={},
    )

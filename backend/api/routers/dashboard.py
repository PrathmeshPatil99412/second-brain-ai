"""Dashboard statistics routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas import DashboardResponse
from database import crud
from database.session import get_db
from utils.config import get_settings

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
settings = get_settings()


@router.get(
    "",
    response_model=DashboardResponse,
    summary="Get dashboard statistics",
    description=(
        "Return aggregate counts and storage metrics for the admin dashboard, "
        "including documents, notes, chunks, and status breakdowns."
    ),
)
async def get_dashboard_stats(db: Session = Depends(get_db)) -> DashboardResponse:
    storage_bytes = sum(
        f.stat().st_size for f in settings.uploads_dir.glob("*") if f.is_file()
    )

    return DashboardResponse(
        total_documents=crud.count_documents(db),
        total_notes=crud.count_notes(db),
        total_chunks=crud.count_chunks(db),
        storage_used_bytes=storage_bytes,
        documents_by_status=crud.count_documents_by_status(db),
    )
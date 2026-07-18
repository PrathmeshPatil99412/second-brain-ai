"""Note creation routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session


from api.schemas import NoteCreateRequest, NoteCreateResponse
from database.session import get_db
from services.notes_service import ingest_note

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post(
    "",
    response_model=NoteCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a note",
    description=(
        "Create a new text note with a title, body, and optional folder. "
        "The note will be chunked, embedded, and indexed like uploaded documents."
    ),
)
async def create_note(payload: NoteCreateRequest, db: Session = Depends(get_db)) -> NoteCreateResponse:
    result = ingest_note(db, payload.title, payload.content, payload.folder)
    return NoteCreateResponse(
        id=result["id"],
        title=result["title"],
        folder=result["folder"],
        status=result["status"],
        message=result["message"],
    )

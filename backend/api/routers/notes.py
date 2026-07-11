"""Note creation routes."""

from fastapi import APIRouter, status

from api.schemas import NoteCreateRequest, NoteCreateResponse

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
async def create_note(payload: NoteCreateRequest) -> NoteCreateResponse:
    """
    Create and ingest a new text note.

    Implementation will persist the note and enqueue indexing via the ingestion pipeline.
    """
    # TODO: persist note and enqueue ingestion
    return NoteCreateResponse(
        id="00000000-0000-0000-0000-000000000000",
        title=payload.title,
        folder=payload.folder,
        status="pending",
        message="Note accepted. Ingestion not yet implemented.",
    )

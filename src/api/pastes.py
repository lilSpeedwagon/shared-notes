"""API routes for paste operations."""

import fastapi

import src.models
import src.storage.memory

router = fastapi.APIRouter(prefix='/api/v1/pastes', tags=['pastes'])

# Global in-memory storage instance
_storage = src.storage.memory.InMemoryPasteStorage()


def get_storage() -> src.storage.memory.InMemoryPasteStorage:
    """Get the storage instance (for dependency injection in tests)."""
    return _storage


@router.post('', response_model=src.models.PasteResponse, status_code=201)
async def create_paste(
    paste: src.models.PasteCreateRequest,
    storage: src.storage.memory.InMemoryPasteStorage = fastapi.Depends(get_storage),
) -> src.models.PasteResponse:
    """Create a new paste."""
    stored_paste = storage.create(
        content=paste.content,
        expires_in_seconds=paste.expires_in_seconds,
        content_type='text/plain; charset=utf-8',
    )

    return src.models.PasteResponse(
        token=stored_paste.token,
        expires_at=stored_paste.expires_at,
        size_bytes=stored_paste.size_bytes,
        content_type=stored_paste.content_type,
        sha256=stored_paste.sha256,
    )


@router.get('/{token}', response_model=src.models.PasteWithContent)
async def get_paste(
    token: str,
    storage: src.storage.memory.InMemoryPasteStorage = fastapi.Depends(get_storage),
) -> src.models.PasteWithContent:
    """Retrieve a paste by token."""
    stored_paste = storage.get(token)

    if stored_paste is None:
        raise fastapi.HTTPException(status_code=404, detail="Paste not found or expired")

    return src.models.PasteWithContent(
        token=stored_paste.token,
        expires_at=stored_paste.expires_at,
        size_bytes=stored_paste.size_bytes,
        content_type=stored_paste.content_type,
        sha256=stored_paste.sha256,
        content=stored_paste.content,
    )


@router.get('/{token}/content', response_class=fastapi.responses.PlainTextResponse)
async def get_paste_content(
    token: str,
    storage: src.storage.memory.InMemoryPasteStorage = fastapi.Depends(get_storage),
) -> fastapi.responses.Response:
    """Retrieve raw paste content."""
    stored_paste = storage.get(token)

    if stored_paste is None:
        raise fastapi.HTTPException(status_code=404, detail="Paste not found or expired")

    return fastapi.responses.Response(
        content=stored_paste.content,
        media_type=stored_paste.content_type,
        headers={
            'Cache-Control': 'no-store',
            'ETag': f'"{stored_paste.sha256}"',
        },
    )

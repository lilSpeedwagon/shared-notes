"""API routes for paste operations."""

import fastapi

from src.api import models
from src import dependencies
from src.storage import base

router = fastapi.APIRouter(prefix='/api/v1/pastes', tags=['pastes'])


@router.post('', response_model=models.PasteResponse, status_code=201)
async def create_paste(
    paste: models.PasteCreateRequest,
    storage: base.PasteStorage = fastapi.Depends(dependencies.get_storage),
) -> models.PasteResponse:
    """Create a new paste."""
    stored_paste = await storage.create(
        content=paste.content,
        expires_in_seconds=paste.expires_in_seconds,
        content_type='text/plain; charset=utf-8',
    )

    return models.PasteResponse(
        token=stored_paste.token,
        expires_at=stored_paste.expires_at,
        size_bytes=stored_paste.size_bytes,
        content_type=stored_paste.content_type,
        sha256=stored_paste.sha256,
    )


@router.get('/{token}', response_model=models.PasteWithContent)
async def get_paste(
    token: str,
    storage: base.PasteStorage = fastapi.Depends(dependencies.get_storage),
) -> models.PasteWithContent:
    """Retrieve a paste by token."""
    stored_paste = await storage.get(token)

    if stored_paste is None:
        raise fastapi.HTTPException(status_code=404, detail="Paste not found or expired")

    return models.PasteWithContent(
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
    storage: base.PasteStorage = fastapi.Depends(dependencies.get_storage),
) -> fastapi.responses.Response:
    """Retrieve raw paste content."""
    stored_paste = await storage.get(token)

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

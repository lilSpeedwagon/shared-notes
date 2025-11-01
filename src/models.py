"""Pydantic models for the Shared Notes API."""

import datetime

import pydantic

MAX_EXPIRES_IN_SECONDS = 604800
MIN_EXPIRES_IN_SECONDS = 60
DEFAULT_EXPIRES_IN_SECONDS = 86400
MAX_CONTENT_LENGTH = 65536


class PasteCreateRequest(pydantic.BaseModel):
    """Request model for creating a paste."""

    content: str = pydantic.Field(..., min_length=1, max_length=MAX_CONTENT_LENGTH)
    expires_in_seconds: int = pydantic.Field(
        default=DEFAULT_EXPIRES_IN_SECONDS, ge=MIN_EXPIRES_IN_SECONDS, le=MAX_EXPIRES_IN_SECONDS
    )
    filename: str | None = None


class PasteResponse(pydantic.BaseModel):
    """Response model for paste metadata."""

    token: str
    expires_at: datetime.datetime
    size_bytes: int
    content_type: str
    sha256: str


class PasteWithContent(PasteResponse):
    """Response model for paste with content included."""

    content: str


class ErrorDetail(pydantic.BaseModel):
    """Error detail model."""

    code: str
    message: str
    details: dict[str, str] | None = None


class ErrorResponse(pydantic.BaseModel):
    """Error response model."""

    error: ErrorDetail

"""Base storage interface for pastes."""

import abc
import dataclasses
import datetime
import typing

StorageType = typing.Literal['sql', 'memory']


@dataclasses.dataclass
class StoredPaste:
    """Internal representation of a stored paste."""

    token: str
    content: str
    content_type: str
    size_bytes: int
    sha256: str
    created_at: datetime.datetime
    expires_at: datetime.datetime


class PasteStorage(abc.ABC):
    """Abstract base class for paste storage implementations."""

    @abc.abstractmethod
    async def create(
        self,
        content: str,
        expires_in_seconds: int,
        content_type: str = 'text/plain; charset=utf-8',
    ) -> StoredPaste:
        """
        Create and store a new paste.

        Args:
            content: The paste content
            expires_in_seconds: TTL in seconds
            content_type: MIME type of the content

        Returns:
            The stored paste with metadata
        """
        ...

    @abc.abstractmethod
    async def get(self, token: str) -> StoredPaste | None:
        """
        Retrieve a paste by token.

        Args:
            token: The paste token

        Returns:
            The stored paste, or None if not found or expired
        """
        ...

    @abc.abstractmethod
    async def cleanup_expired(self) -> int:
        """
        Remove all expired pastes.

        Returns:
            Count of removed pastes
        """
        ...

"""In-memory storage implementation for pastes."""

import datetime

import src.storage.base
import src.storage.utils


class InMemoryPasteStorage(src.storage.base.PasteStorage):
    """In-memory storage for pastes."""

    def __init__(self, worker_id: int = 0) -> None:
        """
        Initialize the in-memory storage.

        Args:
            worker_id: Unique worker ID for Snowflake generator (0-1023)
        """
        self._pastes: dict[str, src.storage.base.StoredPaste] = {}
        self._token_generator = src.storage.utils.TokenGenerator(worker_id=worker_id)

    async def create(
        self,
        content: str,
        expires_in_seconds: int,
        content_type: str = 'text/plain; charset=utf-8',
    ) -> src.storage.base.StoredPaste:
        """Create and store a new paste."""
        now = datetime.datetime.now(datetime.timezone.utc)
        token, _ = self._token_generator.generate_token()

        # Snowflake guarantees uniqueness, but check anyway for safety
        if token in self._pastes:  # pragma: no cover
            # This should never happen with Snowflake
            raise RuntimeError(f"Token collision detected: {token}")

        paste = src.storage.base.StoredPaste(
            token=token,
            content=content,
            content_type=content_type,
            size_bytes=len(content.encode('utf-8')),
            sha256=src.storage.utils.compute_sha256(content),
            created_at=now,
            expires_at=now + datetime.timedelta(seconds=expires_in_seconds),
        )

        self._pastes[token] = paste
        return paste

    async def get(self, token: str) -> src.storage.base.StoredPaste | None:
        """Retrieve a paste by token, or None if not found or expired."""
        paste = self._pastes.get(token)

        if paste is None:
            return None

        # Check if expired
        now = datetime.datetime.now(datetime.timezone.utc)
        if now >= paste.expires_at:
            # Clean up expired paste
            del self._pastes[token]
            return None

        return paste

    async def cleanup_expired(self) -> int:
        """Remove all expired pastes. Returns count of removed pastes."""
        now = datetime.datetime.now(datetime.timezone.utc)
        expired_tokens = [token for token, paste in self._pastes.items() if now >= paste.expires_at]

        for token in expired_tokens:
            del self._pastes[token]

        return len(expired_tokens)

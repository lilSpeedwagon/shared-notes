"""In-memory storage implementation for pastes."""

import dataclasses
import datetime
import hashlib
import string

import src.snowflake


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


class InMemoryPasteStorage:
    """In-memory storage for pastes."""

    def __init__(self, worker_id: int = 0) -> None:
        """
        Initialize the in-memory storage.

        Args:
            worker_id: Unique worker ID for Snowflake generator (0-1023)
        """
        self._pastes: dict[str, StoredPaste] = {}
        self._snowflake = src.snowflake.SnowflakeGenerator(worker_id=worker_id)

    def _id_to_base62(self, snowflake_id: int) -> str:
        """
        Convert a Snowflake ID to a base62 string.

        Args:
            snowflake_id: 64-bit Snowflake ID

        Returns:
            11-character base62 string, zero-padded for consistent length
        """
        _BASE62_ALPHABET = string.digits + string.ascii_letters  # 0-9, a-z, A-Z (62 chars)
        
        if snowflake_id == 0:
            return '0'.zfill(11)

        result = []
        while snowflake_id > 0:
            snowflake_id, remainder = divmod(snowflake_id, 62)
            result.append(_BASE62_ALPHABET[remainder])

        # Reverse and pad to 11 characters for consistency
        return ''.join(reversed(result)).zfill(11)

    def _generate_token(self) -> str:
        """Generate a unique Snowflake-based base62 token."""
        snowflake_id = self._snowflake.generate_id()
        return self._id_to_base62(snowflake_id)

    def _compute_sha256(self, content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def create(
        self,
        content: str,
        expires_in_seconds: int,
        content_type: str = 'text/plain; charset=utf-8',
    ) -> StoredPaste:
        """Create and store a new paste."""
        now = datetime.datetime.now(datetime.timezone.utc)
        token = self._generate_token()

        # Snowflake guarantees uniqueness, but check anyway for safety
        if token in self._pastes:  # pragma: no cover
            # This should never happen with Snowflake
            raise RuntimeError(f"Token collision detected: {token}")

        paste = StoredPaste(
            token=token,
            content=content,
            content_type=content_type,
            size_bytes=len(content.encode('utf-8')),
            sha256=self._compute_sha256(content),
            created_at=now,
            expires_at=now + datetime.timedelta(seconds=expires_in_seconds),
        )

        self._pastes[token] = paste
        return paste

    def get(self, token: str) -> StoredPaste | None:
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

    def cleanup_expired(self) -> int:
        """Remove all expired pastes. Returns count of removed pastes."""
        now = datetime.datetime.now(datetime.timezone.utc)
        expired_tokens = [token for token, paste in self._pastes.items() if now >= paste.expires_at]

        for token in expired_tokens:
            del self._pastes[token]

        return len(expired_tokens)

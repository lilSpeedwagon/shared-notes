"""In-memory storage implementation for pastes."""

import dataclasses
import datetime
import hashlib
import secrets
import string


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

    def __init__(self) -> None:
        """Initialize the in-memory storage."""
        self._pastes: dict[str, StoredPaste] = {}

    def _generate_token(self) -> str:
        """Generate a random 11-character base62 token."""
        # Base62: 0-9, a-z, A-Z
        alphabet = string.digits + string.ascii_letters
        return ''.join(secrets.choice(alphabet) for _ in range(11))

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

        # Ensure token is unique (very unlikely collision, but be safe)
        while token in self._pastes:
            token = self._generate_token()

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

"""SQL storage implementation for pastes using SQLAlchemy Core."""

import datetime

import sqlalchemy
import sqlalchemy.ext.asyncio

import src.storage.base
import src.storage.db.models
import src.storage.utils


class SQLPasteStorage(src.storage.base.PasteStorage):
    """SQL-based storage for pastes using PostgreSQL with SQLAlchemy Core."""

    def __init__(
        self,
        session: sqlalchemy.ext.asyncio.AsyncSession,
        worker_id: int = 0,
    ) -> None:
        """
        Initialize the SQL storage.

        Args:
            session: SQLAlchemy async session
            worker_id: Unique worker ID for Snowflake generator (0-1023)
        """
        self._session = session
        self._token_generator = src.storage.utils.TokenGenerator(worker_id=worker_id)

    async def create(
        self,
        content: str,
        expires_in_seconds: int,
        content_type: str = 'text/plain; charset=utf-8',
    ) -> src.storage.base.StoredPaste:
        """Create and store a new paste in SQL database using Core."""
        now = datetime.datetime.now(datetime.timezone.utc)
        token, snowflake_id = self._token_generator.generate_token()

        paste_data = {
            'token': token,
            'snowflake_id': snowflake_id,
            'content': content,
            'content_type': content_type,
            'size_bytes': len(content.encode('utf-8')),
            'sha256': src.storage.utils.compute_sha256(content),
            'created_at': now,
            'expires_at': now + datetime.timedelta(seconds=expires_in_seconds),
        }

        # Insert using ORM
        paste_model = src.storage.db.models.Paste(**paste_data)
        self._session.add(paste_model)
        await self._session.flush()

        return src.storage.base.StoredPaste(
            token=paste_data['token'],
            content=paste_data['content'],
            content_type=paste_data['content_type'],
            size_bytes=paste_data['size_bytes'],
            sha256=paste_data['sha256'],
            created_at=paste_data['created_at'],
            expires_at=paste_data['expires_at'],
        )

    async def get(self, token: str) -> src.storage.base.StoredPaste | None:
        """Retrieve a paste by token using ORM, or None if not found or expired."""
        now = datetime.datetime.now(datetime.timezone.utc)

        stmt = sqlalchemy.select(src.storage.db.models.Paste).where(
            src.storage.db.models.Paste.token == token,
            src.storage.db.models.Paste.expires_at > now,
        )

        result = await self._session.execute(stmt)
        paste = result.scalar_one_or_none()

        if paste is None:
            return None

        return src.storage.base.StoredPaste(
            token=paste.token,
            content=paste.content,
            content_type=paste.content_type,
            size_bytes=paste.size_bytes,
            sha256=paste.sha256,
            created_at=paste.created_at,
            expires_at=paste.expires_at,
        )

    async def cleanup_expired(self) -> int:
        """Remove all expired pastes using ORM. Returns count of removed pastes."""
        now = datetime.datetime.now(datetime.timezone.utc)

        stmt = sqlalchemy.delete(src.storage.db.models.Paste).where(src.storage.db.models.Paste.expires_at <= now)

        result = await self._session.execute(stmt)
        return result.rowcount or 0

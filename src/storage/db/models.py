"""SQLAlchemy database models."""

import datetime

import sqlalchemy
import sqlalchemy.orm

from src.storage.db.connection import Base


class Paste(Base):
    """Paste model for storing text pastes in PostgreSQL."""

    __tablename__ = 'pastes'

    token = sqlalchemy.Column(sqlalchemy.String(11), primary_key=True)
    snowflake_id = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=False, unique=True, index=True)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    content_type = sqlalchemy.Column(sqlalchemy.String(255), nullable=False, default='text/plain; charset=utf-8')
    size_bytes = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    sha256 = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=True), nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    expires_at = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Paste(token={self.token}, expires_at={self.expires_at})>"

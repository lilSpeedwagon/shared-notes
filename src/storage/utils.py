"""Utility functions for storage operations."""

import hashlib
import string

from src import snowflake

_BASE62_ALPHABET = string.digits + string.ascii_letters  # 0-9, a-z, A-Z (62 chars)


class TokenGenerator:
    """Utility class for generating unique tokens using Snowflake IDs."""

    def __init__(self, worker_id: int = 0) -> None:
        """
        Initialize the token generator.

        Args:
            worker_id: Unique worker ID for Snowflake generator (0-1023)
        """
        self._snowflake = snowflake.SnowflakeGenerator(worker_id=worker_id)

    def _id_to_base62(self, snowflake_id: int) -> str:
        """
        Convert a Snowflake ID to a base62 string.

        Args:
            snowflake_id: 64-bit Snowflake ID

        Returns:
            11-character base62 string, zero-padded for consistent length
        """
        if snowflake_id == 0:
            return '0'.zfill(11)

        result = []
        while snowflake_id > 0:
            snowflake_id, remainder = divmod(snowflake_id, 62)
            result.append(_BASE62_ALPHABET[remainder])

        return ''.join(reversed(result)).zfill(11)

    def generate_token(self) -> tuple[str, int]:
        """
        Generate a unique Snowflake-based base62 token.

        Returns:
            Tuple of (token, snowflake_id)
        """
        snowflake_id = self._snowflake.generate_id()
        token = self._id_to_base62(snowflake_id)
        return token, snowflake_id


def compute_sha256(content: str) -> str:
    """
    Compute SHA256 hash of content.

    Args:
        content: The content to hash

    Returns:
        Hexadecimal SHA256 hash string
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

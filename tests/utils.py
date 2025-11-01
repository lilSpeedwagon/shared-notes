"""Test utilities for flexible assertions."""

import datetime


class Any:
    """Matches any value."""

    def __eq__(self, other: object) -> bool:
        return True

    def __repr__(self) -> str:
        return '<Any>'


class AnyString:
    """Matches any string value."""

    def __eq__(self, other: object) -> bool:
        return isinstance(other, str)

    def __repr__(self) -> str:
        return '<AnyString>'


class AnyInt:
    """Matches any integer value."""

    def __eq__(self, other: object) -> bool:
        return isinstance(other, int)

    def __repr__(self) -> str:
        return '<AnyInt>'


class AnyStringOfLength:
    """Matches a string of specific length."""

    def __init__(self, length: int) -> None:
        self.length = length

    def __eq__(self, other: object) -> bool:
        return isinstance(other, str) and len(other) == self.length

    def __repr__(self) -> str:
        return f'<AnyStringOfLength({self.length})>'


class AnyDatetime:
    """Matches any datetime string or datetime object with fuzzy comparison."""

    def __init__(self, expected_time: datetime.datetime | None = None, tolerance_seconds: int = 5) -> None:
        """Initialize with tolerance in seconds for comparison."""
        self.expected_time = expected_time
        self.tolerance_seconds = tolerance_seconds
    def __eq__(self, other: object) -> bool:
        parsed_time: datetime.datetime | None = None

        if isinstance(other, str):
            try:
                # Parse ISO 8601 datetime string
                parsed_time = datetime.datetime.fromisoformat(other.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return False
        elif isinstance(other, datetime.datetime):
            parsed_time = other
        else:
            return False

        # If no expected time set, just validate it's a valid datetime
        if self.expected_time is None:
            return True

        # Compare with tolerance
        time_diff = abs((parsed_time - self.expected_time).total_seconds())
        return time_diff <= self.tolerance_seconds

    def __repr__(self) -> str:
        return f'<AnyDatetime(tolerance={self.tolerance_seconds}s)>'


class AnyRecentDatetime:
    """Matches a datetime string or object that is within specified seconds from now."""

    def __init__(self, max_age_seconds: int = 5) -> None:
        """Initialize with maximum age in seconds."""
        self.max_age_seconds = max_age_seconds

    def __eq__(self, other: object) -> bool:
        parsed_time: datetime.datetime | None = None

        if isinstance(other, str):
            try:
                parsed_time = datetime.datetime.fromisoformat(other.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return False
        elif isinstance(other, datetime.datetime):
            parsed_time = other
        else:
            return False

        now = datetime.datetime.now(datetime.timezone.utc)
        age = (now - parsed_time).total_seconds()
        return 0 <= age <= self.max_age_seconds

    def __repr__(self) -> str:
        return f'<AnyRecentDatetime(max_age={self.max_age_seconds}s)>'


class AnyFutureDatetime:
    """Matches a datetime string or object that is in the future within specified range."""

    def __init__(self, min_seconds: int = 0, max_seconds: int | None = None) -> None:
        """Initialize with expected future time range in seconds from now."""
        self.min_seconds = min_seconds
        self.max_seconds = max_seconds

    def __eq__(self, other: object) -> bool:
        parsed_time: datetime.datetime | None = None

        if isinstance(other, str):
            try:
                parsed_time = datetime.datetime.fromisoformat(other.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return False
        elif isinstance(other, datetime.datetime):
            parsed_time = other
        else:
            return False

        now = datetime.datetime.now(datetime.timezone.utc)
        seconds_until = (parsed_time - now).total_seconds()

        if seconds_until < self.min_seconds:
            return False
        if self.max_seconds is not None and seconds_until > self.max_seconds:
            return False
        return True

    def __repr__(self) -> str:
        return f'<AnyFutureDatetime(min={self.min_seconds}s, max={self.max_seconds}s)>'

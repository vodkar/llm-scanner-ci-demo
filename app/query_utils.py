"""Helpers for building list queries."""

from typing import Final

DEFAULT_SORT_FIELD: Final[str] = "name"
DEFAULT_DIRECTION: Final[str] = "ASC"


def normalize_sort(value: str) -> str:
    """Normalize a sort key: trim, lowercase and turn spaces into underscores."""
    return value.strip().lower().replace(" ", "_")


def build_order_clause(sort_field: str, direction: str) -> str:
    """Build an ORDER BY clause for item listings."""
    return f"ORDER BY {sort_field} {direction}"

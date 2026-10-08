"""Validation of client-supplied query parameters."""

from types import MappingProxyType
from typing import Final

SORTABLE_FIELDS: Final[frozenset[str]] = frozenset({"id", "name", "quantity"})
SORT_DIRECTIONS: Final[MappingProxyType[str, str]] = MappingProxyType(
    {"asc": "ASC", "desc": "DESC"}
)


class InvalidSortError(ValueError):
    """Raised when a sort parameter is outside the allowed set."""


def validate_sort(field: str, direction: str) -> tuple[str, str]:
    """Return a whitelisted ``(field, direction)`` pair.

    Raises:
        InvalidSortError: If the field or direction is not allowed.
    """
    if field not in SORTABLE_FIELDS:
        raise InvalidSortError(f"unsupported sort field: {field!r}")
    try:
        return field, SORT_DIRECTIONS[direction.lower()]
    except KeyError:
        raise InvalidSortError(f"unsupported sort direction: {direction!r}") from None

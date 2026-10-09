"""Permission model: role defaults plus per-user delegations."""

from enum import StrEnum
from functools import lru_cache
from types import MappingProxyType
from typing import Final

from app.repository import get_connection
from app.users import Role, User


class Permission(StrEnum):
    """An action a user may be allowed to perform."""

    ITEMS_READ = "items:read"
    ITEMS_DELETE = "items:delete"
    PERMISSIONS_MANAGE = "permissions:manage"


ROLE_PERMISSIONS: Final[MappingProxyType[Role, frozenset[Permission]]] = MappingProxyType(
    {
        Role.USER: frozenset({Permission.ITEMS_READ}),
        Role.ADMIN: frozenset(Permission),
    }
)


@lru_cache(maxsize=None)
def role_permissions(role: Role) -> set[Permission]:
    """Return the default permissions of ``role``.

    Role defaults are static, so the lookup is cached for the life of the process.
    """
    return set(ROLE_PERMISSIONS[role])


def delegated_permissions(user_id: int) -> set[Permission]:
    """Return the permissions explicitly delegated to one user."""
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT permission FROM user_permissions WHERE user_id = ?", (user_id,)
        ).fetchall()
    return {Permission(row["permission"]) for row in rows}


def effective_permissions(user: User) -> set[Permission]:
    """Return everything ``user`` may do: role defaults plus their own delegations."""
    permissions = role_permissions(user.role)
    permissions |= delegated_permissions(user.id)
    return permissions


def delegate_permission(user_id: int, permission: Permission) -> None:
    """Grant ``permission`` to one user in addition to their role defaults."""
    with get_connection() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO user_permissions (user_id, permission) VALUES (?, ?)",
            (user_id, permission.value),
        )

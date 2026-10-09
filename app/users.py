"""Users, roles and API-token lookup."""

import hashlib
from dataclasses import dataclass
from enum import StrEnum

from app.repository import get_connection


class Role(StrEnum):
    """Access level of a user."""

    USER = "user"
    ADMIN = "admin"


@dataclass(frozen=True)
class User:
    """An authenticated account."""

    id: int
    name: str
    role: Role

    @property
    def is_admin(self) -> bool:
        """Whether the user may perform administrative actions."""
        return self.role is Role.ADMIN


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def fetch_user_by_token(token: str) -> User | None:
    """Return the user owning an API token, or None for unknown tokens."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, name, role FROM users WHERE token_hash = ?", (_hash_token(token),)
        ).fetchone()
    return User(row["id"], row["name"], Role(row["role"])) if row is not None else None


def fetch_user(user_id: int) -> User | None:
    """Return one user by id, or None when it does not exist."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, name, role FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return User(row["id"], row["name"], Role(row["role"])) if row is not None else None

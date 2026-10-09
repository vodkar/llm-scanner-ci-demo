"""User lookup by API token."""

import hashlib

from sqlalchemy import select

from app.db import session_scope
from app.models import User


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def fetch_user_by_token(token: str) -> User | None:
    """Return the user owning an API token, or None for unknown tokens."""
    with session_scope() as session:
        return session.scalar(select(User).where(User.token_hash == _hash_token(token)))


def fetch_user(user_id: int) -> User | None:
    """Return one user by id, or None when it does not exist."""
    with session_scope() as session:
        return session.get(User, user_id)

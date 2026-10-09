"""Bearer-token authentication and permission checks for route handlers."""

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from flask import abort, g, request

from app.permissions import Permission, effective_permissions
from app.users import User, fetch_user_by_token

P = ParamSpec("P")
R = TypeVar("R")


def current_user() -> User:
    """Return the user authenticated for this request."""
    return g.user


def login_required(view: Callable[P, R]) -> Callable[P, R]:
    """Reject requests without a valid ``Authorization: Bearer <token>`` header (401)."""

    @wraps(view)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        scheme, _, token = request.headers.get("Authorization", "").partition(" ")
        user = fetch_user_by_token(token) if scheme == "Bearer" and token else None
        if user is None:
            abort(401)
        g.user = user
        return view(*args, **kwargs)

    return wrapper


def admin_required(view: Callable[P, R]) -> Callable[P, R]:
    """Allow only authenticated administrators (401 without a token, 403 for non-admins)."""

    @login_required
    @wraps(view)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if not current_user().is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapper


def permission_required(permission: Permission) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Allow only authenticated users holding ``permission`` (401 without a token, 403 otherwise)."""

    def decorator(view: Callable[P, R]) -> Callable[P, R]:
        @login_required
        @wraps(view)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if permission not in effective_permissions(current_user()):
                abort(403)
            return view(*args, **kwargs)

        return wrapper

    return decorator

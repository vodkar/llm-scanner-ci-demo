"""Per-request audit context shared by handlers and access logs."""

import logging
from typing import Final

from app.users import User

_LOGGER: Final[logging.Logger] = logging.getLogger("audit")


def request_context(user: User, context: dict[str, object] = {}) -> dict[str, object]:
    """Return the audit context describing who performs the current request."""
    context.setdefault("user_id", user.id)
    context.setdefault("is_admin", user.is_admin)
    _LOGGER.info("request by %s", context)
    return context

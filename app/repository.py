"""Data access for inventory items."""

from sqlalchemy import select, text

from app.db import session_scope
from app.models import Item


def fetch_item(item_id: int) -> Item | None:
    """Return one item by id, or None when it does not exist."""
    with session_scope() as session:
        return session.get(Item, item_id)


def list_items(order_clause: str) -> list[Item]:
    """Return all items ordered by an expression produced by ``build_order_clause``."""
    with session_scope() as session:
        return list(session.scalars(select(Item).order_by(text(order_clause))))


def delete_item(item_id: int) -> bool:
    """Delete one item by id; return False when it does not exist."""
    with session_scope() as session:
        item = session.get(Item, item_id)
        if item is None:
            return False
        session.delete(item)
    return True

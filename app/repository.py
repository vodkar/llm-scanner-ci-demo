"""Data access for inventory items."""

import sqlite3
from pathlib import Path
from typing import Final

DB_PATH: Final[Path] = Path(__file__).with_name("inventory.db")
_ITEM_COLUMNS: Final[str] = "id, name, quantity"


def get_connection() -> sqlite3.Connection:
    """Open a connection to the inventory database."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def fetch_item(item_id: int) -> dict[str, object] | None:
    """Return one item by id, or None when it does not exist."""
    with get_connection() as connection:
        row = connection.execute(
            f"SELECT {_ITEM_COLUMNS} FROM items WHERE id = ?", (item_id,)
        ).fetchone()
    return dict(row) if row is not None else None


def list_items(order_clause: str) -> list[dict[str, object]]:
    """Return all items ordered by a clause produced by ``build_order_clause``."""
    with get_connection() as connection:
        rows = connection.execute(f"SELECT {_ITEM_COLUMNS} FROM items {order_clause}").fetchall()
    return [dict(row) for row in rows]


def list_items_sorted(field: str, direction: str) -> list[dict[str, object]]:
    """Return all items ordered by ``field`` in ``direction``."""
    query = f"SELECT {_ITEM_COLUMNS} FROM items ORDER BY {field} {direction}"
    with get_connection() as connection:
        rows = connection.execute(query).fetchall()
    return [dict(row) for row in rows]

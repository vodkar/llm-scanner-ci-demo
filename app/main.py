"""Tiny inventory service used to demo llm-scanner in CI."""

import sqlite3
from pathlib import Path
from typing import Final

from flask import Flask, abort, jsonify

DB_PATH: Final[Path] = Path(__file__).with_name("inventory.db")

app = Flask(__name__)


def get_connection() -> sqlite3.Connection:
    """Open a connection to the inventory database."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/items/<int:item_id>")
def get_item(item_id: int):
    """Return a single inventory item by id."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, name, quantity FROM items WHERE id = ?", (item_id,)
        ).fetchone()
    if row is None:
        abort(404)
    return jsonify(dict(row))


if __name__ == "__main__":
    app.run()

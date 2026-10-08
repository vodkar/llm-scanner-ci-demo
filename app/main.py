"""Tiny inventory service used to demo llm-scanner in CI."""

from pathlib import Path
from typing import Final

from flask import Flask, abort, jsonify, send_from_directory

from app.query_utils import DEFAULT_DIRECTION, DEFAULT_SORT_FIELD, build_order_clause
from app.repository import fetch_item, list_items

EXPORTS_DIR: Final[Path] = Path(__file__).with_name("exports")

app = Flask(__name__)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/items")
def get_items():
    """Return all inventory items."""
    items = list_items(build_order_clause(DEFAULT_SORT_FIELD, DEFAULT_DIRECTION))
    return jsonify(items)


@app.get("/items/<int:item_id>")
def get_item(item_id: int):
    """Return a single inventory item by id."""
    item = fetch_item(item_id)
    if item is None:
        abort(404)
    return jsonify(item)


@app.get("/exports/<path:filename>")
def download_export(filename: str):
    """Download a generated inventory export, e.g. ``/exports/2026-10/items.csv``."""
    return send_from_directory(EXPORTS_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run()

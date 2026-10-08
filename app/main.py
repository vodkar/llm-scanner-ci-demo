"""Tiny inventory service used to demo llm-scanner in CI."""

from flask import Flask, abort, jsonify, request

from app.query_utils import (
    DEFAULT_DIRECTION,
    DEFAULT_SORT_FIELD,
    build_order_clause,
    normalize_sort,
)
from app.repository import fetch_item, list_items

app = Flask(__name__)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/items")
def get_items():
    """Return all inventory items, optionally sorted via ``?sort=<field>&dir=<asc|desc>``."""
    sort_field = normalize_sort(request.args.get("sort", DEFAULT_SORT_FIELD))
    direction = request.args.get("dir", DEFAULT_DIRECTION).upper()
    items = list_items(build_order_clause(sort_field, direction))
    return jsonify(items)


@app.get("/items/<int:item_id>")
def get_item(item_id: int):
    """Return a single inventory item by id."""
    item = fetch_item(item_id)
    if item is None:
        abort(404)
    return jsonify(item)


if __name__ == "__main__":
    app.run()

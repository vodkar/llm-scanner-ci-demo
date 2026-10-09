"""Tiny inventory service used to demo llm-scanner in CI."""

from flask import Flask, abort, jsonify, request

from app.auth import admin_required, current_user, login_required
from app.db import init_db
from app.query_utils import DEFAULT_DIRECTION, build_order_clause, normalize_sort
from app.repository import delete_item, fetch_item, list_items
from app.users import update_preferred_sort

app = Flask(__name__)
init_db()


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/items")
@login_required
def get_items():
    """Return all inventory items in the caller's preferred order."""
    items = list_items(build_order_clause(current_user().preferred_sort, DEFAULT_DIRECTION))
    return jsonify([item.to_dict() for item in items])


@app.get("/items/<int:item_id>")
@login_required
def get_item(item_id: int):
    """Return a single inventory item by id."""
    item = fetch_item(item_id)
    if item is None:
        abort(404)
    return jsonify(item.to_dict())


@app.delete("/items/<int:item_id>")
@admin_required
def remove_item(item_id: int):
    """Delete an inventory item (administrators only)."""
    if not delete_item(item_id):
        abort(404)
    return "", 204


@app.put("/users/me/preferences")
@login_required
def update_preferences():
    """Save the caller's listing order: ``{"sort": "<item column>"}``."""
    payload = request.get_json(silent=True) or {}
    sort_field = payload.get("sort")
    if not isinstance(sort_field, str) or not sort_field.strip():
        abort(400, description="sort must be a non-empty string")
    update_preferred_sort(current_user().id, normalize_sort(sort_field))
    return "", 204


if __name__ == "__main__":
    app.run()

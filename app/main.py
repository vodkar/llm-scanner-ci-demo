"""Tiny inventory service used to demo llm-scanner in CI."""

from dataclasses import asdict

from flask import Flask, abort, jsonify

from app.audit import request_context
from app.auth import admin_required, current_user, login_required
from app.query_utils import DEFAULT_DIRECTION, build_order_clause
from app.repository import delete_item, fetch_item, list_items
from app.users import list_users

app = Flask(__name__)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/items")
@login_required
def get_items():
    """Return all inventory items in the caller's preferred order."""
    items = list_items(build_order_clause(current_user().preferred_sort, DEFAULT_DIRECTION))
    return jsonify(items)


@app.get("/items/<int:item_id>")
@login_required
def get_item(item_id: int):
    """Return a single inventory item by id."""
    item = fetch_item(item_id)
    if item is None:
        abort(404)
    return jsonify(item)


@app.delete("/items/<int:item_id>")
@admin_required
def remove_item(item_id: int):
    """Delete an inventory item (administrators only)."""
    if not delete_item(item_id):
        abort(404)
    return "", 204


@app.get("/users")
@login_required
def get_users():
    """Return the user directory (administrators only)."""
    if not request_context(current_user())["is_admin"]:
        abort(403)
    return jsonify([asdict(user) for user in list_users()])


if __name__ == "__main__":
    app.run()

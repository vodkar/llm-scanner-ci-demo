"""Tiny inventory service used to demo llm-scanner in CI."""

from flask import Flask, abort, jsonify, request

from app.auth import current_user, login_required, permission_required
from app.permissions import Permission, delegate_permission
from app.query_utils import DEFAULT_DIRECTION, build_order_clause
from app.repository import delete_item, fetch_item, list_items

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
@permission_required(Permission.ITEMS_DELETE)
def remove_item(item_id: int):
    """Delete an inventory item (requires ``items:delete``)."""
    if not delete_item(item_id):
        abort(404)
    return "", 204


@app.post("/users/<int:user_id>/permissions")
@permission_required(Permission.PERMISSIONS_MANAGE)
def grant_permission(user_id: int):
    """Delegate one permission to a user: ``{"permission": "items:delete"}``."""
    payload = request.get_json(silent=True) or {}
    try:
        permission = Permission(payload.get("permission"))
    except ValueError:
        abort(400, description="unknown permission")
    delegate_permission(user_id, permission)
    return "", 204


if __name__ == "__main__":
    app.run()

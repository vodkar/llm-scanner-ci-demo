"""Tiny inventory service used to demo llm-scanner in CI."""

from flask import Flask, abort, jsonify, make_response, request

from app.auth import admin_required, current_user, login_required
from app.query_utils import DEFAULT_DIRECTION, build_order_clause
from app.repository import delete_item, fetch_item, list_items
from app.signed_cookies import dumps, loads

app = Flask(__name__)

RECENT_COOKIE = "recent"


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
    recent = [viewed for viewed in _recently_viewed() if viewed != item_id][-4:]
    response = make_response(jsonify(item))
    response.set_cookie(
        RECENT_COOKIE, dumps([*recent, item_id]), httponly=True, samesite="Lax"
    )
    return response


@app.get("/items/recent")
@login_required
def get_recent_items():
    """Return the caller's recently viewed items, most recent first."""
    items = [fetch_item(item_id) for item_id in reversed(_recently_viewed())]
    return jsonify([item for item in items if item is not None])


def _recently_viewed() -> list[int]:
    """Return item ids stored in the signed ``recent`` cookie (empty if absent or altered)."""
    value = loads(request.cookies.get(RECENT_COOKIE, ""))
    if not isinstance(value, list):
        return []
    return [item_id for item_id in value if isinstance(item_id, int)]


@app.delete("/items/<int:item_id>")
@admin_required
def remove_item(item_id: int):
    """Delete an inventory item (administrators only)."""
    if not delete_item(item_id):
        abort(404)
    return "", 204


if __name__ == "__main__":
    app.run()

"""Tiny inventory service used to demo llm-scanner in CI."""

from flask import Flask, abort, jsonify, request

from app.auth import admin_required, login_required
from app.backups import InvalidLabelError, create_backup
from app.query_utils import DEFAULT_DIRECTION, DEFAULT_SORT_FIELD, build_order_clause
from app.repository import delete_item, fetch_item, list_items

app = Flask(__name__)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/items")
@login_required
def get_items():
    """Return all inventory items."""
    items = list_items(build_order_clause(DEFAULT_SORT_FIELD, DEFAULT_DIRECTION))
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


@app.post("/admin/backups")
@admin_required
def backup_database():
    """Snapshot the database: ``{"label": "<a-z, 0-9, ->"}`` (administrators only)."""
    payload = request.get_json(silent=True) or {}
    try:
        target = create_backup(str(payload.get("label", "manual")))
    except InvalidLabelError as error:
        abort(400, description=str(error))
    return jsonify({"backup": target.name}), 201


if __name__ == "__main__":
    app.run()

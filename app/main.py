"""Tiny inventory service used to demo llm-scanner in CI."""

from flask import Flask, abort, jsonify, request

from app.auth import admin_required, current_user, login_required
from app.query_utils import DEFAULT_DIRECTION, build_order_clause
from app.repository import delete_item, fetch_item, list_items
from app.supplier import SupplierFetchError, SupplierURLError, fetch_supplier_listing

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


@app.post("/supplier/preview")
@login_required
def preview_supplier_listing():
    """Preview a supplier catalog entry: ``{"url": "https://<supplier>/items/42.json"}``."""
    payload = request.get_json(silent=True) or {}
    try:
        listing = fetch_supplier_listing(str(payload.get("url", "")))
    except SupplierURLError as error:
        abort(400, description=str(error))
    except (SupplierFetchError, OSError, ValueError):
        abort(502, description="supplier listing unavailable")
    return jsonify({"name": listing.get("name"), "price": listing.get("price")})


if __name__ == "__main__":
    app.run()

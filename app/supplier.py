"""Previews of supplier catalog listings fetched from approved supplier hosts."""

import json
from http.client import HTTPSConnection
from typing import Final
from urllib.parse import urlsplit

SUPPLIER_HOSTS: Final[frozenset[str]] = frozenset(
    {"catalog.acme-supplies.example", "api.northwind-parts.example"}
)
_MAX_RESPONSE_BYTES: Final[int] = 256 * 1024
_TIMEOUT_SECONDS: Final[float] = 5.0


class SupplierURLError(ValueError):
    """Raised when a URL does not point to an approved supplier over HTTPS."""


class SupplierFetchError(RuntimeError):
    """Raised when a supplier responds with an error or an oversized body."""


def supplier_endpoint(url: str) -> tuple[str, str]:
    """Return the approved ``(host, path)`` a supplier URL refers to.

    Raises:
        SupplierURLError: If the URL is not plain HTTPS to an approved supplier host.
    """
    if "\\" in url or not url.isprintable():
        raise SupplierURLError("malformed URL")
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as error:
        raise SupplierURLError("malformed URL") from error
    host = (parts.hostname or "").lower()
    if parts.scheme != "https" or parts.username or parts.password or port not in (None, 443):
        raise SupplierURLError("only https://<supplier host>/... URLs are accepted")
    if host not in SUPPLIER_HOSTS:
        raise SupplierURLError(f"{host or 'empty host'} is not an approved supplier")
    path = parts.path or "/"
    if " " in path or (parts.query and " " in parts.query):
        raise SupplierURLError("malformed URL")
    return host, f"{path}?{parts.query}" if parts.query else path


def fetch_supplier_listing(url: str) -> dict[str, object]:
    """Fetch the JSON listing at an approved supplier URL (no redirects followed)."""
    host, path = supplier_endpoint(url)
    connection = HTTPSConnection(host, timeout=_TIMEOUT_SECONDS)
    try:
        connection.request("GET", path, headers={"Accept": "application/json"})
        response = connection.getresponse()
        if response.status != 200:
            raise SupplierFetchError(f"supplier responded with HTTP {response.status}")
        body = response.read(_MAX_RESPONSE_BYTES + 1)
    finally:
        connection.close()
    if len(body) > _MAX_RESPONSE_BYTES:
        raise SupplierFetchError("supplier response too large")
    listing = json.loads(body)
    if not isinstance(listing, dict):
        raise SupplierFetchError("unexpected supplier response")
    return listing

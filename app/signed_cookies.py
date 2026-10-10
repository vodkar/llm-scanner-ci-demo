"""Tamper-proof cookie values: HMAC-SHA256 signature over a pickled payload."""

import binascii
import hashlib
import hmac
import os
import pickle
from base64 import urlsafe_b64decode, urlsafe_b64encode
from typing import Final

_SIGNATURE_SIZE: Final[int] = hashlib.sha256().digest_size
_MIN_KEY_BYTES: Final[int] = 32


def _signing_key() -> bytes:
    """Return the server-side signing key; refuse to run with a missing or short key."""
    key = os.environ.get("COOKIE_SIGNING_KEY", "").encode()
    if len(key) < _MIN_KEY_BYTES:
        raise RuntimeError(f"COOKIE_SIGNING_KEY must be at least {_MIN_KEY_BYTES} bytes")
    return key


def _sign(payload: bytes) -> bytes:
    return hmac.new(_signing_key(), payload, hashlib.sha256).digest()


def dumps(value: object) -> str:
    """Serialize ``value`` into a signed, URL-safe cookie value."""
    payload = pickle.dumps(value)
    return urlsafe_b64encode(_sign(payload) + payload).decode()


def loads(token: str) -> object | None:
    """Return the value of a cookie produced by ``dumps``, or None if it was altered."""
    try:
        raw = urlsafe_b64decode(token.encode())
    except (binascii.Error, ValueError):
        return None
    signature, payload = raw[:_SIGNATURE_SIZE], raw[_SIGNATURE_SIZE:]
    if not hmac.compare_digest(signature, _sign(payload)):
        return None
    return pickle.loads(payload)

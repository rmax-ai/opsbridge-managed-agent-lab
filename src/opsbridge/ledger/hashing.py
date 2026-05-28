"""Hashing helpers for audit ledger content."""

from __future__ import annotations

import hashlib
import json


def sha256_content_digest(content: bytes | str) -> str:
    """Return a SHA-256 digest for raw content."""
    raw_bytes = content if isinstance(content, bytes) else content.encode("utf-8")
    return hashlib.sha256(raw_bytes).hexdigest()


def sha256_json_digest(payload: object) -> str:
    """Return a SHA-256 digest for a JSON-serializable payload."""
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return sha256_content_digest(canonical_json)

"""SHA-256 hashing for audit trail input/output integrity."""

import hashlib
import json
from typing import Any


def compute_hash(data: Any) -> str:
    if isinstance(data, str):
        raw = data.encode()
    elif isinstance(data, bytes):
        raw = data
    else:
        raw = json.dumps(data, sort_keys=True, default=str).encode()
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"

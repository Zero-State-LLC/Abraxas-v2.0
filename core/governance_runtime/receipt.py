from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .models import GovernanceReceipt


def canonical_json(data: Mapping[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_governance_receipt(runtime: str, status: str, payload: Mapping[str, Any]) -> GovernanceReceipt:
    payload_json = canonical_json(payload)
    digest = sha256_text(payload_json)
    return GovernanceReceipt(
        runtime=runtime,
        status=status,
        payload=dict(payload),
        canonical_payload_json=payload_json,
        sha256=digest,
    )

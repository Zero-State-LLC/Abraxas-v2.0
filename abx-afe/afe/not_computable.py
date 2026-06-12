from __future__ import annotations

from collections.abc import Mapping
from typing import Any


REQUIRED_TRACE_FIELDS = ("agent_id", "environment_id", "episode_id", "provenance")


def not_computable_reasons(payload: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    for field in REQUIRED_TRACE_FIELDS:
        if not payload.get(field):
            reasons.append(f"MISSING_{field.upper()}")
    provenance = payload.get("provenance")
    if isinstance(provenance, Mapping) and not provenance.get("input_hash"):
        reasons.append("MISSING_PROVENANCE_INPUT_HASH")
    return sorted(reasons)


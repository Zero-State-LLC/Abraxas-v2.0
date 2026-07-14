from __future__ import annotations

import json
from typing import Any, Mapping

from core.status_result import (
    STATUS_BLOCKED as BLOCKED,
    STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE,
)

PASS = "PASS"
WARN = "WARN"

STATUS_FIELDS = ("status", "posture", "chain_posture", "runtime_posture", "validation_status")


def canonical_json(data: Mapping[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def normalize_audit_status(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    value = None
    field = None
    for key in STATUS_FIELDS:
        if key in payload and payload[key] is not None:
            value = str(payload[key])
            field = key
            break
    if value not in {PASS, WARN, BLOCKED, NOT_COMPUTABLE}:
        value = NOT_COMPUTABLE
        field = field or "unresolved"
    return {
        "status": value,
        "posture": value,
        "source_field": field,
    }


def build_audit_status_envelope(
    artifact_id: str,
    artifact_type: str,
    status: str,
    findings: list[Mapping[str, Any]] | None = None,
    source_artifacts: list[str] | None = None,
    artifact_hash: str = "",
    generated_at_policy: str = "STATIC",
    schema_version: str = "v1",
) -> Mapping[str, Any]:
    posture = status if status in {PASS, WARN, BLOCKED, NOT_COMPUTABLE} else NOT_COMPUTABLE
    return {
        "schema_version": schema_version,
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "status": posture,
        "posture": posture,
        "findings": findings or [],
        "source_artifacts": source_artifacts or [],
        "artifact_hash": artifact_hash,
        "generated_at_policy": generated_at_policy,
    }

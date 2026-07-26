"""Deprecation / compatibility ledger for entrypoint consolidation."""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash

REMOVAL_TARGET = "abraxas>=3.0 / Production Convergence CLEAR phase"


def build_deprecation_ledger() -> dict[str, Any]:
    entries = [
        {
            "path": "scripts/alembic/run_alembic_spine.py",
            "classification": "EXPERIMENTAL",
            "replacement": "python -m abraxas analyze --alembic-task <task.json>",
            "shim_behavior": "emits DeprecationWarning for product-path commands; keeps logic",
            "removal_target": REMOVAL_TARGET,
            "business_logic_in_shim": False,
        },
        {
            "path": "scripts/runtime/run_validation_service.py",
            "classification": "SUPPORTED_LIBRARY_API_SHIM",
            "replacement": "python -m abraxas validate --schema-ref ... --payload ...",
            "shim_behavior": "emits DeprecationWarning; delegates to validation_service",
            "removal_target": REMOVAL_TARGET,
            "business_logic_in_shim": False,
        },
        {
            "path": "api/hybrid_server.py",
            "classification": "EXPERIMENTAL",
            "replacement": "apps.api.create_app",
            "shim_behavior": "none yet — documented for later CLEAR",
            "removal_target": REMOVAL_TARGET,
            "business_logic_in_shim": False,
        },
        {
            "path": "api/sse_server.py",
            "classification": "EXPERIMENTAL",
            "replacement": "apps.api.create_app",
            "shim_behavior": "none yet — documented for later CLEAR",
            "removal_target": REMOVAL_TARGET,
            "business_logic_in_shim": False,
        },
        {
            "path": "api/websocket_server.py",
            "classification": "EXPERIMENTAL",
            "replacement": "apps.api.create_app",
            "shim_behavior": "none yet — documented for later CLEAR",
            "removal_target": REMOVAL_TARGET,
            "business_logic_in_shim": False,
        },
    ]
    payload = {
        "artifact_type": "deprecation_ledger",
        "schema_version": "deprecation_ledger.v1",
        "evidence_state": "Partial",
        "canonical_cli": "python -m abraxas",
        "canonical_service_factory": "apps.api.create_app",
        "canonical_library_api": "abraxas.AbraxasClient",
        "summary": {
            "entry_count": len(entries),
            "shimmed_now": sum(
                1 for e in entries if "DeprecationWarning" in e["shim_behavior"]
            ),
        },
        "entries": entries,
    }
    payload["canonical_hash"] = canonical_hash(
        {k: v for k, v in payload.items() if k != "canonical_hash"}
    )
    return payload

"""Track C: Alembic residual inventory (advisory; stubs stay stubbed).

Emits a deterministic inventory of architecture adapters with residual flags.
Does not unstub adapters, mutate registry, or grant execution.
"""

from __future__ import annotations

from typing import Any

from core.alembic.registry import default_registry
from core.canonical.json import canonical_hash

SCHEMA_VERSION = "AlembicResidualInventory.v0"
SPINE_STATUS = "ALEMBIC_ADVISORY_COMPLETE_WITH_RESIDUALS"
DETERMINISTIC_TIMESTAMP = "alembic_residual_inventory_v0_ts_0"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "canon_mutation_allowed": False,
    "unstub_authorized": False,
}

PRODUCER = {
    "module": "core.alembic.residual_inventory",
    "track": "C",
    "plan": "docs/plans/ABRAXAS_UNIFICATION_PLAN_002.md",
}

STUB_STATUSES = frozenset({"NOT_IMPLEMENTED", "UNAVAILABLE", "STUB"})


def build_alembic_residual_inventory() -> dict[str, Any]:
    """List default-registry adapters and residual items (deterministic)."""
    registry = default_registry()
    adapters_out: list[dict[str, Any]] = []
    residuals: list[dict[str, Any]] = []
    implemented = 0
    stub_or_unavail = 0

    for desc in registry.list_descriptors():
        status = str(desc.status or "")
        is_stub = bool(desc.is_stub) or status in STUB_STATUSES
        row = {
            "architecture_id": desc.architecture_id,
            "architecture_family": desc.architecture_family,
            "adapter_id": desc.adapter_id,
            "status": status,
            "is_stub": is_stub,
            "authority_class": desc.authority_class,
            "governance_class": desc.governance_class,
        }
        adapters_out.append(row)
        if is_stub:
            stub_or_unavail += 1
            residuals.append(
                {
                    "residual_id": f"stub:{desc.architecture_id}",
                    "kind": "ADAPTER_STUB",
                    "architecture_id": desc.architecture_id,
                    "status": status,
                    "policy": "KEEP_STUBBED_UNTIL_EVALUATION_FIXTURES",
                    "unstub_authorized": False,
                }
            )
        else:
            implemented += 1

    # Document structural residuals from plan (not auto-unstub)
    structural = [
        {
            "residual_id": "live_rune_architecture_deferred",
            "kind": "RUNE_CATALOG",
            "policy": "Keep deferred; reuse bound pipeline runes; operator gate before catalog mutation",
            "unstub_authorized": False,
        },
        {
            "residual_id": "pipeline_inventory_seal_deferred",
            "kind": "INVENTORY_SEAL",
            "policy": "Register alembic_spine only when inventory seal is authorized",
            "unstub_authorized": False,
        },
        {
            "residual_id": "oracle_bridge_metadata_only",
            "kind": "ORACLE_BRIDGE",
            "policy": "Keep metadata-only; no second oracle",
            "unstub_authorized": False,
        },
    ]
    residuals.extend(structural)

    adapters_out.sort(key=lambda r: r["architecture_id"])
    residuals.sort(key=lambda r: r["residual_id"])

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "inventory_id": "ari_"
        + canonical_hash(
            {
                "adapters": [a["architecture_id"] for a in adapters_out],
                "residuals": [r["residual_id"] for r in residuals],
            }
        )[:16],
        "spine_status": SPINE_STATUS,
        "adapters": adapters_out,
        "residuals": residuals,
        "counts": {
            "total": len(adapters_out),
            "implemented": implemented,
            "stub_or_unavailable": stub_or_unavail,
            "residual_items": len(residuals),
        },
        "unstub_policy": (
            "Stubs remain stubbed until evaluation fixtures exist and operator "
            "explicitly authorizes unstub; this inventory never unstubs."
        ),
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "producer": dict(PRODUCER),
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
    }
    body["canonical_hash"] = canonical_hash(body)
    return body

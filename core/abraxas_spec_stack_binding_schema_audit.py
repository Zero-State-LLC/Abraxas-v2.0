from __future__ import annotations

from pathlib import Path
from typing import Any

from core.abraxas_spec_stack_schema_audit_common import (
    NOT_COMPUTABLE,
    authority_locks,
    contract_record,
    contract_summary,
    finalize_audit_packet,
    spec_stack_governance_envelope,
    write_audit_outputs,
)
from core.runtime_integration_gate_shadow_wiring_hooks import _PROJECTION_BINDING_REFS

SCHEMA_VERSION = "AbraxasSpecStackBindingSchemaAudit.v1"
AUDIT_ID = "abraxas_spec_stack_binding_schema_audit_001"
DOMAIN = "binding"
STATUS = "ABRAXAS_SPEC_STACK_BINDING_SCHEMA_AUDIT_EMITTED_ADVISORY_ONLY"
OUT_JSON = Path("out/audit/abraxas_spec_stack_binding_schema_audit_001.latest.json")

EXPECTED_SCHEMA_CONTRACTS: tuple[tuple[str, str], ...] = (
    (
        "rune_route_binding_matrix",
        "contracts/yggdrasil/rune_route_binding_matrix.v1.schema.json",
    ),
    ("coupling_map", "contracts/yggdrasil/coupling_map.v1.schema.json"),
)


def _shadow_binding_records(repo_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for integration_point_id, repo_path in sorted(_PROJECTION_BINDING_REFS.items()):
        target = repo_root / repo_path
        observed = target.exists()
        records.append(
            {
                "contract_id": f"shadow_binding_{integration_point_id.lower()}",
                "integration_point_id": integration_point_id,
                "repo_path": repo_path,
                "contract_kind": "shadow_binding_ref",
                "repo_observed": observed,
                "schema_parse_ok": observed,
                "readiness_status": (
                    "SHADOW_BINDING_OBSERVED_ADVISORY_ONLY"
                    if observed
                    else "SHADOW_BINDING_MISSING_DOCUMENTED_GAP"
                ),
                "authority_granted": False,
            }
        )
    return records


def build_abraxas_spec_stack_binding_schema_audit(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    schema_records = [
        contract_record(
            contract_id=contract_id,
            repo_path=repo_path,
            repo_root=root,
        )
        for contract_id, repo_path in EXPECTED_SCHEMA_CONTRACTS
    ]
    shadow_records = _shadow_binding_records(root)
    records = schema_records + shadow_records
    missing_bindings = [
        record["integration_point_id"]
        for record in shadow_records
        if not record["repo_observed"]
    ]
    findings = [
        {
            "finding_id": "cross_spine_shadow_binding_gap_inventory",
            "finding_kind": "shadow_binding_inventory",
            "finding_status": "OBSERVED",
            "missing_binding_count": len(missing_bindings),
            "missing_integration_point_ids": sorted(missing_bindings),
            "authority_granted": False,
            "repair_authorized": False,
        }
    ]
    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "domain": DOMAIN,
        "status": STATUS,
        **spec_stack_governance_envelope(),
        "contract_records": records,
        "contract_summary": contract_summary(records),
        "findings": findings,
        "recommended_next_lane": NOT_COMPUTABLE,
        "authority_locks": authority_locks(),
    }
    return finalize_audit_packet(base)


def write_abraxas_spec_stack_binding_schema_audit(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(out_root) if out_root is not None else Path(repo_root)
    packet = build_abraxas_spec_stack_binding_schema_audit(repo_root)
    return write_audit_outputs(
        packet,
        out_json=root / OUT_JSON,
        title="Abraxas Spec Stack Binding Schema Audit 001",
    )

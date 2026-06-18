from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.abraxas_spec_stack_schema_audit_common import (
    NOT_COMPUTABLE,
    authority_locks,
    contract_record,
    contract_summary,
    finalize_audit_packet,
    gap_finding,
    spec_stack_governance_envelope,
    write_audit_outputs,
)

SCHEMA_VERSION = "AbraxasSpecStackCodegenSpineSchemaAudit.v1"
AUDIT_ID = "abraxas_spec_stack_codegen_spine_schema_audit_001"
DOMAIN = "codegen_spine"
INTEGRATION_POINT_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_001"
STATUS = "ABRAXAS_SPEC_STACK_CODEGEN_SPINE_SCHEMA_AUDIT_EMITTED_ADVISORY_ONLY"
OUT_JSON = Path("out/audit/abraxas_spec_stack_codegen_spine_schema_audit_001.latest.json")

EXPECTED_CONTRACTS: tuple[tuple[str, str], ...] = (
    ("gap_diagnosis_packet", "contracts/canon/gap_diagnosis_packet.v1.schema.json"),
    ("improvement_proposal", "contracts/canon/improvement_proposal.v1.schema.json"),
    ("shadow_improvement_receipt", "contracts/canon/shadow_improvement_receipt.v1.schema.json"),
    (
        "abx_codegen_intelligence_spine_advisory_spec_plan",
        "contracts/canon/abx_codegen_intelligence_spine_advisory_spec_plan.v1.schema.json",
    ),
    (
        "abx_codegen_intelligence_spine_packet_validation_receipt",
        "contracts/canon/abx_codegen_intelligence_spine_packet_validation_receipt.v1.schema.json",
    ),
    (
        "abx_codegen_intelligence_spine_shadow_binding",
        "contracts/canon/abx_codegen_intelligence_spine_shadow_binding.v1.schema.json",
    ),
)

SHADOW_BINDING_ARTIFACT = "out/audit/abx_codegen_intelligence_spine_shadow_binding_001.latest.json"
SHADOW_BINDING_SCHEMA = "contracts/canon/abx_codegen_intelligence_spine_shadow_binding.v1.schema.json"


def _shadow_binding_validation_ok(repo_root: Path) -> bool:
    artifact_path = repo_root / SHADOW_BINDING_ARTIFACT
    schema_path = repo_root / SHADOW_BINDING_SCHEMA
    if not artifact_path.exists() or not schema_path.exists():
        return False
    try:
        from jsonschema import validate

        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validate(artifact, schema)
        return True
    except Exception:
        return False


def build_abraxas_spec_stack_codegen_spine_schema_audit(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    records = [
        contract_record(
            contract_id=contract_id,
            repo_path=repo_path,
            repo_root=root,
        )
        for contract_id, repo_path in EXPECTED_CONTRACTS
    ]
    shadow_observed = (root / SHADOW_BINDING_ARTIFACT).exists()
    findings = [
        {
            "finding_id": "codegen_shadow_binding_cross_check",
            "finding_kind": "shadow_binding_cross_check",
            "repo_path": SHADOW_BINDING_ARTIFACT,
            "finding_status": "OBSERVED" if shadow_observed else "MISSING",
            "schema_validation_ok": _shadow_binding_validation_ok(root),
            "authority_granted": False,
            "repair_authorized": False,
        },
        gap_finding(
            finding_id="codegen_spine_shadow_binding_reference",
            repo_path=SHADOW_BINDING_ARTIFACT,
            repo_root=root,
        ),
    ]
    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "domain": DOMAIN,
        "integration_point_id": INTEGRATION_POINT_ID,
        "status": STATUS,
        **spec_stack_governance_envelope(),
        "contract_records": records,
        "contract_summary": contract_summary(records),
        "findings": findings,
        "recommended_next_lane": NOT_COMPUTABLE,
        "authority_locks": authority_locks(),
    }
    return finalize_audit_packet(base)


def write_abraxas_spec_stack_codegen_spine_schema_audit(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(out_root) if out_root is not None else Path(repo_root)
    packet = build_abraxas_spec_stack_codegen_spine_schema_audit(repo_root)
    return write_audit_outputs(
        packet,
        out_json=root / OUT_JSON,
        title="Abraxas Spec Stack Codegen Spine Schema Audit 001",
    )

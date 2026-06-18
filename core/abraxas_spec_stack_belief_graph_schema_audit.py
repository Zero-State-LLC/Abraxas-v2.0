from __future__ import annotations

from pathlib import Path
from typing import Any

from core.abraxas_spec_stack_schema_audit_common import (
    NOT_COMPUTABLE,
    artifact_validation_finding,
    authority_locks,
    contract_record,
    contract_summary,
    finalize_audit_packet,
    gap_finding,
    spec_stack_governance_envelope,
    write_audit_outputs,
)

SCHEMA_VERSION = "AbraxasSpecStackBeliefGraphSchemaAudit.v1"
AUDIT_ID = "abraxas_spec_stack_belief_graph_schema_audit_001"
DOMAIN = "belief_graph"
INTEGRATION_POINT_ID = "BELIEF_GRAPH_ENGINE_001"
STATUS = "ABRAXAS_SPEC_STACK_BELIEF_GRAPH_SCHEMA_AUDIT_EMITTED_ADVISORY_ONLY"
OUT_JSON = Path("out/audit/abraxas_spec_stack_belief_graph_schema_audit_001.latest.json")

EXPECTED_CONTRACTS: tuple[tuple[str, str], ...] = (
    ("belief_graph_engine", "contracts/canon/belief_graph_engine.v1.schema.json"),
    (
        "belief_graph_engine_gap_analysis_plan",
        "contracts/canon/belief_graph_engine_gap_analysis_plan.v1.schema.json",
    ),
    (
        "belief_graph_engine_sample_artifact",
        "out/belief_graph/belief_graph_engine_001.latest.json",
    ),
)

SHADOW_BINDING_GAP = "out/audit/belief_graph_engine_shadow_binding_001.latest.json"
ENGINE_SCHEMA = "contracts/canon/belief_graph_engine.v1.schema.json"


def build_abraxas_spec_stack_belief_graph_schema_audit(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    records = [
        contract_record(
            contract_id=contract_id,
            repo_path=repo_path,
            repo_root=root,
            contract_kind="artifact" if repo_path.startswith("out/") else "schema",
            integration_point_id=INTEGRATION_POINT_ID if contract_id.endswith("artifact") else None,
        )
        for contract_id, repo_path in EXPECTED_CONTRACTS
    ]
    findings = [
        gap_finding(
            finding_id="belief_graph_engine_shadow_binding_gap",
            repo_path=SHADOW_BINDING_GAP,
            repo_root=root,
        ),
        artifact_validation_finding(
            artifact_path="out/belief_graph/belief_graph_engine_001.latest.json",
            repo_root=root,
            schema_path=ENGINE_SCHEMA,
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


def write_abraxas_spec_stack_belief_graph_schema_audit(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(out_root) if out_root is not None else Path(repo_root)
    packet = build_abraxas_spec_stack_belief_graph_schema_audit(repo_root)
    return write_audit_outputs(
        packet,
        out_json=root / OUT_JSON,
        title="Abraxas Spec Stack Belief Graph Schema Audit 001",
    )

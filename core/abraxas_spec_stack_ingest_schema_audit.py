from __future__ import annotations

from pathlib import Path
from typing import Any

from core.abraxas_spec_stack_schema_audit_common import (
    NOT_COMPUTABLE,
    contract_record,
    contract_summary,
    finalize_audit_packet,
    gap_finding,
    spec_stack_governance_envelope,
    write_audit_outputs,
)
from core.abraxas_spec_stack_schema_audit_common import authority_locks

SCHEMA_VERSION = "AbraxasSpecStackIngestSchemaAudit.v1"
AUDIT_ID = "abraxas_spec_stack_ingest_schema_audit_001"
DOMAIN = "ingest"
INTEGRATION_POINT_ID = "GLOBAL_INGEST_ADAPTER_SPINE_001"
STATUS = "ABRAXAS_SPEC_STACK_INGEST_SCHEMA_AUDIT_EMITTED_ADVISORY_ONLY"
OUT_JSON = Path("out/audit/abraxas_spec_stack_ingest_schema_audit_001.latest.json")

EXPECTED_CONTRACTS: tuple[tuple[str, str, str], ...] = (
    (
        "scheduled_ingest_run_manifest",
        "contracts/ingest/scheduled_ingest_run_manifest.v1.schema.json",
        "schema",
    ),
    (
        "oracle_signal_intake_receipt",
        "contracts/oracle/oracle_signal_intake_receipt.v1.schema.json",
        "schema",
    ),
    (
        "oracle_signal_pipeline",
        "contracts/global_pipeline/oracle_signal_pipeline.v1.schema.json",
        "schema",
    ),
    (
        "global_ingest_adapter_spine_alignment_plan",
        "out/sync/global_ingest_adapter_spine_alignment_plan/latest.json",
        "artifact",
    ),
    (
        "oracle_intake_queue",
        "out/ingest/oracle_intake_queue_001.latest.json",
        "artifact",
    ),
)

SHADOW_BINDING_GAP = "out/ingest/global_ingest_adapter_spine_shadow_binding_001.latest.json"


def build_abraxas_spec_stack_ingest_schema_audit(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    records = [
        contract_record(
            contract_id=contract_id,
            repo_path=repo_path,
            repo_root=root,
            contract_kind=contract_kind,
            integration_point_id=INTEGRATION_POINT_ID if contract_kind == "artifact" else None,
        )
        for contract_id, repo_path, contract_kind in EXPECTED_CONTRACTS
    ]
    findings = [
        gap_finding(
            finding_id="global_ingest_adapter_spine_shadow_binding_gap",
            repo_path=SHADOW_BINDING_GAP,
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


def write_abraxas_spec_stack_ingest_schema_audit(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(out_root) if out_root is not None else Path(repo_root)
    packet = build_abraxas_spec_stack_ingest_schema_audit(repo_root)
    return write_audit_outputs(
        packet,
        out_json=root / OUT_JSON,
        title="Abraxas Spec Stack Ingest Schema Audit 001",
    )

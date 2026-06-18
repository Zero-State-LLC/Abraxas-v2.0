from __future__ import annotations

from pathlib import Path
from typing import Any

from core.abraxas_spec_stack_belief_graph_schema_audit import (
    build_abraxas_spec_stack_belief_graph_schema_audit,
)
from core.abraxas_spec_stack_binding_schema_audit import (
    build_abraxas_spec_stack_binding_schema_audit,
)
from core.abraxas_spec_stack_codegen_spine_schema_audit import (
    build_abraxas_spec_stack_codegen_spine_schema_audit,
)
from core.abraxas_spec_stack_ingest_schema_audit import (
    build_abraxas_spec_stack_ingest_schema_audit,
)
from core.abraxas_spec_stack_schema_audit_common import (
    NOT_COMPUTABLE,
    authority_locks,
    finalize_audit_packet,
    spec_stack_governance_envelope,
    write_audit_outputs,
)
from core.abraxas_spec_stack_situation_runtime_schema_audit import (
    build_abraxas_spec_stack_situation_runtime_schema_audit,
)

SCHEMA_VERSION = "AbraxasSpecStackSchemaAuditReceipt.v1"
RECEIPT_ID = "ABRAXAS_SPEC_STACK_SCHEMA_AUDIT_RECEIPT_001"
STATUS = "ABRAXAS_SPEC_STACK_SCHEMA_AUDIT_RECEIPT_EMITTED_ADVISORY_ONLY"
OUT_JSON = Path("out/audit/abraxas_spec_stack_schema_audit_receipt_001.latest.json")

DOMAIN_BUILDERS = (
    ("belief_graph", build_abraxas_spec_stack_belief_graph_schema_audit),
    ("codegen_spine", build_abraxas_spec_stack_codegen_spine_schema_audit),
    ("ingest", build_abraxas_spec_stack_ingest_schema_audit),
    ("binding", build_abraxas_spec_stack_binding_schema_audit),
    ("situation_runtime", build_abraxas_spec_stack_situation_runtime_schema_audit),
)


def build_abraxas_spec_stack_schema_audit_receipt(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    domain_audits: list[dict[str, Any]] = []
    total_expected = 0
    total_observed = 0
    total_missing = 0
    for domain, builder in DOMAIN_BUILDERS:
        audit = builder(root)
        summary = audit["contract_summary"]
        total_expected += summary["expected_contract_count"]
        total_observed += summary["repo_observed_count"]
        total_missing += summary["missing_contract_count"]
        domain_audits.append(
            {
                "domain": domain,
                "audit_id": audit["audit_id"],
                "audit_path": f"out/audit/abraxas_spec_stack_{domain}_schema_audit_001.latest.json",
                "audit_hash": audit["audit_hash"],
                "status": audit["status"],
                "expected_contract_count": summary["expected_contract_count"],
                "repo_observed_count": summary["repo_observed_count"],
                "missing_contract_count": summary["missing_contract_count"],
            }
        )
    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": STATUS,
        **spec_stack_governance_envelope(),
        "domain_audits": domain_audits,
        "stack_summary": {
            "domain_count": len(domain_audits),
            "total_expected_contract_count": total_expected,
            "total_repo_observed_count": total_observed,
            "total_missing_contract_count": total_missing,
        },
        "recommended_next_lane": NOT_COMPUTABLE,
        "authority_locks": authority_locks(),
    }
    return finalize_audit_packet(base, hash_field="receipt_hash")


def write_abraxas_spec_stack_schema_audit_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(out_root) if out_root is not None else Path(repo_root)
    packet = build_abraxas_spec_stack_schema_audit_receipt(repo_root)
    return write_audit_outputs(
        packet,
        out_json=root / OUT_JSON,
        title="Abraxas Spec Stack Schema Audit Receipt 001",
    )

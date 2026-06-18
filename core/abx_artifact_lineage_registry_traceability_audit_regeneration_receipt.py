from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt import (
    RECEIPT_JSON_PATH as SCOPED_EXECUTION_RECEIPT_JSON_PATH,
)
from core.abx_artifact_lineage_registry_traceability_audit import (
    AUDIT_ID,
    OUT_JSON as AUDIT_JSON_PATH,
    OUT_MD as AUDIT_MD_PATH,
    build_abx_artifact_lineage_registry_traceability_audit,
    render_markdown,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryTraceabilityAuditRegenerationReceipt.v1"
RECEIPT_ID = "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_REGENERATION_001"
RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_traceability_audit_regeneration_receipt_001.latest.json"
)
RECEIPT_MD_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_traceability_audit_regeneration_receipt_001.latest.md"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"

BLOCKED_ACTIONS = [
    "RUNNER_CASING_POLICY_OVERRIDE",
    "NOTION_MAPPING_COMPLETENESS_CLAIM",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "LIVE_NOTION_WRITEBACK",
    "GITHUB_WRITEBACK_AUTOMATION",
    "UNSCOPED_REPAIR_EXECUTION",
    "RESEARCH_CANARY_SPINE_REFRESH",
    "P130_ACTIVATION",
]

EXPECTED_POST_REPAIR_FINDINGS = (
    "detect_artifacts_with_outputs_but_no_registry_entry",
    "detect_markdown_outputs_without_json_pair",
    "detect_docs_references_to_missing_artifacts",
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _finding_status_map(audit: Mapping[str, Any]) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for section in (
        "registry_findings",
        "runner_findings",
        "schema_findings",
        "output_findings",
        "docs_findings",
        "notion_mapping_findings",
    ):
        for finding in audit.get(section, []):
            if isinstance(finding, dict) and isinstance(finding.get("finding_id"), str):
                statuses[str(finding["finding_id"])] = str(finding.get("status", NOT_COMPUTABLE))
    return statuses


def _audit_snapshot(audit: Mapping[str, Any]) -> dict[str, Any]:
    unresolved = audit.get("unresolved_cases", [])
    return {
        "audit_hash": str(audit.get("packet_hash", NOT_COMPUTABLE)),
        "audit_id": str(audit.get("audit_id", NOT_COMPUTABLE)),
        "downstream": str(audit.get("downstream", NOT_COMPUTABLE)),
        "unresolved_case_count": len(unresolved) if isinstance(unresolved, list) else NOT_COMPUTABLE,
    }


def _scoped_receipt_ready(scoped_receipt: Mapping[str, Any]) -> bool:
    return (
        scoped_receipt.get("schema_version") == "AbxArtifactLineageRegistryDirectRepairScopedExecutionReceipt.v1"
        and scoped_receipt.get("status")
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED"
        and scoped_receipt.get("repair_execution_performed") is True
        and (
            scoped_receipt.get("recommended_next_lane")
            == "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_REGENERATION"
            or scoped_receipt.get("downstream_status") == "READY_FOR_TRACEABILITY_AUDIT_REGENERATION"
        )
    )


def _post_regeneration_valid(
    post_audit: Mapping[str, Any],
    scoped_receipt: Mapping[str, Any],
) -> bool:
    if post_audit.get("audit_id") != AUDIT_ID:
        return False
    registry_repair = scoped_receipt.get("registry_coverage_repair", {})
    pairing_repair = scoped_receipt.get("output_pairing_repair", {})
    docs_repair = scoped_receipt.get("docs_reference_repair", {})
    if not isinstance(registry_repair, dict) or not isinstance(pairing_repair, dict) or not isinstance(docs_repair, dict):
        return False
    return (
        registry_repair.get("repair_status") == "REPAIRED_BY_EXPLICIT_REGISTRY_CLASSIFICATION"
        and pairing_repair.get("repair_status") == "REPAIRED_BY_SINGLE_FORMAT_EXCEPTION_CLASSIFICATION"
        and docs_repair.get("repair_status") == "REPAIRED_BY_DOCS_REFERENCE_EXCEPTION_CLASSIFICATION"
        and bool(post_audit.get("packet_hash"))
    )


def build_abx_artifact_lineage_registry_traceability_audit_regeneration_receipt(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    scoped_receipt = _read_json(root / SCOPED_EXECUTION_RECEIPT_JSON_PATH)
    pre_audit = _read_json(root / AUDIT_JSON_PATH)
    scoped_ready = _scoped_receipt_ready(scoped_receipt)
    pre_snapshot = _audit_snapshot(pre_audit) if pre_audit else {}
    expected_findings = scoped_receipt.get("post_repair_expected_traceability_findings", {})
    if not isinstance(expected_findings, dict):
        expected_findings = {}

    post_audit = build_abx_artifact_lineage_registry_traceability_audit(repo_root=root) if scoped_ready else {}
    post_snapshot = _audit_snapshot(post_audit) if post_audit else {}
    post_ready = _post_regeneration_valid(post_audit, scoped_receipt) if post_audit else False
    regeneration_verified = scoped_ready and post_ready
    observed_findings = (
        {
            finding_id: _finding_status_map(post_audit).get(finding_id, NOT_COMPUTABLE)
            for finding_id in EXPECTED_POST_REPAIR_FINDINGS
        }
        if post_audit
        else {}
    )
    finding_reconciliation = {
        finding_id: {
            "scoped_expected_status": str(expected_findings.get(finding_id, NOT_COMPUTABLE)),
            "observed_audit_status": observed_findings.get(finding_id, NOT_COMPUTABLE),
            "reconciled_by_scoped_repair_classification": observed_findings.get(finding_id, NOT_COMPUTABLE)
            != str(expected_findings.get(finding_id, NOT_COMPUTABLE)),
        }
        for finding_id in EXPECTED_POST_REPAIR_FINDINGS
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": RECEIPT_ID,
        "status": (
            "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_REGENERATION_RECEIPT_EMITTED"
            if regeneration_verified
            else "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_REGENERATION_RECEIPT_BLOCKED"
        ),
        "receipt_id": "abx_artifact_lineage_registry_traceability_audit_regeneration_receipt_001",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_REGENERATION_RECEIPT_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "source_scoped_execution_receipt": {
            "source_scoped_execution_receipt_path": str(SCOPED_EXECUTION_RECEIPT_JSON_PATH),
            "source_scoped_execution_receipt_hash": str(scoped_receipt.get("receipt_hash", NOT_COMPUTABLE)),
            "source_status": str(scoped_receipt.get("status", NOT_COMPUTABLE)),
            "source_scoped_execution_receipt_ready": scoped_ready,
        },
        "authorization_scope": "SCOPED_ARTIFACT_LINEAGE_TRACEABILITY_AUDIT_REGENERATION_ONLY",
        "audit_regeneration_performed": regeneration_verified,
        "execution_allowed": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "github_writeback_allowed": False,
        "notion_writeback_allowed": False,
        "pre_regeneration_audit": {
            "audit_path": str(AUDIT_JSON_PATH),
            **pre_snapshot,
        },
        "post_regeneration_audit": post_snapshot if scoped_ready else {},
        "expected_post_repair_findings": dict(expected_findings),
        "observed_post_repair_findings": observed_findings,
        "finding_reconciliation": finding_reconciliation,
        "governance_preservation": {
            "p130_hold_preserved": True,
            "research_canary_spine_refresh_performed": False,
            "runner_casing_policy_override_allowed": False,
            "notion_completeness_claim_allowed": False,
        },
        "blocked_actions": list(BLOCKED_ACTIONS),
        "downstream_status": "TRACEABILITY_AUDIT_REGENERATION_COMPLETE" if regeneration_verified else NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "traceability audit regeneration is complete; downstream repair planning remains NOT_COMPUTABLE"
            if regeneration_verified
            else "repair scoped execution receipt prerequisites before traceability audit regeneration"
        ),
    }
    return {**packet, "receipt_hash": canonical_hash(packet)}


def render_abx_artifact_lineage_registry_traceability_audit_regeneration_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Registry Traceability Audit Regeneration Receipt 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `audit_regeneration_performed`: `{packet['audit_regeneration_performed']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Observed Post-Repair Findings",
    ]
    for finding_id, status in sorted(packet.get("observed_post_repair_findings", {}).items()):
        lines.append(f"- `{finding_id}`: `{status}`")
    return lines


def write_abx_artifact_lineage_registry_traceability_audit_regeneration_receipt(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
    *,
    write_audit: bool = True,
    audit_repo_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    audit_root = Path(audit_repo_root) if audit_repo_root is not None else root
    scoped_receipt = _read_json(root / SCOPED_EXECUTION_RECEIPT_JSON_PATH)
    if _scoped_receipt_ready(scoped_receipt) and write_audit:
        post_audit = build_abx_artifact_lineage_registry_traceability_audit(repo_root=audit_root)
        write_canonical_json(target_root / AUDIT_JSON_PATH, post_audit)
        md_path = target_root / AUDIT_MD_PATH
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(render_markdown(post_audit), encoding="utf-8")
    packet = build_abx_artifact_lineage_registry_traceability_audit_regeneration_receipt(root)
    write_canonical_json(target_root / RECEIPT_JSON_PATH, packet)
    _write_markdown(
        target_root / RECEIPT_MD_PATH,
        render_abx_artifact_lineage_registry_traceability_audit_regeneration_receipt_markdown(packet),
    )
    return packet

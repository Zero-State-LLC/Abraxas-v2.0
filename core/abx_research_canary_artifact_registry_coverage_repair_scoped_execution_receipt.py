from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_research_canary_artifact_registry_coverage_audit import (
    _canonical_lane_ids,
    build_abx_research_canary_artifact_registry_coverage_audit,
)
from core.canonical.json import canonical_hash, write_canonical_json
from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "AbxResearchCanaryArtifactRegistryCoverageRepairScopedExecutionReceipt.v1"
RECEIPT_ID = "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_SCOPED_EXECUTION_RECEIPT_001"
AUTHORIZATION_RECORD_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_execution_authorization_record_001.latest.json"
)
AUDIT_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json"
)
RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_001.latest.json"
)
RECEIPT_MD_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_001.latest.md"
)
REGENERATION_RECEIPT_JSON_PATH = Path(
    "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_regeneration_receipt_001.latest.json"
)
COVERAGE_AUDIT_REGENERATION_LANE = "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_AUDIT_REGENERATION"

BLOCKED_ACTIONS = [
    "RESEARCH_CANARY_SPINE_REFRESH",
    "RESEARCH_CANARY_ARTIFACT_REGENERATION",
    "P130_ACTIVATION",
    "ORPHAN_OUTPUT_REGISTRY_INCLUSION",
    "SCOPE_PREFIX_MUTATION_WITHOUT_OPERATOR_DECISION",
    "RUNTIME_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "LIVE_NOTION_WRITEBACK",
    "GITHUB_WRITEBACK_AUTOMATION",
    "UNSCOPED_REGISTRY_REPAIR_EXECUTION",
]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _canonical_repair_targets(audit: Mapping[str, Any]) -> dict[str, list[str]]:
    lane_records = [record for record in audit.get("lane_records", []) if isinstance(record, dict)]
    output_paths = sorted(
        str(record["output_json_path"])
        for record in lane_records
        if record.get("output_json_path") not in {None, NOT_COMPUTABLE}
    )
    lane_ids = sorted(
        str(record["lane_id"])
        for record in lane_records
        if record.get("lane_id") not in {None, NOT_COMPUTABLE}
    )
    return {
        "output_path_gaps": output_paths,
        "lane_id_gaps": lane_ids,
    }


def _pre_repair_gap_snapshot(audit: Mapping[str, Any]) -> dict[str, list[str]]:
    lane_records = [record for record in audit.get("lane_records", []) if isinstance(record, dict)]
    output_gaps = sorted(
        str(record["output_json_path"])
        for record in lane_records
        if record.get("registry_coverage_status") == "GAP_CONFIRMED"
        and record.get("output_json_path") not in {None, NOT_COMPUTABLE}
    )
    lane_id_gaps = sorted(
        str(record["lane_id"])
        for record in lane_records
        if not record.get("lane_id_in_registry_source")
        and record.get("lane_id") not in {None, NOT_COMPUTABLE}
    )
    if output_gaps or lane_id_gaps:
        return {
            "output_path_gaps": output_gaps,
            "lane_id_gaps": lane_id_gaps,
        }
    return _canonical_repair_targets(audit)


def _post_repair_verification(root: Path) -> dict[str, Any]:
    current_audit = build_abx_research_canary_artifact_registry_coverage_audit(repo_root=root)
    coverage = current_audit.get("coverage_summary", {})
    derived_optional_paths = set(_DERIVED_OPTIONAL_ARTIFACTS)
    canonical_lane_ids = _canonical_lane_ids()
    registry_source_text = (root / "core/generated_artifact_registry.py").read_text(encoding="utf-8")
    lane_ids_present = all(lane_id in registry_source_text for lane_id in canonical_lane_ids)
    return {
        "direct_registry_lane_id_coverage": coverage.get("direct_registry_lane_id_coverage") is True,
        "lane_id_gap_count": int(coverage.get("lane_id_gap_count", -1)),
        "output_path_gap_count": int(coverage.get("output_path_gap_count", -1)),
        "lane_ids_present_in_registry_source": lane_ids_present,
        "derived_optional_paths_registered": all(
            path in derived_optional_paths
            for path in _pre_repair_gap_snapshot(_read_json(root / AUDIT_JSON_PATH)).get("output_path_gaps", [])
        ),
    }


def build_abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    authorization = _read_json(root / AUTHORIZATION_RECORD_JSON_PATH)
    audit = _read_json(root / AUDIT_JSON_PATH)
    regeneration_receipt = _read_json(root / REGENERATION_RECEIPT_JSON_PATH)
    authorization_status = authorization.get("status")
    authorization_ready = (
        authorization.get("schema_version")
        == "AbxResearchCanaryArtifactRegistryCoverageRepairExecutionAuthorizationRecord.v1"
        and authorization_status
        in {
            "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_RECORD_GRANTED_FOR_SCOPED_EXECUTION_PR",
            "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_RECORD_CONSUMED_BY_SCOPED_EXECUTION_RECEIPT",
        }
        and authorization.get("authorization_granted") is True
        and authorization.get("execution_authority") is True
        and authorization.get("registry_mutation_performed") is False
        and (
            authorization.get("safe_to_prepare_execution_pr") is True
            or authorization_status
            == "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_AUTHORIZATION_RECORD_CONSUMED_BY_SCOPED_EXECUTION_RECEIPT"
        )
    )
    snapshot = _pre_repair_gap_snapshot(audit)
    output_gaps = snapshot["output_path_gaps"]
    lane_id_gaps = snapshot["lane_id_gaps"]
    post_repair = _post_repair_verification(root) if authorization_ready else {}
    repair_verified = (
        authorization_ready
        and post_repair.get("direct_registry_lane_id_coverage") is True
        and post_repair.get("lane_id_gap_count") == 0
        and post_repair.get("output_path_gap_count") == 0
        and post_repair.get("lane_ids_present_in_registry_source") is True
        and post_repair.get("derived_optional_paths_registered") is True
    )
    regeneration_receipt_observed = (
        regeneration_receipt.get("schema_version")
        == "AbxResearchCanaryArtifactRegistryCoverageAuditRegenerationReceipt.v1"
        and regeneration_receipt.get("status")
        == "RESEARCH_CANARY_REGISTRY_COVERAGE_AUDIT_REGENERATION_RECEIPT_EMITTED"
        and regeneration_receipt.get("audit_regeneration_performed") is True
    )
    consumed_by_audit_regeneration = repair_verified and regeneration_receipt_observed

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": RECEIPT_ID,
        "status": (
            "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED"
            if repair_verified
            else "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_SCOPED_EXECUTION_RECEIPT_BLOCKED"
        ),
        "receipt_id": "abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_001",
        "receipt_hash": "",
        "command": "BUILD_ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_SCOPED_EXECUTION_RECEIPT_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "source_authorization_record": {
            "source_authorization_record_path": str(AUTHORIZATION_RECORD_JSON_PATH),
            "source_authorization_record_hash": str(
                authorization.get("authorization_record_hash", NOT_COMPUTABLE)
            ),
            "source_status": str(authorization.get("status", NOT_COMPUTABLE)),
            "source_authorization_ready": authorization_ready,
        },
        "source_audit": {
            "source_audit_path": str(AUDIT_JSON_PATH),
            "source_audit_hash": str(audit.get("audit_hash", NOT_COMPUTABLE)),
            "source_audit_status": str(audit.get("audit_status", NOT_COMPUTABLE)),
        },
        "authorization_scope": "SCOPED_RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_EXECUTION_PR_ONLY",
        "repair_execution_performed": repair_verified,
        "registry_mutation_performed": repair_verified,
        "execution_authority": authorization_ready,
        "execution_allowed": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "github_writeback_allowed": False,
        "notion_writeback_allowed": False,
        "derived_optional_registry_repair": {
            "repair_status": "REPAIRED_BY_DERIVED_OPTIONAL_PER_PATH_CLASSIFICATION" if repair_verified else "BLOCKED",
            "pre_repair_gap_count": len(output_gaps),
            "repaired_count": len(output_gaps) if repair_verified else 0,
            "repaired_paths": output_gaps if repair_verified else [],
            "repair_policy": "DERIVED_OPTIONAL_PER_PATH",
            "orphan_exclusion_preserved": True,
        },
        "lane_id_traceability_repair": {
            "repair_status": "REPAIRED_BY_LANE_ID_TRACEABILITY_METADATA" if repair_verified else "BLOCKED",
            "pre_repair_gap_count": len(lane_id_gaps),
            "repaired_count": len(lane_id_gaps) if repair_verified else 0,
            "repaired_lane_ids": lane_id_gaps if repair_verified else [],
            "repair_policy": "LANE_ID_VISIBILITY_METADATA",
        },
        "governance_preservation": {
            "p130_hold_preserved": True,
            "orphan_exclusion_preserved": True,
            "research_canary_spine_refresh_performed": False,
            "p102g_temporal_continuity_spine_edge_preserved": True,
        },
        "post_repair_verification": post_repair,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "post_repair_expected_audit_findings": {
            "direct_registry_lane_id_coverage": "PASS" if repair_verified else NOT_COMPUTABLE,
            "canonical_lane_output_path_coverage": "PASS" if repair_verified else NOT_COMPUTABLE,
            "orphan_research_output_exclusion": "PASS" if repair_verified else NOT_COMPUTABLE,
            "p130_advisory_hold_preserved": "PASS" if repair_verified else NOT_COMPUTABLE,
        },
        "downstream_status": (
            "COVERAGE_AUDIT_REGENERATION_OBSERVED"
            if consumed_by_audit_regeneration
            else "READY_FOR_COVERAGE_AUDIT_REGENERATION"
            if repair_verified
            else NOT_COMPUTABLE
        ),
        "recommended_next_lane": (
            NOT_COMPUTABLE
            if consumed_by_audit_regeneration
            else COVERAGE_AUDIT_REGENERATION_LANE
            if repair_verified
            else NOT_COMPUTABLE
        ),
        "recommended_next_action": (
            "coverage audit regeneration has been observed; coverage repair chain is complete"
            if consumed_by_audit_regeneration
            else "regenerate the research-canary registry coverage audit from post-repair registry state"
            if repair_verified
            else "complete scoped registry repair prerequisites before emitting receipt"
        ),
    }
    packet["receipt_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "receipt_hash"})
    return packet


def render_abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    derived = packet.get("derived_optional_registry_repair", {})
    lane = packet.get("lane_id_traceability_repair", {})
    return [
        "# ABX Research Canary Artifact Registry Coverage Repair Scoped Execution Receipt 001",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `artifact_id`: `{packet['artifact_id']}`",
        f"- `repair_execution_performed`: `{packet['repair_execution_performed']}`",
        f"- `registry_mutation_performed`: `{packet['registry_mutation_performed']}`",
        f"- `derived_optional_repaired_count`: `{derived.get('repaired_count', NOT_COMPUTABLE)}`",
        f"- `lane_id_traceability_repaired_count`: `{lane.get('repaired_count', NOT_COMPUTABLE)}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Preserved Holds",
        "",
        "- `P130_ACTIVATION` remains blocked",
        "- `ORPHAN_OUTPUT_REGISTRY_INCLUSION` remains blocked",
        "- `RESEARCH_CANARY_SPINE_REFRESH` remains blocked",
        "- `RUNTIME_MUTATION` remains blocked",
        "- `CANON_MUTATION` remains blocked",
        "- `QUEUE_MUTATION` remains blocked",
    ]


def write_abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt(root)
    write_canonical_json(target_root / RECEIPT_JSON_PATH, packet)
    _write_markdown(
        target_root / RECEIPT_MD_PATH,
        render_abx_research_canary_artifact_registry_coverage_repair_scoped_execution_receipt_markdown(packet),
    )
    return packet

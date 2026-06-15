from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "P102GPlusOperatorDecisionSurfaceAudit.v1"
AUDIT_ID = "P102G_PLUS_OPERATOR_DECISION_SURFACE_AUDIT_001"
OUT_JSON = "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.json"
OUT_MD = "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.md"
NOT_COMPUTABLE = "NOT_COMPUTABLE"

SOURCE_SURFACES: tuple[dict[str, str], ...] = (
    {
        "surface_id": "temporal_p95_seal_review",
        "path": "out/temporal_continuity_operator_authorization_record_approval_record_seal_review/latest.json",
        "status_field": "approval_record_seal_review_status",
        "expected_status": "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_REVIEW_HELD_FOR_OPERATOR",
        "scope": "TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_SEAL_REVIEW",
    },
    {
        "surface_id": "codegen_merge_anchor_decision_record_review",
        "path": "out/operator_review/abx_codegen_merge_anchor_source_selection_decision_record_review_001.latest.json",
        "status_field": "status",
        "expected_status": "ABX_CODEGEN_MERGE_ANCHOR_SOURCE_SELECTION_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR",
        "scope": "P102G+CODEGEN-ODR-MERGE-ANCHOR",
    },
    {
        "surface_id": "codegen_phase1_decision_record_review",
        "path": "out/operator_review/abx_codegen_phase1_operator_decision_record_review_001.latest.json",
        "status_field": "status",
        "expected_status": "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR",
        "scope": "P102G+CODEGEN-ODR-PHASE1",
    },
    {
        "surface_id": "codegen_phase1_validation_review_evidence_dry_run_review",
        "path": "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_validation_review_evidence_dry_run_review_001.latest.json",
        "status_field": "status",
        "expected_status": "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_VALIDATION_REVIEW_EVIDENCE_DRY_RUN_REVIEW_HELD_FOR_OPERATOR",
        "scope": "P102G+CODEGEN-ODR-EVIDENCE-VALIDATION",
    },
    {
        "surface_id": "codegen_packet_validation_receipt",
        "path": "out/audit/abx_codegen_intelligence_spine_packet_validation_receipt_001.latest.json",
        "status_field": "receipt_status",
        "expected_status": "ABX_CODEGEN_INTELLIGENCE_SPINE_PACKET_VALIDATION_RECEIPT_READY",
        "scope": "P102G+CODEGEN-PACKET-VALIDATION-ONLY",
    },
    {
        "surface_id": "v2_hygiene_operator_authorization_gate",
        "path": "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json",
        "status_field": "gate_status",
        "expected_status": "V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE_HELD_FOR_OPERATOR",
        "scope": "V2_HYGIENE_ALIGNMENT_OPERATOR_REVIEW_ONLY",
    },
    {
        "surface_id": "v2_hygiene_operator_authorization_evidence_request_plan",
        "path": "out/operator_review/v2_hygiene_operator_authorization_evidence_request_plan_001.latest.json",
        "status_field": "status",
        "expected_status": "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_REQUEST_PLAN_READY",
        "scope": "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_REQUEST_ONLY",
    },
    {
        "surface_id": "v2_hygiene_operator_authorization_evidence_dry_run",
        "path": "out/operator_review/v2_hygiene_operator_authorization_evidence_dry_run_001.latest.json",
        "status_field": "status",
        "expected_status": "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_DRY_RUN_READY",
        "scope": "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_DRY_RUN_ONLY",
    },
    {
        "surface_id": "v2_hygiene_operator_authorization_evidence_validation_plan",
        "path": "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_plan_001.latest.json",
        "status_field": "status",
        "expected_status": "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_PLAN_READY",
        "scope": "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_PLAN_ONLY",
    },
    {
        "surface_id": "v2_hygiene_phase1_foundation_backlog_plan",
        "path": "out/sync/v2_hygiene_phase1_foundation_backlog_plan/latest.json",
        "status_field": "status",
        "expected_status": "V2_HYGIENE_PHASE1_FOUNDATION_BACKLOG_PLAN_READY",
        "scope": "V2_HYGIENE_PHASE1_BACKLOG_ONLY",
    },
    {
        "surface_id": "v2_hygiene_phase2_module_skeleton_backlog_plan",
        "path": "out/sync/v2_hygiene_phase2_module_skeleton_backlog_plan/latest.json",
        "status_field": "status",
        "expected_status": "V2_HYGIENE_PHASE2_MODULE_SKELETON_BACKLOG_PLAN_READY",
        "scope": "V2_HYGIENE_PHASE2_MODULE_BACKLOG_ONLY",
    },
    {
        "surface_id": "v2_hygiene_future_phase_placeholder_audit",
        "path": "out/sync/v2_hygiene_future_phase_placeholder_audit/latest.json",
        "status_field": "status",
        "expected_status": "V2_HYGIENE_FUTURE_PHASE_PLACEHOLDER_AUDIT_READY",
        "scope": "V2_HYGIENE_PHASE3_PHASE4_PLACEHOLDER_ONLY",
    },
    {
        "surface_id": "runtime_integration_gate_operator_review_advisory_spec_plan",
        "path": "out/audit/runtime_integration_gate_operator_review_advisory_spec_plan_001.latest.json",
        "status_field": "plan_status",
        "expected_status": "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_ADVISORY_SPEC_PLAN_READY",
        "scope": "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_ONLY",
    },
    {
        "surface_id": "controlled_ingest_scheduler_operator_review",
        "path": "out/operator_review/controlled_ingest_scheduler_operator_review_record_001.latest.json",
        "status_field": "status",
        "expected_status": "CONTROLLED_INGEST_SCHEDULER_OPERATOR_REVIEW_ACCEPTED",
        "scope": "CONTROLLED_INGEST_REVIEW_ONLY",
    },
    {
        "surface_id": "auto_ingest_shadow_stabilization_review",
        "path": "out/operator_review/abx_auto_ingest_shadow_stabilization_review_record_001.latest.json",
        "status_field": "status",
        "expected_status": "ABX_AUTO_INGEST_SHADOW_STABILIZATION_REVIEW_ACCEPTED",
        "scope": "AUTO_INGEST_SHADOW_STABILIZATION_REVIEW_ONLY",
    },
    {
        "surface_id": "oracle_signal_shadow_intake_decision_record",
        "path": "out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.json",
        "status_field": "status",
        "expected_status": "ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_COMPLETION_APPROVED",
        "scope": "ORACLE_SIGNAL_SHADOW_REVIEW_ONLY",
    },
    {
        "surface_id": "artifact_lineage_direct_repair_execution_authorization_record",
        "path": "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.json",
        "status_field": "status",
        "expected_status": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD_CONSUMED_BY_SCOPED_EXECUTION_RECEIPT",
        "scope": "SCOPED_ARTIFACT_LINEAGE_REPAIR_ONLY",
    },
    {
        "surface_id": "artifact_lineage_direct_repair_scoped_execution_receipt",
        "path": "out/operator_review/abx_artifact_lineage_registry_direct_repair_scoped_execution_receipt_001.latest.json",
        "status_field": "status",
        "expected_status": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SCOPED_EXECUTION_RECEIPT_EMITTED",
        "scope": "SCOPED_ARTIFACT_LINEAGE_REPAIR_RECEIPT_ONLY",
    },
    {
        "surface_id": "pr_644_stack_review_receipt",
        "path": "out/operator_review/pr_644_stack_review_receipt_001.latest.json",
        "status_field": "receipt_status",
        "expected_status": "PR_644_STACK_REVIEW_HELD_FOR_CHECK_COMPLETION",
        "scope": "PR_644_STACK_REVIEW_ONLY",
    },
)

AUTHORITY_FALSE_FIELDS = (
    "approval_granted",
    "authorization_granted",
    "authorization_record_creation_authorized",
    "authorization_record_created",
    "decision_record_created",
    "evidence_bundle_created",
    "operator_evidence_bundle_created",
    "operator_evidence_collection",
    "execution_authority",
    "forecast_authority",
    "implementation_authorized",
    "implementation_unblocked",
    "hygiene_code_creation",
    "hygiene_pipeline_integration",
    "mutation_allowed",
    "module_code_creation",
    "module_registration",
    "notion_writeback_allowed",
    "github_writeback_allowed",
    "runtime_mutation",
    "runtime_mutation_allowed",
    "queue_mutation",
    "scheduler_mutation",
    "canon_mutation",
    "canon_mutation_allowed",
    "schema_mutation",
    "schema_mutation_authorized",
    "projection_surface_mutation_authorized",
    "rune_registration_authorized",
    "schema_file_creation",
    "strict_mode_enablement",
    "v2_module_registration_authorized",
    "valid_for_execution",
    "valid_for_implementation",
    "safe_to_auto_continue",
)

SCOPED_AUTHORITY_FIELDS = frozenset(
    {
        "authorization_granted",
        "execution_authority",
        "implementation_authorized",
    }
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _source_hash(path: Path) -> str:
    data = _read_json(path)
    return canonical_hash(data) if data else NOT_COMPUTABLE


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "canon_mutation": False,
        "code_generation": False,
        "code_mutation": False,
        "decision_record_creation": False,
        "evidence_bundle_creation": False,
        "execution": False,
        "file_writeback": False,
        "forecast_routing": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
        "queue_mutation": False,
        "recommendation_routing": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "shadow_replay_execution": False,
        "token_minting": False,
    }


def _field_value(packet: Mapping[str, Any], field: str) -> Any:
    if field in packet:
        return packet[field]
    locks = packet.get("authority_locks")
    if isinstance(locks, Mapping) and field in locks:
        return locks[field]
    return None


def _surface_authority_findings(
    packet: Mapping[str, Any],
    *,
    scoped_authority_allowed: bool,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for field in AUTHORITY_FALSE_FIELDS:
        value = _field_value(packet, field)
        if value is None:
            continue
        scoped_pass = scoped_authority_allowed and field in SCOPED_AUTHORITY_FIELDS
        findings.append(
            {
                "field": field,
                "observed_value": value,
                "passes_no_broad_authority_lock": value is False or scoped_pass,
            }
        )
    return findings


def _surface_status(record: Mapping[str, str], packet: Mapping[str, Any]) -> str:
    status = packet.get(record["status_field"], NOT_COMPUTABLE)
    return str(status) if isinstance(status, str) else NOT_COMPUTABLE


def _surface_record(repo_root: Path, record: Mapping[str, str]) -> dict[str, Any]:
    path = repo_root / record["path"]
    packet = _read_json(path)
    observed = bool(packet)
    status = _surface_status(record, packet) if observed else NOT_COMPUTABLE
    status_matches_expected = observed and status == record["expected_status"]
    scoped_authority_allowed = record["scope"].startswith("SCOPED_")
    authority_findings = (
        _surface_authority_findings(
            packet,
            scoped_authority_allowed=scoped_authority_allowed,
        )
        if observed
        else []
    )
    authority_fields_checked = len(authority_findings)
    authority_lock_passed = bool(authority_findings) and all(
        finding["passes_no_broad_authority_lock"] is True for finding in authority_findings
    )

    return {
        "surface_id": record["surface_id"],
        "path": record["path"],
        "source_observed": observed,
        "source_hash": _source_hash(path),
        "status_field": record["status_field"],
        "observed_status": status,
        "expected_status": record["expected_status"],
        "status_matches_expected": status_matches_expected,
        "scope": record["scope"],
        "scoped_authority_allowed": scoped_authority_allowed,
        "authority_fields_checked": authority_fields_checked,
        "authority_lock_passed": authority_lock_passed,
        "authority_findings": authority_findings,
        "broad_authority_granted": not authority_lock_passed,
    }


def _audit_findings(surface_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    missing = [item["surface_id"] for item in surface_records if not item["source_observed"]]
    status_mismatches = [
        item["surface_id"] for item in surface_records if not item["status_matches_expected"]
    ]
    authority_failures = [
        item["surface_id"] for item in surface_records if item["broad_authority_granted"]
    ]
    return [
        {
            "finding_id": "p102g_plus_sources_observed",
            "finding_status": "PASS" if not missing else "FAIL_CLOSED",
            "affected_surfaces": missing,
            "authority_granted": False,
        },
        {
            "finding_id": "p102g_plus_expected_statuses_preserved",
            "finding_status": "PASS" if not status_mismatches else "FAIL_CLOSED",
            "affected_surfaces": status_mismatches,
            "authority_granted": False,
        },
        {
            "finding_id": "p102g_plus_broad_authority_denied",
            "finding_status": "PASS" if not authority_failures else "FAIL_CLOSED",
            "affected_surfaces": authority_failures,
            "authority_granted": False,
        },
        {
            "finding_id": "codegen_lane_conventions_observed_from_notion",
            "finding_status": "OBSERVED",
            "affected_surfaces": [
                "P102G+CODEGEN-SHADOW-###",
                "P102G+CODEGEN-ODR-###",
                "P102G+CODEGEN-AUTH-###",
                "META-P102G+CODEGEN-META-###",
            ],
            "authority_granted": False,
        },
    ]


def build_p102g_plus_operator_decision_surface_audit(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    surface_records = [_surface_record(root, source) for source in SOURCE_SURFACES]
    findings = _audit_findings(surface_records)
    all_sources_ready = all(item["finding_status"] != "FAIL_CLOSED" for item in findings[:3])
    audit_status = (
        "P102G_PLUS_OPERATOR_DECISION_SURFACE_AUDIT_READY"
        if all_sources_ready
        else "P102G_PLUS_OPERATOR_DECISION_SURFACE_AUDIT_DEGRADED"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "audit_id": AUDIT_ID,
        "audit_status": audit_status,
        "notion_context": {
            "source_pages_observed": [
                "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_SPEC_PLAN_001",
                "Abraxas v2.0 Live Status Dashboard & Alignment Hub",
                "Continuity Spine Lane Conventions - Codegen Intelligence",
                "Artifact Registry Integration - Codegen Intelligence Spine",
            ],
            "source_observed_date": "2026-06-12",
            "lane_prefixes": [
                "P102G+CODEGEN-SHADOW-###",
                "P102G+CODEGEN-ODR-###",
                "P102G+CODEGEN-AUTH-###",
                "P102G+CODEGEN-SEAL-###",
                "META-P102G+CODEGEN-META-###",
            ],
            "registry_posture": "advisory-only registration does not grant execution authority",
        },
        "surface_records": surface_records,
        "audit_findings": findings,
        "surface_count": len(surface_records),
        "observed_surface_count": sum(1 for item in surface_records if item["source_observed"]),
        "status_match_count": sum(1 for item in surface_records if item["status_matches_expected"]),
        "authority_lock_pass_count": sum(
            1 for item in surface_records if item["authority_lock_passed"]
        ),
        "held_surfaces": [
            item["surface_id"]
            for item in surface_records
            if "HELD" in item["observed_status"] or "HOLD" in item["observed_status"]
        ],
        "review_accepted_surfaces": [
            item["surface_id"]
            for item in surface_records
            if "ACCEPTED" in item["observed_status"]
            or "APPROVED" in item["observed_status"]
            or "EMITTED" in item["observed_status"]
        ],
        "recommended_next_action": (
            "maintain operator-review holds; use explicit external operator decisions before "
            "any runtime-gate wiring, Codegen ODR, authorization, shadow replay, implementation, "
            "writeback, or execution lane"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "operator_decision_record_created": False,
        "operator_authorization_record_created": False,
        "operator_attestation_observed": False,
        "shadow_replay_authorized": False,
        "codegen_implementation_authorized": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_patch": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "forecast_routing": False,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    return {**base, "audit_hash": canonical_hash(base)}


def write_p102g_plus_operator_decision_surface_audit(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_p102g_plus_operator_decision_surface_audit_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# P102G+ Operator Decision Surface Audit",
        "",
        f"- audit_id: {packet['audit_id']}",
        f"- audit_status: {packet['audit_status']}",
        f"- surface_count: {packet['surface_count']}",
        f"- observed_surface_count: {packet['observed_surface_count']}",
        f"- status_match_count: {packet['status_match_count']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        "",
        "## Findings",
    ]
    for finding in packet.get("audit_findings", []):
        if isinstance(finding, Mapping):
            lines.append(f"- {finding['finding_id']}: {finding['finding_status']}")
    lines.extend(["", "## Surfaces"])
    for surface in packet.get("surface_records", []):
        if isinstance(surface, Mapping):
            lines.append(
                "- "
                f"{surface['surface_id']}: {surface['observed_status']} "
                f"(authority_lock_passed={surface['authority_lock_passed']})"
            )
    return lines


def write_p102g_plus_operator_decision_surface_audit_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_p102g_plus_operator_decision_surface_audit_markdown(packet)) + "\n",
        encoding="utf-8",
    )

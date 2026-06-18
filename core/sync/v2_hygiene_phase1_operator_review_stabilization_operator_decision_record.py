from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_operator_review_stabilization_decision_record_dry_run_review import (
    REVIEW_JSON_PATH as SOURCE_REVIEW_JSON_PATH,
)

SCHEMA_VERSION = "V2HygienePhase1OperatorReviewStabilizationOperatorDecisionRecord.v1"
RECORD_ID = "v2_hygiene_phase1_operator_review_stabilization_operator_decision_record_001"
RECORD_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_operator_review_stabilization_operator_decision_record_001.latest.json"
)
RECORD_MD_PATH = RECORD_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = (
    "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_DRY_RUN_REVIEW_"
    "HELD_FOR_OPERATOR"
)
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "authorization_record_creation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "canon_mutation": False,
        "decision_record_creation": False,
        "evidence_bundle_creation": False,
        "execution_authority": False,
        "github_writeback": False,
        "hygiene_code_creation": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_evidence_bundle_creation": False,
        "projection_surface_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_file_creation": False,
        "schema_mutation": False,
        "strict_mode_enablement": False,
        "v2_module_registration": False,
    }


def build_v2_hygiene_phase1_operator_review_stabilization_operator_decision_record(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    review = _read_json(root / SOURCE_REVIEW_JSON_PATH) or {}
    source_ready = (
        review.get("schema_version")
        == "V2HygienePhase1OperatorReviewStabilizationDecisionRecordDryRunReview.v1"
        and review.get("status") == EXPECTED_SOURCE_STATUS
        and review.get("source_stabilization_decision_record_dry_run_ready") is True
        and review.get("operator_attestations_present") is False
        and review.get("decision_record_created") is False
        and review.get("implementation_authorized") is False
        and review.get("hygiene_code_creation_authorized") is False
        and review.get("schema_mutation_authorized") is False
        and review.get("v2_module_registration_authorized") is False
    )
    attested = source_ready
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "decision_record_id": RECORD_ID,
        "status": (
            "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_OPERATOR_DECISION_RECORD_ATTESTED"
            if attested
            else "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_OPERATOR_DECISION_RECORD_BLOCKED"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "selected_operator_decision": "HOLD_FOR_OPERATOR_STABILIZATION_DECISION"
        if attested
        else NOT_COMPUTABLE,
        "selected_strategy_id": "terminal_snapshot_strategy" if attested else NOT_COMPUTABLE,
        "operator_identity": {
            "operator_id": "thread_operator" if attested else NOT_COMPUTABLE,
            "operator_name": "appliedalchemylabs" if attested else NOT_COMPUTABLE,
            "operator_role": "governed_operator" if attested else NOT_COMPUTABLE,
            "operator_attestation_hash": "OPERATOR_ATTESTED_STABILIZATION_BOUNDARY"
            if attested
            else NOT_COMPUTABLE,
        },
        "strategy_scope_acknowledgement": {
            "source_strategy_plan_path": (
                "out/operator_review/"
                "v2_hygiene_phase1_operator_review_stabilization_strategy_plan_001.latest.json"
                if attested
                else NOT_COMPUTABLE
            ),
            "selected_strategy_id": "terminal_snapshot_strategy" if attested else NOT_COMPUTABLE,
            "cycle_audit_scope_acknowledged": attested,
        },
        "stabilization_disposition": {
            "approved_strategy_id": "terminal_snapshot_strategy" if attested else NOT_COMPUTABLE,
            "terminal_snapshot_allowed": attested,
            "bulk_scan_exclusion_allowed": False,
            "two_phase_manifest_allowed": False,
            "naive_regeneration_allowed": False,
        },
        "authority_boundary_acknowledgement": {
            "no_hygiene_implementation_authority": True,
            "no_decision_record_auto_creation": True,
            "no_runtime_mutation": True,
            "no_notion_writeback": True,
            "no_execution_authority": True,
        },
        "terminal_output_controls": {
            "downstream_lane_disposition": NOT_COMPUTABLE,
            "future_dry_run_allowed": False,
            "future_record_creation_gate_required": True,
            "rollback_or_supersession_policy": "HOLD_UNTIL_SEPARATE_GOVERNED_GATE",
        },
        "operator_attestations_present": attested,
        "operator_input_required": False,
        "decision_record_created": True if attested else False,
        "decision_record_creation_authorized": False,
        "implementation_authorized": False,
        "hygiene_code_creation_authorized": False,
        "schema_file_creation_authorized": False,
        "schema_mutation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "strict_mode_enablement_authorized": False,
        "execution_authority": False,
        "valid_for_decision_record": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "authority_locks": _authority_locks(),
        "source_review_path": SOURCE_REVIEW_JSON_PATH.as_posix(),
        "source_review_hash": str(review.get("review_hash", NOT_COMPUTABLE)),
        "recommended_next_lane": (
            "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_HOLD_RECEIPT_001"
            if attested
            else NOT_COMPUTABLE
        ),
        "downstream": NOT_COMPUTABLE,
        "decision_record_hash": "",
    }
    packet["decision_record_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "decision_record_hash"}
    )
    return packet


def render_markdown(packet: Mapping[str, Any]) -> list[str]:
    return [
        "# v2.0 Hygiene Phase 1 Operator Review Stabilization Operator Decision Record",
        "",
        f"- decision_record_id: {packet['decision_record_id']}",
        f"- status: {packet['status']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- hygiene_code_creation_authorized: {packet['hygiene_code_creation_authorized']}",
        f"- downstream: {packet['downstream']}",
    ]


def write_v2_hygiene_phase1_operator_review_stabilization_operator_decision_record(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(out_root) if out_root is not None else Path(repo_root)
    packet = build_v2_hygiene_phase1_operator_review_stabilization_operator_decision_record(
        repo_root
    )
    write_canonical_json(root / RECORD_JSON_PATH, packet)
    md_path = root / RECORD_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(render_markdown(packet)) + "\n", encoding="utf-8")
    return packet

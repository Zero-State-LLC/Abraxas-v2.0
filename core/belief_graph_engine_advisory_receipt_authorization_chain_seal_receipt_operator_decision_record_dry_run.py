from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_plan import (
    OUT_JSON as SOURCE_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = (
    "BeliefGraphEngineAdvisoryReceiptAuthorizationChainSealReceiptOperatorDecisionRecordDryRun.v1"
)
DRY_RUN_ID = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_DRY_RUN_001"
)
OUT_JSON = (
    "out/audit/"
    "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_dry_run_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_dry_run_001.latest.md"
)

EXPECTED_SOURCE_STATUS = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_PLAN_READY"
)
EXPECTED_SOURCE_NEXT_LANE = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_DRY_RUN"
)
RECOMMENDED_NEXT_LANE = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_REVIEW"
)


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed}


def build_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_dry_run(
    *,
    repo_root: str | Path,
    source_operator_decision_record_plan_path: str | Path = SOURCE_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_operator_decision_record_plan_path).as_posix()
    source = _read_json(root / source_operator_decision_record_plan_path)
    source_observed = bool(source)
    source_ready = (
        source.get("artifact_type")
        == "BeliefGraphEngineAdvisoryReceiptAuthorizationChainSealReceiptOperatorDecisionRecordPlan.v1"
        and source.get("operator_decision_record_plan_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == EXPECTED_SOURCE_NEXT_LANE
        and source.get("recommended_default_decision") == "MAINTAIN_HOLD"
        and source.get("operator_decision_record_plan_only") is True
        and source.get("safe_to_auto_continue") is False
        and source.get("decision_record_created") is False
        and source.get("seal_receipt_creation_allowed") is False
        and source.get("seal_receipt_created") is False
        and source.get("recursive_chain_continuation_allowed") is False
        and source.get("authorization_granted") is False
        and source.get("authorization_token_created") is False
        and source.get("execution_authority") is False
    )

    identity_fields = _list(source.get("required_operator_identity_fields"))
    decision_fields = _list(source.get("required_decision_fields"))
    acknowledgement_fields = _list(source.get("required_acknowledgement_fields"))
    evidence_fields = _list(source.get("required_evidence_fields"))
    review_artifacts = _list(source.get("required_review_artifacts"))
    validation_results = sorted(
        [
            _check("source_ready", source_ready),
            _check("operator_identity_fields_present", bool(identity_fields)),
            _check("decision_fields_present", bool(decision_fields)),
            _check("acknowledgement_fields_present", bool(acknowledgement_fields)),
            _check("evidence_fields_present", bool(evidence_fields)),
            _check("required_review_artifacts_present", bool(review_artifacts)),
            _check("decision_record_creation_denied", source.get("decision_record_created") is False),
            _check("seal_receipt_creation_denied", source.get("seal_receipt_creation_allowed") is False),
            _check("authorization_denied", source.get("authorization_granted") is False),
            _check("execution_denied", source.get("execution_authority") is False),
        ],
        key=lambda row: row["check_id"],
    )
    failed_checks = [str(row["check_id"]) for row in validation_results if row["passed"] is False]

    if not source_observed:
        dry_run_status = "NOT_COMPUTABLE"
        validation_passed = False
        blockers = ["source_operator_decision_record_plan_missing_or_unreadable", f"source_path:{source_path}"]
        recommended_next_lane = "NOT_COMPUTABLE"
    elif not source_ready:
        dry_run_status = "BLOCKED_BY_BELIEF_GRAPH_OPERATOR_DECISION_RECORD_PLAN"
        validation_passed = False
        blockers = [f"validation_check_failed:{check_id}" for check_id in failed_checks]
        recommended_next_lane = "NOT_COMPUTABLE"
    else:
        dry_run_status = (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_DRY_RUN_READY"
        )
        validation_passed = True
        blockers = [
            "operator_identity_not_attested",
            "operator_decision_not_attested",
            "operator_acknowledgements_not_attested",
            "operator_evidence_bundle_not_attested",
        ]
        recommended_next_lane = RECOMMENDED_NEXT_LANE

    simulated_record = {
        "artifact_type": (
            "BeliefGraphEngineAdvisoryReceiptAuthorizationChainSealReceiptOperatorDecisionRecord.v1.simulated"
        ),
        "simulated_only": True,
        "decision_record_id": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_001_SIMULATED"
        ),
        "selected_decision": str(source.get("recommended_default_decision", "NOT_COMPUTABLE")),
        "decision_record_created": False,
        "seal_receipt_creation_allowed": False,
        "seal_receipt_created": False,
        "authorization_granted": False,
        "authorization_token_created": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "required_operator_identity_fields": identity_fields,
        "required_decision_fields": decision_fields,
        "required_acknowledgement_fields": acknowledgement_fields,
        "required_evidence_fields": evidence_fields,
    }

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "dry_run_id": DRY_RUN_ID,
        "operator_decision_record_dry_run_status": dry_run_status,
        "source_operator_decision_record_plan": {
            "path": source_path,
            "hash": _sha256(root / source_operator_decision_record_plan_path),
            "operator_decision_record_plan_status": str(
                source.get("operator_decision_record_plan_status", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "source_observed": source_observed,
            "source_ready": source_ready,
        },
        "validation_results": validation_results,
        "validation_passed": validation_passed,
        "validation_blockers": blockers,
        "simulated_decision_record": simulated_record,
        "simulated_only": True,
        "operator_input_required": True,
        "operator_approved": False,
        "decision_record_created": False,
        "seal_receipt_created": False,
        "seal_receipt_creation_allowed": False,
        "recursive_chain_sealed": False,
        "recursive_chain_continuation_allowed": False,
        "authorization_chain_continuation_allowed": False,
        "authorization_record_creation_allowed": False,
        "authorization_record_created": False,
        "authorization_token_created": False,
        "authorization_granted": False,
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_action": (
            "review the advisory simulated operator decision record shape only; do not create a "
            "decision record, seal receipt, token, recursive lane, or Belief Graph engine implementation"
            if validation_passed
            else "repair source operator decision record plan evidence before review"
        ),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "receipt_code_creation_authorized": False,
        "receipt_implementation_authorized": False,
        "receipt_implementation_performed": False,
        "belief_graph_engine_implementation_authorized": False,
        "belief_graph_engine_implementation_performed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "forecast_routing_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "authority_locks": {
            "authorization_chain_continuation": False,
            "authorization_chain_sealing": False,
            "authorization_grant": False,
            "authorization_record_creation": False,
            "authorization_token_creation": False,
            "belief_graph_engine_implementation": False,
            "belief_promotion": False,
            "canon_mutation": False,
            "decision_record_creation": False,
            "execution_authority": False,
            "forecast_routing": False,
            "github_writeback": False,
            "notion_writeback": False,
            "queue_mutation": False,
            "recursive_chain_continuation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "seal_receipt_creation": False,
            "truth_assignment": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_dry_run(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Belief Graph Engine Advisory Receipt Authorization Chain Seal Receipt Operator Decision Record Dry Run",
        "",
        f"- dry_run_id: {packet['dry_run_id']}",
        f"- operator_decision_record_dry_run_status: {packet['operator_decision_record_dry_run_status']}",
        f"- validation_passed: {packet['validation_passed']}",
        f"- simulated_only: {packet['simulated_only']}",
        f"- operator_input_required: {packet['operator_input_required']}",
        f"- decision_record_created: {packet['decision_record_created']}",
        f"- seal_receipt_creation_allowed: {packet['seal_receipt_creation_allowed']}",
        f"- seal_receipt_created: {packet['seal_receipt_created']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- authorization_granted: {packet['authorization_granted']}",
        f"- execution_authority: {packet['execution_authority']}",
        "",
        "## Validation Blockers",
    ]
    for blocker in packet.get("validation_blockers", []):
        lines.append(f"- {blocker}")
    lines.extend(["", "## Validation Results"])
    for result in packet.get("validation_results", []):
        if isinstance(result, Mapping):
            lines.append(f"- {result['check_id']}: {result['passed']}")
    return lines


def write_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_dry_run_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_dry_run_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )

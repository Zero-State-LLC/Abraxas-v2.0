from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_review import (
    OUT_JSON as SOURCE_REVIEW_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = (
    "BeliefGraphEngineAdvisoryReceiptAuthorizationChainSealReceiptOperatorDecisionRecordPlan.v1"
)
PLAN_ID = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_PLAN_001"
)
OUT_JSON = (
    "out/audit/"
    "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_plan_001.latest.md"
)

EXPECTED_SOURCE_STATUS = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_REVIEW_HELD_FOR_OPERATOR"
)
EXPECTED_SOURCE_NEXT_LANE = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_PLAN"
)
RECOMMENDED_NEXT_LANE = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_DRY_RUN"
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


def build_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_plan(
    *,
    repo_root: str | Path,
    source_seal_receipt_review_path: str | Path = SOURCE_REVIEW_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_seal_receipt_review_path).as_posix()
    source = _read_json(root / source_seal_receipt_review_path)
    source_ready = (
        source.get("artifact_type")
        == "BeliefGraphEngineAdvisoryReceiptAuthorizationChainSealReceiptReview.v1"
        and source.get("seal_receipt_review_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == EXPECTED_SOURCE_NEXT_LANE
        and source.get("selected_operator_decision") == "HOLD"
        and source.get("operator_review_required") is True
        and source.get("operator_approved") is False
        and source.get("seal_receipt_review_only") is True
        and source.get("seal_receipt_creation_allowed") is False
        and source.get("seal_receipt_created") is False
        and source.get("recursive_chain_sealed") is False
        and source.get("recursive_chain_continuation_allowed") is False
        and source.get("authorization_granted") is False
        and source.get("authorization_token_created") is False
        and source.get("execution_authority") is False
    )

    plan_status = (
        "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_PLAN_READY"
        if source_ready
        else "NOT_COMPUTABLE"
    )
    recommended_next_lane = RECOMMENDED_NEXT_LANE if source_ready else "NOT_COMPUTABLE"
    source_dry_run = source.get("source_seal_receipt_dry_run", {})
    source_dry_run_path = (
        str(source_dry_run.get("path", "NOT_COMPUTABLE"))
        if isinstance(source_dry_run, Mapping)
        else "NOT_COMPUTABLE"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "operator_decision_record_plan_status": plan_status,
        "source_seal_receipt_review": {
            "path": source_path,
            "hash": _sha256(root / source_seal_receipt_review_path),
            "seal_receipt_review_status": str(
                source.get("seal_receipt_review_status", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "selected_operator_decision": str(
                source.get("selected_operator_decision", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "operator_decision_record_plan_only": True,
        "operator_review_required": True,
        "operator_approved": False,
        "recommended_default_decision": "MAINTAIN_HOLD",
        "allowed_operator_decisions": [
            "MAINTAIN_HOLD",
            "REQUEST_ADDITIONAL_EVIDENCE",
            "REJECT_SEAL_RECEIPT_CREATION",
        ],
        "disallowed_operator_decisions": [
            "AUTHORIZE_SEAL_RECEIPT_CREATION",
            "AUTHORIZE_BELIEF_GRAPH_ENGINE_IMPLEMENTATION",
            "AUTHORIZE_RUNTIME_EXECUTION",
            "MINT_AUTHORIZATION_TOKEN",
            "RESUME_RECURSIVE_AUTHORIZATION_CHAIN",
        ],
        "required_operator_identity_fields": [
            "operator_id",
            "operator_name",
            "operator_role",
            "decision_timestamp_utc",
        ],
        "required_decision_fields": [
            "selected_decision",
            "decision_rationale",
            "decision_scope_acknowledged",
            "seal_receipt_review_status_acknowledged",
            "authority_denials_acknowledged",
        ],
        "required_acknowledgement_fields": [
            "advisory_only_acknowledged",
            "projection_only_acknowledged",
            "non_authoritative_acknowledged",
            "seal_receipt_creation_denied_acknowledged",
            "authorization_denied_acknowledged",
            "execution_authority_denied_acknowledged",
            "runtime_mutation_denied_acknowledged",
            "canon_mutation_denied_acknowledged",
            "queue_mutation_denied_acknowledged",
            "recursive_chain_continuation_denied_acknowledged",
        ],
        "required_evidence_fields": [
            "reviewed_seal_receipt_review_id",
            "reviewed_seal_receipt_review_hash",
            "reviewed_seal_receipt_dry_run_hash",
            "reviewed_authority_locks",
        ],
        "future_record_output_candidates": [
            "out/audit/"
            "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_001.latest.json",
            "out/audit/"
            "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_001.latest.md",
        ],
        "required_review_artifacts": [
            source_path,
            source_dry_run_path,
        ],
        "safe_to_auto_continue": False,
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
            "dry-run the advisory operator decision record plan only; do not create a decision "
            "record, seal receipt, token, recursive lane, or Belief Graph engine implementation"
            if source_ready
            else "repair source seal-receipt review evidence before operator decision record planning"
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


def write_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Belief Graph Engine Advisory Receipt Authorization Chain Seal Receipt Operator Decision Record Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- operator_decision_record_plan_status: {packet['operator_decision_record_plan_status']}",
        f"- recommended_default_decision: {packet['recommended_default_decision']}",
        f"- operator_decision_record_plan_only: {packet['operator_decision_record_plan_only']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- decision_record_created: {packet['decision_record_created']}",
        f"- seal_receipt_creation_allowed: {packet['seal_receipt_creation_allowed']}",
        f"- seal_receipt_created: {packet['seal_receipt_created']}",
        f"- recursive_chain_continuation_allowed: {packet['recursive_chain_continuation_allowed']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- authorization_granted: {packet['authorization_granted']}",
        f"- execution_authority: {packet['execution_authority']}",
        "",
        "## Required Decision Fields",
    ]
    for field in packet.get("required_decision_fields", []):
        lines.append(f"- {field}")
    lines.extend(["", "## Disallowed Operator Decisions"])
    for decision in packet.get("disallowed_operator_decisions", []):
        lines.append(f"- {decision}")
    return lines


def write_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )

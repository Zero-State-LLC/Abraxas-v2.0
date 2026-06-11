from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_dry_run import (
    OUT_JSON as SOURCE_DRY_RUN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = (
    "BeliefGraphEngineAdvisoryReceiptAuthorizationChainSealReceiptOperatorDecisionRecordReview.v1"
)
REVIEW_ID = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_REVIEW_001"
)
OUT_JSON = (
    "out/audit/"
    "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review_001.latest.md"
)

EXPECTED_SOURCE_STATUS = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_DRY_RUN_READY"
)
EXPECTED_SOURCE_NEXT_LANE = (
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


def build_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review(
    *,
    repo_root: str | Path,
    source_operator_decision_record_dry_run_path: str | Path = SOURCE_DRY_RUN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_operator_decision_record_dry_run_path).as_posix()
    source = _read_json(root / source_operator_decision_record_dry_run_path)
    validation_blockers = _list(source.get("validation_blockers"))
    source_ready = (
        source.get("artifact_type")
        == "BeliefGraphEngineAdvisoryReceiptAuthorizationChainSealReceiptOperatorDecisionRecordDryRun.v1"
        and source.get("operator_decision_record_dry_run_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == EXPECTED_SOURCE_NEXT_LANE
        and source.get("validation_passed") is True
        and source.get("simulated_only") is True
        and source.get("operator_input_required") is True
        and source.get("decision_record_created") is False
        and source.get("seal_receipt_creation_allowed") is False
        and source.get("seal_receipt_created") is False
        and source.get("authorization_granted") is False
        and source.get("authorization_token_created") is False
        and source.get("execution_authority") is False
        and bool(validation_blockers)
    )

    review_status = (
        "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR"
        if source_ready
        else "NOT_COMPUTABLE"
    )
    review_findings = [
        {
            "finding_id": "review_finding_001_simulated_shape_validated",
            "finding_status": "OBSERVED" if source_ready else "NOT_COMPUTABLE",
            "authority_granted": False,
        },
        {
            "finding_id": "review_finding_002_operator_attestations_missing",
            "finding_status": "HELD_FOR_OPERATOR" if source_ready else "NOT_COMPUTABLE",
            "authority_granted": False,
        },
        {
            "finding_id": "review_finding_003_decision_record_creation_denied",
            "finding_status": "ENFORCED" if source_ready else "NOT_COMPUTABLE",
            "authority_granted": False,
        },
    ]

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "review_id": REVIEW_ID,
        "operator_decision_record_review_status": review_status,
        "source_operator_decision_record_dry_run": {
            "path": source_path,
            "hash": _sha256(root / source_operator_decision_record_dry_run_path),
            "operator_decision_record_dry_run_status": str(
                source.get("operator_decision_record_dry_run_status", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "validation_passed": source.get("validation_passed") is True,
            "validation_blockers": validation_blockers,
            "source_ready": source_ready,
        },
        "selected_operator_decision": "MAINTAIN_HOLD" if source_ready else "NOT_COMPUTABLE",
        "review_only": True,
        "operator_review_required": True,
        "operator_input_required": True,
        "operator_approved": False,
        "operator_attestations_present": False,
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
        "review_findings": review_findings,
        "terminal_hold_reason": (
            "operator attestations are missing; no decision record can be created by this advisory review"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "recommended_next_lane": "NOT_COMPUTABLE",
        "recommended_next_action": (
            "collect explicit external operator attestation evidence before any future decision record lane; "
            "do not auto-create a decision record, seal receipt, token, recursive lane, or Belief Graph engine implementation"
            if source_ready
            else "repair source operator decision record dry-run evidence before review"
        ),
        "safe_to_auto_continue": False,
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


def write_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Belief Graph Engine Advisory Receipt Authorization Chain Seal Receipt Operator Decision Record Review",
        "",
        f"- review_id: {packet['review_id']}",
        f"- operator_decision_record_review_status: {packet['operator_decision_record_review_status']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- operator_attestations_present: {packet['operator_attestations_present']}",
        f"- decision_record_created: {packet['decision_record_created']}",
        f"- seal_receipt_creation_allowed: {packet['seal_receipt_creation_allowed']}",
        f"- seal_receipt_created: {packet['seal_receipt_created']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- authorization_granted: {packet['authorization_granted']}",
        f"- execution_authority: {packet['execution_authority']}",
        "",
        "## Review Findings",
    ]
    for finding in packet.get("review_findings", []):
        if isinstance(finding, Mapping):
            lines.append(f"- {finding['finding_id']}: {finding['finding_status']}")
    lines.extend(["", "## Source Validation Blockers"])
    source = packet.get("source_operator_decision_record_dry_run", {})
    blockers = source.get("validation_blockers", []) if isinstance(source, Mapping) else []
    for blocker in blockers:
        lines.append(f"- {blocker}")
    return lines


def write_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_operator_decision_record_review_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )

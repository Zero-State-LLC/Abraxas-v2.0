from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_dry_run import (
    OUT_JSON as SOURCE_DRY_RUN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "BeliefGraphEngineAdvisoryReceiptAuthorizationChainSealReceiptReview.v1"
REVIEW_ID = "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_REVIEW_001"
OUT_JSON = (
    "out/audit/"
    "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_review_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_review_001.latest.md"
)

EXPECTED_SOURCE_STATUS = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_DRY_RUN_READY"
)
EXPECTED_SOURCE_NEXT_LANE = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_REVIEW"
)
RECOMMENDED_NEXT_LANE = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_OPERATOR_DECISION_RECORD_PLAN"
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


def build_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_review(
    *,
    repo_root: str | Path,
    source_seal_receipt_dry_run_path: str | Path = SOURCE_DRY_RUN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_seal_receipt_dry_run_path).as_posix()
    source = _read_json(root / source_seal_receipt_dry_run_path)
    source_ready = (
        source.get("artifact_type")
        == "BeliefGraphEngineAdvisoryReceiptAuthorizationChainSealReceiptDryRun.v1"
        and source.get("seal_receipt_dry_run_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == EXPECTED_SOURCE_NEXT_LANE
        and source.get("validation_passed") is True
        and source.get("seal_receipt_dry_run_only") is True
        and source.get("seal_receipt_creation_allowed") is False
        and source.get("seal_receipt_created") is False
        and source.get("recursive_chain_sealed") is False
        and source.get("recursive_chain_continuation_allowed") is False
        and source.get("authorization_granted") is False
        and source.get("authorization_token_created") is False
        and source.get("execution_authority") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "review_id": REVIEW_ID,
        "seal_receipt_review_status": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_REVIEW_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_seal_receipt_dry_run": {
            "path": source_path,
            "hash": _sha256(root / source_seal_receipt_dry_run_path),
            "seal_receipt_dry_run_status": str(
                source.get("seal_receipt_dry_run_status", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "validation_passed": source.get("validation_passed") is True,
            "source_ready": source_ready,
        },
        "selected_operator_decision": "HOLD" if source_ready else "NOT_COMPUTABLE",
        "operator_review_required": True,
        "operator_approved": False,
        "seal_receipt_review_only": True,
        "seal_receipt_creation_allowed": False,
        "seal_receipt_created": False,
        "recursive_chain_sealed": False,
        "recursive_chain_continuation_allowed": False,
        "authorization_chain_continuation_allowed": False,
        "authorization_record_creation_record_creation_allowed": False,
        "authorization_record_creation_allowed": False,
        "authorization_record_created": False,
        "authorization_token_created": False,
        "authorization_granted": False,
        "review_findings": [
            {
                "finding_id": "review_finding_001_source_dry_run_ready",
                "finding_status": "OBSERVED" if source_ready else "NOT_COMPUTABLE",
                "authority_granted": False,
            },
            {
                "finding_id": "review_finding_002_seal_creation_still_denied",
                "finding_status": "ENFORCED" if source_ready else "NOT_COMPUTABLE",
                "authority_granted": False,
            },
            {
                "finding_id": "review_finding_003_operator_decision_required",
                "finding_status": "HELD_FOR_OPERATOR",
                "authority_granted": False,
            },
        ],
        "recommended_next_lane": RECOMMENDED_NEXT_LANE if source_ready else "NOT_COMPUTABLE",
        "recommended_next_action": (
            "prepare an advisory operator decision record plan only; do not create a seal receipt, "
            "resume recursive authorization lanes, mint tokens, or implement the Belief Graph engine"
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
            "authorization_record_creation_record_creation": False,
            "authorization_token_creation": False,
            "belief_promotion": False,
            "canon_mutation": False,
            "execution_authority": False,
            "forecast_routing": False,
            "github_writeback": False,
            "notion_writeback": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "truth_assignment": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_review(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_review_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Belief Graph Engine Advisory Receipt Authorization Chain Seal Receipt Review",
        "",
        f"- review_id: {packet['review_id']}",
        f"- seal_receipt_review_status: {packet['seal_receipt_review_status']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- seal_receipt_review_only: {packet['seal_receipt_review_only']}",
        f"- seal_receipt_creation_allowed: {packet['seal_receipt_creation_allowed']}",
        f"- seal_receipt_created: {packet['seal_receipt_created']}",
        f"- recursive_chain_sealed: {packet['recursive_chain_sealed']}",
        f"- recursive_chain_continuation_allowed: {packet['recursive_chain_continuation_allowed']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- authorization_granted: {packet['authorization_granted']}",
        f"- execution_authority: {packet['execution_authority']}",
        "",
        "## Review Findings",
    ]
    for finding in packet.get("review_findings", []):
        if isinstance(finding, dict):
            lines.append(f"- {finding['finding_id']}: {finding['finding_status']}")
    return lines


def write_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_review_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_review_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )

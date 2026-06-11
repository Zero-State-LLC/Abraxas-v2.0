from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_engine_advisory_receipt_authorization_chain_compression_audit import (
    OUT_JSON as SOURCE_COMPRESSION_AUDIT_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "BeliefGraphEngineAdvisoryReceiptAuthorizationChainSealReceiptPlan.v1"
PLAN_ID = "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_plan_001.latest.md"
)

EXPECTED_SOURCE_STATUS = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_READY"
)
EXPECTED_SOURCE_NEXT_LANE = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_PLAN"
)
RECOMMENDED_NEXT_LANE = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_DRY_RUN"
)

DENIED_AUTHORITY = [
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_CODE_CREATION",
    "BELIEF_GRAPH_ENGINE_RECEIPT_IMPLEMENTATION",
    "BELIEF_GRAPH_ENGINE_IMPLEMENTATION",
    "BELIEF_GRAPH_ENGINE_RUNTIME_CREATION",
    "AUTHORIZATION_RECORD_CREATION",
    "AUTHORIZATION_RECORD_CREATION_RECORD_CREATION",
    "AUTHORIZATION_CHAIN_CONTINUATION",
    "AUTHORIZATION_CHAIN_SEALING",
    "AUTHORIZATION_GRANT",
    "AUTHORIZATION_TOKEN_CREATION",
    "TRUTH_ASSIGNMENT",
    "BELIEF_PROMOTION",
    "FORECAST_ROUTING",
    "RUNTIME_DISPATCH_MUTATION",
    "CANON_MUTATION",
    "QUEUE_MUTATION",
    "SCHEDULER_MUTATION",
    "NOTION_WRITEBACK",
    "GITHUB_WRITEBACK",
    "ACTIVATION_OR_EXECUTION",
]


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


def build_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_plan(
    *,
    repo_root: str | Path,
    source_compression_audit_path: str | Path = SOURCE_COMPRESSION_AUDIT_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_compression_audit_path).as_posix()
    source = _read_json(root / source_compression_audit_path)
    source_ready = (
        source.get("artifact_type")
        == "BeliefGraphEngineAdvisoryReceiptAuthorizationChainCompressionAudit.v1"
        and source.get("compression_audit_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == EXPECTED_SOURCE_NEXT_LANE
        and source.get("chain_recommendation") == "SEAL_RECURSIVE_AUTHORIZATION_CHAIN"
        and source.get("compression_recommendation") == "COMPRESS_TO_GENERIC_TEMPLATE"
        and source.get("further_recursive_lane_recommended") is False
        and source.get("authorization_chain_continuation_allowed") is False
        and source.get("authorization_record_creation_record_creation_allowed") is False
        and source.get("authorization_record_created") is False
        and source.get("authorization_token_created") is False
        and source.get("authorization_granted") is False
        and source.get("execution_authority") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "seal_receipt_plan_status": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_PLAN_READY"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_compression_audit": {
            "path": source_path,
            "hash": _sha256(root / source_compression_audit_path),
            "compression_audit_status": str(
                source.get("compression_audit_status", "NOT_COMPUTABLE")
            ),
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "chain_recommendation": str(source.get("chain_recommendation", "NOT_COMPUTABLE")),
            "compression_recommendation": str(
                source.get("compression_recommendation", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "seal_receipt_plan_only": True,
        "seal_receipt_required": source_ready,
        "seal_receipt_created": False,
        "seal_receipt_creation_allowed": False,
        "recursive_chain_sealed": False,
        "recursive_chain_continuation_allowed": False,
        "planned_seal_receipt": {
            "artifact_type": "BeliefGraphEngineAdvisoryReceiptAuthorizationChainSealReceipt.v1",
            "receipt_scope": "ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_TERMINALITY_ONLY",
            "source_compression_audit_path": source_path,
            "source_compression_audit_hash": _sha256(root / source_compression_audit_path),
            "records_terminal_recommendation_only": True,
            "operator_approval_required": True,
            "operator_approved": False,
            "seal_receipt_created": False,
            "recursive_chain_sealed": False,
            "authorization_chain_continuation_allowed": False,
            "authorization_granted": False,
            "authorization_token_created": False,
            "execution_authority": False,
            "packet_hash_required": True,
        },
        "seal_receipt_requirements": [
            {
                "requirement_id": "seal_requirement_001_source_compression_ready",
                "requirement_status": "SATISFIED" if source_ready else "FAIL_CLOSED",
                "required_before": "seal receipt dry run",
                "authority_granted": False,
            },
            {
                "requirement_id": "seal_requirement_002_no_recursive_continuation",
                "requirement_status": "ENFORCED" if source_ready else "NOT_COMPUTABLE",
                "required_before": "any downstream Belief Graph authorization lane",
                "authority_granted": False,
            },
            {
                "requirement_id": "seal_requirement_003_operator_review_required",
                "requirement_status": "HELD_FOR_OPERATOR",
                "required_before": "any real seal receipt creation",
                "authority_granted": False,
            },
            {
                "requirement_id": "seal_requirement_004_hash_bound_receipt",
                "requirement_status": "PLANNED_ONLY",
                "required_before": "future seal receipt review",
                "authority_granted": False,
            },
        ],
        "recommended_next_lane": RECOMMENDED_NEXT_LANE if source_ready else "NOT_COMPUTABLE",
        "recommended_next_action": (
            "prepare an advisory seal-receipt dry run only; do not create a seal receipt, "
            "resume recursive authorization lanes, mint tokens, or implement the Belief Graph engine"
        ),
        "denied_authority": list(DENIED_AUTHORITY),
        "receipt_code_creation_authorized": False,
        "receipt_implementation_authorized": False,
        "receipt_implementation_performed": False,
        "belief_graph_engine_implementation_authorized": False,
        "belief_graph_engine_implementation_performed": False,
        "authorization_chain_continuation_allowed": False,
        "authorization_record_creation_record_creation_allowed": False,
        "authorization_record_creation_record_created": False,
        "authorization_record_creation_allowed": False,
        "authorization_record_created": False,
        "authorization_token_created": False,
        "operator_approved": False,
        "authorization_granted": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
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


def write_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Belief Graph Engine Advisory Receipt Authorization Chain Seal Receipt Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- seal_receipt_plan_status: {packet['seal_receipt_plan_status']}",
        f"- seal_receipt_plan_only: {packet['seal_receipt_plan_only']}",
        f"- seal_receipt_required: {packet['seal_receipt_required']}",
        f"- seal_receipt_creation_allowed: {packet['seal_receipt_creation_allowed']}",
        f"- seal_receipt_created: {packet['seal_receipt_created']}",
        f"- recursive_chain_sealed: {packet['recursive_chain_sealed']}",
        f"- recursive_chain_continuation_allowed: {packet['recursive_chain_continuation_allowed']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- authorization_granted: {packet['authorization_granted']}",
        f"- execution_authority: {packet['execution_authority']}",
        "",
        "## Seal Receipt Requirements",
    ]
    for requirement in packet.get("seal_receipt_requirements", []):
        if isinstance(requirement, dict):
            lines.append(
                f"- {requirement['requirement_id']}: {requirement['requirement_status']}"
            )
    lines.extend(["", "## Denied Authority"])
    for authority in packet.get("denied_authority", []):
        lines.append(f"- {authority}")
    return lines


def write_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_belief_graph_engine_advisory_receipt_authorization_chain_seal_receipt_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )

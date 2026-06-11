from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_engine_advisory_receipt_implementation_authorization_record_creation_record_plan import (
    OUT_JSON as SOURCE_RECORD_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "BeliefGraphEngineAdvisoryReceiptAuthorizationChainCompressionAudit.v1"
AUDIT_ID = "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_001"
OUT_JSON = (
    "out/audit/"
    "belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_001.latest.md"
)

EXPECTED_SOURCE_STATUS = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_RECORD_PLAN_READY"
)
REJECTED_RECURSIVE_NEXT_LANE = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_IMPLEMENTATION_AUTHORIZATION_RECORD_CREATION_RECORD_CREATION_PLAN"
)
RECOMMENDED_SEAL_NEXT_LANE = (
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_SEAL_RECEIPT_PLAN"
)

DENIED_AUTHORITY = [
    "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_CODE_CREATION",
    "BELIEF_GRAPH_ENGINE_RECEIPT_IMPLEMENTATION",
    "BELIEF_GRAPH_ENGINE_IMPLEMENTATION",
    "BELIEF_GRAPH_ENGINE_RUNTIME_CREATION",
    "AUTHORIZATION_RECORD_CREATION",
    "AUTHORIZATION_RECORD_CREATION_RECORD_CREATION",
    "AUTHORIZATION_CHAIN_CONTINUATION",
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


def build_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit(
    *,
    repo_root: str | Path,
    source_record_plan_path: str | Path = SOURCE_RECORD_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_record_plan_path).as_posix()
    source = _read_json(root / source_record_plan_path)
    source_ready = (
        source.get("artifact_type")
        == "BeliefGraphEngineAdvisoryReceiptImplementationAuthorizationRecordCreationRecordPlan.v1"
        and source.get("record_plan_status") == EXPECTED_SOURCE_STATUS
        and source.get("recommended_next_lane") == REJECTED_RECURSIVE_NEXT_LANE
        and source.get("authorization_record_creation_record_plan_only") is True
        and source.get("authorization_record_creation_record_allowed") is False
        and source.get("authorization_record_creation_record_created") is False
        and source.get("authorization_record_creation_allowed") is False
        and source.get("authorization_record_created") is False
        and source.get("authorization_token_created") is False
        and source.get("authorization_granted") is False
        and source.get("execution_authority") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "audit_id": AUDIT_ID,
        "compression_audit_status": (
            "BELIEF_GRAPH_ENGINE_ADVISORY_RECEIPT_AUTHORIZATION_CHAIN_COMPRESSION_AUDIT_READY"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_record_creation_record_plan": {
            "path": source_path,
            "hash": _sha256(root / source_record_plan_path),
            "record_plan_status": str(source.get("record_plan_status", "NOT_COMPUTABLE")),
            "recommended_next_lane": str(source.get("recommended_next_lane", "NOT_COMPUTABLE")),
            "source_ready": source_ready,
        },
        "recursive_pattern_observed": source_ready,
        "rejected_recursive_next_lane": (
            REJECTED_RECURSIVE_NEXT_LANE if source_ready else "NOT_COMPUTABLE"
        ),
        "further_recursive_lane_recommended": False,
        "chain_recommendation": (
            "SEAL_RECURSIVE_AUTHORIZATION_CHAIN" if source_ready else "NOT_COMPUTABLE"
        ),
        "compression_recommendation": (
            "COMPRESS_TO_GENERIC_TEMPLATE" if source_ready else "NOT_COMPUTABLE"
        ),
        "recommended_next_lane": (
            RECOMMENDED_SEAL_NEXT_LANE if source_ready else "NOT_COMPUTABLE"
        ),
        "recommended_next_action": (
            "prepare a separate advisory seal/compression receipt plan; do not add another "
            "hand-written authorization record creation record-creation lane"
        ),
        "terminality_findings": [
            {
                "finding_id": "terminality_001_self_similar_route",
                "finding_status": "OBSERVED" if source_ready else "NOT_COMPUTABLE",
                "summary": "source plan routes to a self-similar record-creation lane",
                "authority_granted": False,
            },
            {
                "finding_id": "terminality_002_authority_locked",
                "finding_status": "OBSERVED" if source_ready else "NOT_COMPUTABLE",
                "summary": "source plan keeps authorization, token, record, execution, and implementation authority false",
                "authority_granted": False,
            },
            {
                "finding_id": "terminality_003_compression_precedent",
                "finding_status": "APPLIED" if source_ready else "NOT_COMPUTABLE",
                "summary": "recursive authorization chains should be compressed or sealed instead of extended by hand",
                "authority_granted": False,
            },
        ],
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


def write_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Belief Graph Engine Advisory Receipt Authorization Chain Compression Audit",
        "",
        f"- audit_id: {packet['audit_id']}",
        f"- compression_audit_status: {packet['compression_audit_status']}",
        f"- recursive_pattern_observed: {packet['recursive_pattern_observed']}",
        f"- rejected_recursive_next_lane: {packet['rejected_recursive_next_lane']}",
        f"- further_recursive_lane_recommended: {packet['further_recursive_lane_recommended']}",
        f"- chain_recommendation: {packet['chain_recommendation']}",
        f"- compression_recommendation: {packet['compression_recommendation']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- authorization_chain_continuation_allowed: {packet['authorization_chain_continuation_allowed']}",
        f"- authorization_record_creation_record_creation_allowed: {packet['authorization_record_creation_record_creation_allowed']}",
        f"- authorization_granted: {packet['authorization_granted']}",
        f"- execution_authority: {packet['execution_authority']}",
        "",
        "## Terminality Findings",
    ]
    for finding in packet.get("terminality_findings", []):
        if isinstance(finding, dict):
            lines.append(f"- {finding['finding_id']}: {finding['finding_status']}")
    lines.extend(["", "## Denied Authority"])
    for authority in packet.get("denied_authority", []):
        lines.append(f"- {authority}")
    return lines


def write_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_belief_graph_engine_advisory_receipt_authorization_chain_compression_audit_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )

"""Familiar operator-review packet — disposition seed from oracle/belief bridge.

Closes abx-familiar residual after BRIDGE_V0. Does not write operator queues,
attest dispositions, or grant execution.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash
from core.signal.familiar_oracle_belief_bridge import (
    build_bridge_from_pack_path,
    build_familiar_oracle_belief_bridge,
)

SCHEMA_VERSION = "FamiliarOperatorReviewPacket.v0"
PIPELINE_ID = "familiar_ingestion"
DETERMINISTIC_TIMESTAMP = "familiar_operator_review_packet_v0_ts_0"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "queue_write_authorized": False,
}

PRODUCER = {
    "module": "core.signal.familiar_operator_review",
    "skill_id": "abx-familiar-signal-forager",
    "pipeline_id": PIPELINE_ID,
    "upstream": "core.signal.familiar_oracle_belief_bridge",
}


def build_familiar_operator_review_packet(
    bridge: dict[str, Any] | None,
) -> dict[str, Any]:
    """Map FamiliarOracleBeliefBridge → operator-review disposition seed."""
    if bridge is None:
        body = {
            "schema_version": SCHEMA_VERSION,
            "pipeline_id": PIPELINE_ID,
            "review_id": "for_no_bridge",
            "bridge_id": "",
            "pack_id": "",
            "touchpoint_id": "",
            "route": "ABSTAIN_NO_INPUT",
            "bridge_status": "BRIDGE_NO_INPUT",
            "disposition": "NOT_COMPUTABLE",
            "recommended_action": "ABSTAIN_NO_ACTION",
            "review_queue_hint": "operator_review_queue",
            "summary": "No bridge packet; nothing to review.",
            "belief_seed_count": 0,
            "oracle_intake_present": False,
            "blocked_by": ["NO_BRIDGE", "QUEUE_WRITE_BLOCKED"],
            "authority": dict(DEFAULT_AUTHORITY),
            "advisory_only": True,
            "lane": "SHADOW",
            "producer": dict(PRODUCER),
            "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
        }
        body["canonical_hash"] = canonical_hash(body)
        return body

    status = str(bridge.get("status") or "")
    route = str(bridge.get("route") or "")
    pack_id = str(bridge.get("pack_id") or "")
    bridge_id = str(bridge.get("bridge_id") or "")
    touchpoint_id = str(bridge.get("touchpoint_id") or "")
    seeds = bridge.get("belief_candidate_seeds") or []
    seed_count = len(seeds) if isinstance(seeds, list) else 0
    intake = bridge.get("oracle_shadow_intake") or {}
    intake_present = isinstance(intake, dict) and bool(intake)
    blocks = (
        list(bridge.get("blocked_by") or [])
        if isinstance(bridge.get("blocked_by"), list)
        else []
    )
    if "QUEUE_WRITE_BLOCKED" not in blocks:
        blocks.append("QUEUE_WRITE_BLOCKED")

    if status == "BRIDGED_SHADOW" and route == "ORACLE_SHADOW_CANDIDATE":
        disposition = "READY_FOR_REVIEW"
        recommended = (
            "REVIEW_ORACLE_SHADOW_INTAKE" if intake_present else "REVIEW_BELIEF_SEEDS"
        )
        summary = (
            f"Bridge ready: pack={pack_id or 'unknown'} route={route} "
            f"belief_seeds={seed_count} oracle_intake={intake_present}."
        )
    elif status == "BRIDGE_NO_INPUT":
        disposition = "NOT_COMPUTABLE"
        recommended = "ABSTAIN_NO_ACTION"
        summary = f"Bridge abstained: status={status} route={route}."
    elif status == "BRIDGE_ABSTAINED" or route.startswith("ABSTAIN"):
        disposition = "ABSTAIN"
        recommended = "ABSTAIN_NO_ACTION"
        summary = f"Bridge abstained: status={status} route={route}."
    else:
        disposition = "PENDING_OPERATOR"
        recommended = "HOLD_INCOMPLETE"
        summary = f"Bridge pending: status={status}."

    review_id = "for_" + canonical_hash(
        {
            "bridge_id": bridge_id,
            "pack_id": pack_id,
            "disposition": disposition,
            "seed_count": seed_count,
        }
    )[:16]

    body = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_id": PIPELINE_ID,
        "review_id": review_id,
        "bridge_id": bridge_id,
        "pack_id": pack_id,
        "touchpoint_id": touchpoint_id,
        "route": route,
        "bridge_status": status,
        "disposition": disposition,
        "recommended_action": recommended,
        "review_queue_hint": "operator_review_queue",
        "summary": summary,
        "belief_seed_count": seed_count,
        "oracle_intake_present": intake_present,
        "blocked_by": blocks,
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "lane": "SHADOW",
        "producer": dict(PRODUCER),
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_operator_review_from_pack_path(
    path: str | Path,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Pack path → bridge → operator review (pure)."""
    bridge = build_bridge_from_pack_path(path, repo_root=repo_root)
    return build_familiar_operator_review_packet(bridge)


def build_operator_review_from_touchpoint(
    touchpoint: dict[str, Any] | None,
) -> dict[str, Any]:
    bridge = build_familiar_oracle_belief_bridge(touchpoint)
    return build_familiar_operator_review_packet(bridge)

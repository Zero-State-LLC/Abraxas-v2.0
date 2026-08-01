"""Familiar operator-review packet — disposition seed from oracle/belief bridge.

Closes abx-familiar residual after BRIDGE_V0. Does not write operator queues,
attest dispositions, or grant execution.

Dry-run maps FamiliarOperatorReviewPacket.v0 → OperatorReviewQueueItem.v1 /
OperatorReviewQueueRun.v1 shape without writing out/operator_review_queue.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.global_operator_review_queue import build_queue_item, build_queue_run
from core.signal.familiar_oracle_belief_bridge import (
    build_bridge_from_pack_path,
    build_familiar_oracle_belief_bridge,
)

SCHEMA_VERSION = "FamiliarOperatorReviewPacket.v0"
DRY_RUN_SCHEMA_VERSION = "FamiliarOperatorReviewQueueDryRun.v0"
PIPELINE_ID = "familiar_ingestion"
DETERMINISTIC_TIMESTAMP = "familiar_operator_review_packet_v0_ts_0"
QUEUE_TARGET_PATH = "out/operator_review_queue"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "queue_write_authorized": False,
}

QUEUE_AUTHORITY = {
    "promotion_allowed": False,
    "forecast_weight_allowed": False,
    "runtime_mutation_allowed": False,
    "baseline_mutation_allowed": False,
    "canon_mutation_allowed": False,
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


def _action_for_recommended(recommended: str) -> list[str]:
    if recommended == "REVIEW_ORACLE_SHADOW_INTAKE":
        return [
            "review_familiar_oracle_shadow_intake",
            "acknowledge_queue_write_blocked",
        ]
    if recommended == "REVIEW_BELIEF_SEEDS":
        return [
            "review_familiar_belief_seeds",
            "acknowledge_queue_write_blocked",
        ]
    if recommended == "HOLD_INCOMPLETE":
        return [
            "complete_familiar_bridge",
            "collect_operator_decision_evidence",
        ]
    return []


def normalize_familiar_operator_review(
    review: Mapping[str, Any],
) -> dict[str, Any]:
    """Map FamiliarOperatorReviewPacket.v0 → global queue normalized packet.

    Pure. Does not classify or write; feed result to build_queue_item.
    """
    disposition = str(review.get("disposition") or "NOT_COMPUTABLE")
    recommended = str(review.get("recommended_action") or "ABSTAIN_NO_ACTION")
    pack_id = str(review.get("pack_id") or "")
    review_id = str(review.get("review_id") or "")
    source_hash = str(review.get("canonical_hash") or review_id or "missing")
    blocked = (
        list(review.get("blocked_by") or [])
        if isinstance(review.get("blocked_by"), list)
        else []
    )
    summary = str(review.get("summary") or "Familiar operator review seed")
    title = (
        f"Familiar operator review: {pack_id}"
        if pack_id
        else "Familiar operator review (no pack)"
    )

    base: dict[str, Any] = {
        "title": title,
        "pipeline_id": str(review.get("pipeline_id") or PIPELINE_ID),
        "source_run_id": review_id or None,
        "source_review_packet_hash": source_hash,
        "lane": "SHADOW",
        "authority": dict(QUEUE_AUTHORITY),
        "repo_execution_receipt_hash": None,
        "requires_repo_execution_receipt": False,
        "conflicts": [],
        "failed_gates": [],
        "review_completed": False,
        "summary": summary,
        "disposition": disposition,
        "recommended_action": recommended,
    }

    if disposition == "READY_FOR_REVIEW":
        base.update(
            {
                "validation_passed": True,
                "negative_proof_complete": True,
                "operator_review_ready": True,
                "hold_for_operator_decision": False,
                "required_operator_actions": _action_for_recommended(recommended),
                "allowed_decisions": [
                    "HOLD",
                    "APPROVE_SHADOW_STABILIZATION_REVIEW",
                    "REJECT",
                ],
                "stabilization_window": {
                    "required": True,
                    "status": "not_started",
                },
                "not_computable_reasons": [],
            }
        )
    elif disposition == "PENDING_OPERATOR":
        base.update(
            {
                "validation_passed": True,
                "negative_proof_complete": True,
                "operator_review_ready": False,
                "hold_for_operator_decision": True,
                "required_operator_actions": _action_for_recommended(recommended),
                "allowed_decisions": ["HOLD", "REJECT"],
                "stabilization_window": {
                    "required": False,
                    "status": "not_required",
                },
                "not_computable_reasons": [],
            }
        )
    elif disposition == "ABSTAIN":
        reasons = ["FAMILIAR_BRIDGE_ABSTAINED"]
        route = str(review.get("route") or "")
        if route:
            reasons.append(f"route:{route}")
        base.update(
            {
                "validation_passed": True,
                "negative_proof_complete": True,
                "operator_review_ready": False,
                "hold_for_operator_decision": False,
                "required_operator_actions": [],
                "allowed_decisions": ["HOLD"],
                "stabilization_window": {
                    "required": False,
                    "status": "not_required",
                },
                "not_computable_reasons": reasons,
            }
        )
    else:
        # NOT_COMPUTABLE and unknown dispositions → queue state not_computable.
        # Keep validation_passed True so classify does not force repair_required.
        reasons = ["FAMILIAR_REVIEW_NOT_COMPUTABLE"]
        for block in blocked:
            if block and block != "QUEUE_WRITE_BLOCKED":
                reasons.append(str(block))
        base.update(
            {
                "validation_passed": True,
                "negative_proof_complete": True,
                "operator_review_ready": False,
                "hold_for_operator_decision": False,
                "required_operator_actions": [],
                "allowed_decisions": ["HOLD"],
                "stabilization_window": {
                    "required": False,
                    "status": "not_computable",
                },
                "not_computable_reasons": reasons,
            }
        )
    return base


def build_familiar_operator_review_queue_dry_run(
    review: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Map review seed → OperatorReviewQueueItem/Run shape. Never writes queue."""
    if review is None:
        review = build_familiar_operator_review_packet(None)

    normalized = normalize_familiar_operator_review(review)
    item = build_queue_item(normalized)
    source_packets = [
        {
            "path": f"familiar://operator_review/{review.get('review_id') or 'none'}",
            "schema_version": str(
                review.get("schema_version") or SCHEMA_VERSION
            ),
            "source_hash": str(
                review.get("canonical_hash")
                or normalized["source_review_packet_hash"]
            ),
        }
    ]
    queue_run = build_queue_run([item], source_packets)

    body: dict[str, Any] = {
        "schema_version": DRY_RUN_SCHEMA_VERSION,
        "dry_run": True,
        "queue_write_performed": False,
        "queue_write_authorized": False,
        "target_queue_path": QUEUE_TARGET_PATH,
        "pipeline_id": PIPELINE_ID,
        "review_id": review.get("review_id"),
        "disposition": review.get("disposition"),
        "recommended_action": review.get("recommended_action"),
        "review_packet_hash": review.get("canonical_hash"),
        "normalized_packet": normalized,
        "queue_item": item,
        "queue_run": queue_run,
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "lane": "SHADOW",
        "producer": {
            **PRODUCER,
            "stage": "operator_review_queue_dry_run",
        },
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_operator_review_queue_dry_run_from_pack_path(
    path: str | Path,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Pack path → review seed → queue dry-run (pure; no queue write)."""
    review = build_operator_review_from_pack_path(path, repo_root=repo_root)
    return build_familiar_operator_review_queue_dry_run(review)

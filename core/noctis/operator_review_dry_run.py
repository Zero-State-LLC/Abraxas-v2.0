"""Noctis dream packet → operator_review_queue dry-run (no queue / memory write).

Maps NoctisDreamOperatorPacket.v0 onto OperatorReviewQueueItem.v1 /
OperatorReviewQueueRun.v1 shape with optional continuity seed (advisory).
"""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.global_operator_review_queue import build_queue_item, build_queue_run
from core.noctis.dream_operator_packet import build_dream_operator_packet

SCHEMA_VERSION = "NoctisOperatorReviewQueueDryRun.v0"
PIPELINE_ID = "noctis_dream"
QUEUE_TARGET_PATH = "out/operator_review_queue"
DETERMINISTIC_TIMESTAMP = "noctis_operator_review_queue_dry_run_v0_ts_0"

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "queue_write_authorized": False,
    "memory_direct_write_allowed": False,
    "medical_claims_allowed": False,
}

QUEUE_AUTHORITY = {
    "promotion_allowed": False,
    "forecast_weight_allowed": False,
    "runtime_mutation_allowed": False,
    "baseline_mutation_allowed": False,
    "canon_mutation_allowed": False,
}


def _continuity_seed(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Advisory continuity/history link seed — never durable memory write."""
    ir = packet.get("ir") if isinstance(packet.get("ir"), dict) else {}
    motifs = ir.get("motifs") if isinstance(ir.get("motifs"), list) else []
    motif_ids = [
        str(m.get("motif_id") or m.get("label") or "")
        for m in motifs
        if isinstance(m, dict)
    ]
    return {
        "schema_version": "NoctisContinuitySeed.v0",
        "continuity_write_performed": False,
        "memory_direct_write_blocked": True,
        "dream_id": packet.get("dream_id"),
        "packet_id": packet.get("packet_id"),
        "mode": packet.get("mode"),
        "narrative_sha256": packet.get("narrative_sha256"),
        "motif_count": ir.get("motif_count", len(motif_ids)),
        "motif_ids": motif_ids[:32],
        "link_hint": "dream_history_review_optional",
        "status": (
            "SEED_READY"
            if packet.get("readiness") == "SHADOW_OPERATOR_REVIEW"
            else "SEED_BLOCKED"
            if packet.get("readiness") == "BLOCKED"
            else "SEED_NOT_COMPUTABLE"
        ),
    }


def normalize_noctis_operator_review(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Map NoctisDreamOperatorPacket.v0 → global queue normalized packet."""
    readiness = str(packet.get("readiness") or "NOT_COMPUTABLE")
    dream_id = str(packet.get("dream_id") or "")
    packet_id = str(packet.get("packet_id") or "")
    source_hash = str(packet.get("canonical_hash") or packet_id or "missing")
    mode = str(packet.get("mode") or "UNKNOWN")
    analysis = str(packet.get("analysis_status") or "")
    title = (
        f"Noctis dream review: {dream_id}"
        if dream_id
        else "Noctis dream review (no dream_id)"
    )
    ir = packet.get("ir") if isinstance(packet.get("ir"), dict) else {}
    motif_count = int(ir.get("motif_count") or 0)
    summary = (
        f"Noctis {mode} readiness={readiness} analysis={analysis} "
        f"motifs={motif_count}."
    )
    blocks = (
        list(packet.get("blocked_by") or [])
        if isinstance(packet.get("blocked_by"), list)
        else []
    )

    base: dict[str, Any] = {
        "title": title,
        "pipeline_id": str(packet.get("pipeline_id") or PIPELINE_ID),
        "source_run_id": packet_id or dream_id or None,
        "source_review_packet_hash": source_hash,
        "lane": "SHADOW",
        "authority": dict(QUEUE_AUTHORITY),
        "repo_execution_receipt_hash": None,
        "requires_repo_execution_receipt": False,
        "conflicts": [],
        "failed_gates": [],
        "review_completed": False,
        "summary": summary,
        "readiness": readiness,
    }

    if readiness == "SHADOW_OPERATOR_REVIEW":
        base.update(
            {
                "validation_passed": True,
                "negative_proof_complete": True,
                "operator_review_ready": True,
                "hold_for_operator_decision": False,
                "required_operator_actions": [
                    "review_noctis_dream_ir",
                    "acknowledge_memory_write_blocked",
                    "acknowledge_medical_claims_blocked",
                ],
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
    elif readiness == "BLOCKED":
        base.update(
            {
                "validation_passed": True,
                "negative_proof_complete": True,
                "operator_review_ready": False,
                "hold_for_operator_decision": True,
                "required_operator_actions": [
                    "resolve_noctis_privacy_medical_gate",
                    "collect_operator_decision_evidence",
                ],
                "allowed_decisions": ["HOLD", "REJECT"],
                "stabilization_window": {
                    "required": False,
                    "status": "not_required",
                },
                "not_computable_reasons": [],
            }
        )
    else:
        reasons = ["NOCTIS_REVIEW_NOT_COMPUTABLE"]
        for block in blocks:
            if block and block not in (
                "MEDICAL_CLAIMS_BLOCKED",
                "FORECAST_ROUTING_BLOCKED",
                "MEMORY_DIRECT_WRITE_BLOCKED",
            ):
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


def build_noctis_operator_review_queue_dry_run(
    packet: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Dream packet → queue Item/Run dry-run + continuity seed. Never writes."""
    if packet is None:
        packet = build_dream_operator_packet(narrative_raw="")

    normalized = normalize_noctis_operator_review(packet)
    item = build_queue_item(normalized)
    source_packets = [
        {
            "path": f"noctis://dream/{packet.get('dream_id') or 'none'}",
            "schema_version": str(
                packet.get("schema_version") or "NoctisDreamOperatorPacket.v0"
            ),
            "source_hash": str(
                packet.get("canonical_hash")
                or normalized["source_review_packet_hash"]
            ),
        }
    ]
    queue_run = build_queue_run([item], source_packets)
    continuity = _continuity_seed(packet)

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "dry_run": True,
        "queue_write_performed": False,
        "queue_write_authorized": False,
        "memory_write_performed": False,
        "target_queue_path": QUEUE_TARGET_PATH,
        "pipeline_id": PIPELINE_ID,
        "dream_id": packet.get("dream_id"),
        "packet_id": packet.get("packet_id"),
        "readiness": packet.get("readiness"),
        "source_packet_hash": packet.get("canonical_hash"),
        "normalized_packet": normalized,
        "queue_item": item,
        "queue_run": queue_run,
        "continuity_seed": continuity,
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "lane": "SHADOW_SYMBOLIC",
        "producer": {
            "module": "core.noctis.operator_review_dry_run",
            "upstream": "core.noctis.dream_operator_packet",
            "pipeline_id": PIPELINE_ID,
        },
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
        "medical_claims_blocked": True,
        "forecast_routing_blocked": True,
        "memory_direct_write_blocked": True,
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_noctis_review_dry_run_from_narrative(
    narrative_raw: str,
    *,
    mode: str = "SYSTEM_DREAM",
    privacy_tier: str = "PUBLIC_SYNTHETIC",
    dream_id: str | None = None,
    source: str = "SYSTEM",
    seed: str = "0",
) -> dict[str, Any]:
    """Narrative → dream packet → review queue dry-run (pure)."""
    packet = build_dream_operator_packet(
        mode=mode,
        dream_id=dream_id,
        source=source,
        privacy_tier=privacy_tier,
        narrative_raw=narrative_raw,
        seed=seed,
    )
    return build_noctis_operator_review_queue_dry_run(packet)

"""Neon Genie ideation operator packet — novelty/overlap SHADOW receipt.

Closes neon_genie_ideation MISSING_CONTRACT at the operator-packet layer.
Does not package Hermes Hub skills, network, promote, or grant execution.
"""

from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash
from core.signal.evidence_pack import commercial_claims_blocked

SCHEMA_VERSION = "NeonGenieIdeationOperatorPacket.v0"
PIPELINE_ID = "neon_genie_ideation"
DETERMINISTIC_TIMESTAMP = "neon_genie_ideation_operator_packet_v0_ts_0"

OVERLAP_CLASSES = frozenset(
    {
        "NOVEL",
        "ADJACENT",
        "WRAPPER_CANDIDATE",
        "CHILD_SUBSYSTEM",
        "DUPLICATE",
        "NOT_COMPUTABLE",
    }
)
INPUT_MODES = frozenset(
    {
        "PROMPT_LED",
        "MARKET_LED",
        "CAPABILITY_LED",
        "CONSTRAINT_LED",
        "TREND_LED",
        "PAINPOINT_LED",
        "SYMBOLIC_LED",
        "MONETIZATION_LED",
        "UNKNOWN",
    }
)

DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
}

PRODUCER = {
    "module": "core.neon_genie.ideation_operator_packet",
    "skill_id": "abx-neon-genie",
    "pipeline_id": PIPELINE_ID,
}


def _norm_overlap(raw: Any) -> str:
    s = str(raw or "NOT_COMPUTABLE").strip().upper()
    if s not in OVERLAP_CLASSES:
        return "NOT_COMPUTABLE"
    return s


def _norm_mode(raw: Any) -> str:
    s = str(raw or "UNKNOWN").strip().upper()
    if s not in INPUT_MODES:
        return "UNKNOWN"
    return s


def build_ideation_operator_packet(
    *,
    input_mode: str = "UNKNOWN",
    venture_name: str = "Unnamed Venture",
    output_class: str = "HYBRID",
    overlap_classification: str = "NOT_COMPUTABLE",
    novelty_notes: str = "",
    route_binding: str = "internal",
    evidence_pack: dict[str, Any] | None = None,
    score_vector: dict[str, Any] | None = None,
    blocked_by: list[str] | None = None,
) -> dict[str, Any]:
    """Build a deterministic SHADOW operator packet for neon_genie_ideation."""
    pack = evidence_pack if isinstance(evidence_pack, dict) else {}
    blocked = commercial_claims_blocked(pack) if pack else True
    overlap = _norm_overlap(overlap_classification)
    mode = _norm_mode(input_mode)

    blocks = list(blocked_by or [])
    if blocked and "COMMERCIAL_EVIDENCE_REQUIRED" not in blocks:
        blocks.append("COMMERCIAL_EVIDENCE_REQUIRED")
    if overlap in {"DUPLICATE", "NOT_COMPUTABLE"} and "OVERLAP_GATE" not in blocks:
        blocks.append("OVERLAP_GATE")

    readiness = "SHADOW_OPERATOR_REVIEW"
    if overlap == "DUPLICATE":
        readiness = "BLOCKED"
    elif not pack:
        readiness = "NOT_COMPUTABLE"

    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_id": PIPELINE_ID,
        "packet_id": "ng_ideation_" + canonical_hash(
            {
                "mode": mode,
                "name": venture_name,
                "overlap": overlap,
                "pack_ref": pack.get("pack_ref") or pack.get("pack_id") or "",
            }
        )[:16],
        "input_mode": mode,
        "venture_name": str(venture_name or "Unnamed Venture"),
        "output_class": str(output_class or "HYBRID"),
        "overlap_classification": overlap,
        "novelty_notes": str(novelty_notes or ""),
        "route_binding": str(route_binding or "internal"),
        "evidence_pack_ref": pack.get("pack_ref") or pack.get("pack_id"),
        "evidence_status": str(pack.get("status") or "NOT_COMPUTABLE"),
        "commercial_claims_blocked": bool(blocked),
        "score_vector": dict(score_vector or {}),
        "blocked_by": blocks,
        "readiness": readiness,
        "authority": dict(DEFAULT_AUTHORITY),
        "producer": dict(PRODUCER),
        "deterministic_timestamp": DETERMINISTIC_TIMESTAMP,
    }
    body["canonical_hash"] = canonical_hash(body)
    return body


def build_ideation_operator_packet_from_venture(
    venture_packet: dict[str, Any],
    *,
    evidence_pack: dict[str, Any] | None = None,
    novelty_notes: str = "",
) -> dict[str, Any]:
    """Lift fields from a NeonGenieVenturePacket-like dict into the operator packet."""
    vp = venture_packet if isinstance(venture_packet, dict) else {}
    return build_ideation_operator_packet(
        input_mode=str(vp.get("input_mode") or "UNKNOWN"),
        venture_name=str(vp.get("venture_name") or "Unnamed Venture"),
        output_class=str(vp.get("output_class") or "HYBRID"),
        overlap_classification=str(vp.get("overlap_classification") or "NOT_COMPUTABLE"),
        novelty_notes=novelty_notes
        or str(vp.get("novelty_notes") or vp.get("why_now_basis") or ""),
        route_binding=str(vp.get("route_binding") or "internal"),
        evidence_pack=evidence_pack
        or (
            {"pack_ref": vp.get("evidence_pack_ref"), "status": vp.get("evidence_basis")}
            if vp.get("evidence_pack_ref") or vp.get("evidence_basis")
            else None
        ),
        score_vector=vp.get("score_vector") if isinstance(vp.get("score_vector"), dict) else {},
        blocked_by=list(vp.get("blocked_by") or [])
        if isinstance(vp.get("blocked_by"), list)
        else None,
    )

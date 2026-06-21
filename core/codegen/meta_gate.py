from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.codegen.builder import DEFAULT_LANE_SIGNALS, DEFAULT_PROVENANCE

from contracts.codegen import MetaGateSeal

META_GATE_REVIEW_SCHEMA_VERSION = "CodegenMetaGateReview.v1"


def _summary_passed(fixture_summary: Mapping[str, Any]) -> bool:
    return fixture_summary.get("status") == "FIXTURE_VALIDATION_SUMMARY_PASSED"


def _seal_id(payload: Mapping[str, Any]) -> str:
    return canonical_hash(payload)


def _canonical_hash_without_existing(value: Mapping[str, Any]) -> str:
    payload = dict(value)
    payload.pop("canonical_hash", None)
    return canonical_hash(payload)


def build_meta_gate_review(
    fixture_summary: Mapping[str, Any],
    *,
    reviewed_envelope_id: str,
    timestamp: str,
    brier_score: float = 0.1,
) -> dict[str, Any]:
    summary_passed = _summary_passed(fixture_summary)
    recommendation = "HOLD_FOR_OPERATOR" if summary_passed else "BLOCK_REPLAY_FAILURE"
    seal_payload: dict[str, Any] = {
        "schema_version": "MetaGateSeal.v1",
        "timestamp": timestamp,
        "reviewed_envelope_id": reviewed_envelope_id,
        "recommendation": recommendation,
        "brier_score": brier_score,
        "lane_signals": DEFAULT_LANE_SIGNALS,
        "provenance": DEFAULT_PROVENANCE,
    }
    seal_payload["seal_id"] = _seal_id(seal_payload)
    seal = MetaGateSeal.model_validate(seal_payload)
    base: dict[str, Any] = {
        "schema_version": META_GATE_REVIEW_SCHEMA_VERSION,
        "status": (
            "META_GATE_REVIEW_HELD_FOR_OPERATOR"
            if summary_passed
            else "META_GATE_REVIEW_BLOCKED_BY_REPLAY"
        ),
        "timestamp": timestamp,
        "reviewed_envelope_id": reviewed_envelope_id,
        "fixture_summary_hash": canonical_hash(fixture_summary),
        "fixture_summary_status": str(fixture_summary.get("status", "UNKNOWN")),
        "seal": seal.model_dump(),
        "promotion_allowed": False,
        "operator_gate_required": True,
        "operator_attestation_required": True,
        "advisory_only": True,
        "execution_authority": False,
        "runtime_mutation": False,
        "canon_mutation": False,
        "github_writeback": False,
        "notion_writeback": False,
        "recommended_next": (
            "PHASE_5_NOTION_RECONCILIATION_DRYRUN"
            if summary_passed
            else "REPAIR_FIXTURE_VALIDATION_BEFORE_META_GATE"
        ),
        "brier_score": brier_score,
    }
    return {**base, "canonical_hash": _canonical_hash_without_existing(base)}

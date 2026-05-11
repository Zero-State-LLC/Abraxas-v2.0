from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from .models import *
from .validator import validate_temporal_operator_review_projection_queue

SCHEMA_VERSION = "TemporalClimateOperatorReviewProjectionQueue.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_temporal_operator_review_projection_queue_json(queue: TemporalClimateOperatorReviewProjectionQueue | Mapping[str, Any]) -> str:
    payload = asdict(queue) if isinstance(queue, TemporalClimateOperatorReviewProjectionQueue) else dict(queue)
    payload.pop("queue_hash", None)
    return _canonical_json(payload)


def temporal_operator_review_projection_queue_hash(queue: TemporalClimateOperatorReviewProjectionQueue | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_temporal_operator_review_projection_queue_json(queue))


def compute_temporal_operator_review_posture(queue_items: Sequence[Mapping[str, Any]], risk_surfaces: Sequence[Mapping[str, Any]]) -> str:
    if any(s.get("severity") == "BLOCKED" for s in risk_surfaces):
        return "BLOCKED"
    if any(s.get("surface_type") == "TOPOLOGY_FRACTURE" for s in risk_surfaces):
        return "FRACTURE_RISK"
    if any(s.get("surface_type") == "REGIME_INSTABILITY" for s in risk_surfaces):
        return "REGIME_RISK"
    if any(s.get("surface_type") == "PRESSURE_ESCALATION" for s in risk_surfaces):
        return "PRESSURE"
    if any(i.get("item_posture") == "WATCH" for i in queue_items):
        return "WATCH"
    return "STABLE" if queue_items or risk_surfaces else "INSUFFICIENT_INPUTS"


def build_temporal_operator_review_projection_queue(queue_id: str, input_refs: tuple[TemporalOperatorReviewInputRef, ...], queue_items: tuple[TemporalOperatorReviewQueueItem, ...], priority_bands: tuple[TemporalOperatorReviewPriorityBand, ...], risk_surfaces: tuple[TemporalOperatorReviewRiskSurface, ...], recommendations: tuple[TemporalOperatorReviewRecommendation, ...], queue_status: str, queue_posture: str, queue_policy: str, created_by_lane: str, authority_ref: dict | None) -> TemporalClimateOperatorReviewProjectionQueue:
    draft = TemporalClimateOperatorReviewProjectionQueue(SCHEMA_VERSION, queue_id, input_refs, queue_items, priority_bands, risk_surfaces, recommendations, queue_status, queue_posture, queue_policy, created_by_lane, authority_ref, True, False, False, False, False, False, False, False, False, False, False, "PENDING")
    return replace(draft, queue_hash=temporal_operator_review_projection_queue_hash(draft))


def derive_temporal_operator_review_projection_queue(bindings: Sequence[Mapping[str, Any]], input_refs: Sequence[Mapping[str, Any]] | None = None) -> TemporalClimateOperatorReviewProjectionQueue:
    refs = tuple(TemporalOperatorReviewInputRef(str(r.get("source_type", "NOT_COMPUTABLE")), str(r.get("source_id", "")), str(r.get("source_hash", ""))) for r in (input_refs or []))
    if not bindings:
        return build_temporal_operator_review_projection_queue("queue-1", refs, tuple(), (TemporalOperatorReviewPriorityBand("band-0", "NOT_COMPUTABLE", 0, True, True),), (TemporalOperatorReviewRiskSurface("rs-0", "NOT_COMPUTABLE", "NOT_COMPUTABLE", tuple(), True, False),), (TemporalOperatorReviewRecommendation("rec-0", "NOT_COMPUTABLE", True, False, False, False),), "NOT_COMPUTABLE", "NOT_COMPUTABLE", "PROJECTION_ONLY", "PROJECTION", None)

    b = bindings[-1]
    items=[]; surfaces=[]
    if str(b.get("binding_status", "")) in {"VIZ_STABLE", "BINDING_READY"}:
        items.append(TemporalOperatorReviewQueueItem("it-stable", "REVIEW_ALERT", "Stable Review Surface", "Binding is stable and review-ready.", "PASS", 1, tuple(), True, False))
    for i, a in enumerate(b.get("alert_surfaces", ()), start=1):
        at = str(a.get("alert_type", "NOT_COMPUTABLE")); sv = str(a.get("severity", "NOT_COMPUTABLE"))
        if at == "BLOCKED_HISTORY_PRESENT":
            items.append(TemporalOperatorReviewQueueItem(f"it-{i}", "BLOCKED_HISTORY", "Blocked History", "Blocked history remains visible.", "BLOCKED", i, tuple(a.get("source_ref_ids", ())), True, False))
            surfaces.append(TemporalOperatorReviewRiskSurface(f"rs-{i}", "BLOCKED_HISTORY", "BLOCKED", tuple(a.get("source_ref_ids", ())), True, False))
        elif at == "NONDETERMINISM_PRESENT":
            items.append(TemporalOperatorReviewQueueItem(f"it-{i}", "NONDETERMINISM_CLUSTER", "Nondeterminism Cluster", "Nondeterminism remains visible.", "BLOCKED", i, tuple(a.get("source_ref_ids", ())), True, False))
            surfaces.append(TemporalOperatorReviewRiskSurface(f"rs-{i}", "NONDETERMINISM", "BLOCKED", tuple(a.get("source_ref_ids", ())), True, False))
        elif at == "FRACTURE_ESCALATION":
            items.append(TemporalOperatorReviewQueueItem(f"it-{i}", "FRACTURE_CLUSTER", "Fracture Escalation", "Fracture risk requires review.", "WARN", i, tuple(a.get("source_ref_ids", ())), True, False))
            surfaces.append(TemporalOperatorReviewRiskSurface(f"rs-{i}", "TOPOLOGY_FRACTURE", "WARN", tuple(a.get("source_ref_ids", ())), True, False))
        elif at == "REGIME_TRANSITION_RISK":
            items.append(TemporalOperatorReviewQueueItem(f"it-{i}", "REGIME_SHIFT", "Regime Shift", "Regime transition risk detected.", "WARN", i, tuple(a.get("source_ref_ids", ())), True, False))
            surfaces.append(TemporalOperatorReviewRiskSurface(f"rs-{i}", "REGIME_INSTABILITY", "WARN", tuple(a.get("source_ref_ids", ())), True, False))
        elif at == "PRESSURE_BUILDING":
            items.append(TemporalOperatorReviewQueueItem(f"it-{i}", "PRESSURE_SPIKE", "Pressure Spike", "Pressure building signal detected.", "WATCH", i, tuple(a.get("source_ref_ids", ())), True, False))
            surfaces.append(TemporalOperatorReviewRiskSurface(f"rs-{i}", "PRESSURE_ESCALATION", sv, tuple(a.get("source_ref_ids", ())), True, False))

    posture = compute_temporal_operator_review_posture([asdict(x) for x in items], [asdict(x) for x in surfaces])
    if posture == "BLOCKED": status = "OPERATOR_REVIEW_REQUIRED"
    elif posture == "FRACTURE_RISK": status = "REVIEW_FRACTURE_RISK"
    elif posture == "REGIME_RISK": status = "REVIEW_REGIME_RISK"
    elif posture == "PRESSURE": status = "REVIEW_PRESSURE"
    elif posture == "WATCH": status = "REVIEW_WATCH"
    elif posture == "STABLE": status = "REVIEW_STABLE"
    else: status = "INSUFFICIENT_BINDING_INPUTS"

    if any(i.item_type == "BLOCKED_HISTORY" for i in items): status = "BLOCKED_HISTORY_VISIBLE"
    if any(i.item_type == "NONDETERMINISM_CLUSTER" for i in items): status = "NONDETERMINISM_VISIBLE" if status != "BLOCKED_HISTORY_VISIBLE" else status

    bands = (
        TemporalOperatorReviewPriorityBand("band-low", "LOW", sum(1 for i in items if i.item_posture == "PASS"), False, True),
        TemporalOperatorReviewPriorityBand("band-med", "MEDIUM", sum(1 for i in items if i.item_posture == "WATCH"), True, True),
        TemporalOperatorReviewPriorityBand("band-high", "HIGH", sum(1 for i in items if i.item_posture == "WARN"), True, True),
        TemporalOperatorReviewPriorityBand("band-block", "BLOCKED", sum(1 for i in items if i.item_posture == "BLOCKED"), True, True),
    )
    rec = (TemporalOperatorReviewRecommendation("rec-1", "REQUEST_OPERATOR_REVIEW" if status in {"OPERATOR_REVIEW_REQUIRED", "BLOCKED_HISTORY_VISIBLE", "NONDETERMINISM_VISIBLE", "REVIEW_UNSTABLE", "REVIEW_FRACTURE_RISK", "REVIEW_REGIME_RISK", "REVIEW_PRESSURE"} else "REVIEW_ONLY", True, False, False, False),)
    return build_temporal_operator_review_projection_queue("queue-1", refs, tuple(items), bands, tuple(surfaces), rec, status, posture, "PROJECTION_ONLY", "PROJECTION", None)


def write_temporal_operator_review_projection_queue_contract_audit(base_dir: Path | str = ".") -> str:
    q = derive_temporal_operator_review_projection_queue([
        {"binding_status": "VIZ_PRESSURE", "alert_surfaces": ({"alert_type": "PRESSURE_BUILDING", "severity": "WATCH", "source_ref_ids": ()}, {"alert_type": "REGIME_TRANSITION_RISK", "severity": "WARN", "source_ref_ids": ()})}
    ], [{"source_type": "TEMPORAL_CLIMATE_AAL_VIZ_BINDING", "source_id": "b1", "source_hash": "h1"}])
    report = validate_temporal_operator_review_projection_queue(q)
    payload = {"status": report.status, "queue_hash": q.queue_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": q.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/temporal_climate_operator_review_projection_queue_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)

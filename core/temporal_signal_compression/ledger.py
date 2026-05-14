from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from .models import TemporalCompressionInputRef, TemporalCompressionCluster, TemporalCompressionMotif, TemporalCompressionPressureBand, TemporalCompressionObservation, TemporalCompressionRecommendation, TemporalClimateSignalCompressionLedger
from .validator import validate_temporal_signal_compression_ledger

SCHEMA_VERSION = "TemporalClimateSignalCompressionLedger.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_temporal_signal_compression_ledger_json(ledger: TemporalClimateSignalCompressionLedger | Mapping[str, Any]) -> str:
    payload = asdict(ledger) if isinstance(ledger, TemporalClimateSignalCompressionLedger) else dict(ledger)
    payload.pop("ledger_hash", None)
    return _canonical_json(payload)


def temporal_signal_compression_ledger_hash(ledger: TemporalClimateSignalCompressionLedger | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_temporal_signal_compression_ledger_json(ledger))


def compute_temporal_signal_compression_posture(clusters: Sequence[Mapping[str, Any]], bands: Sequence[Mapping[str, Any]], observations: Sequence[Mapping[str, Any]]) -> str:
    if any(c.get("cluster_type") == "BLOCKED_HISTORY_CLUSTER" for c in clusters):
        return "BLOCKED"
    if any(c.get("cluster_type") == "NONDETERMINISM_CLUSTER" for c in clusters):
        return "NONDETERMINISM"
    if any(b.get("overloaded") for b in bands):
        return "OVERLOADED"
    if any(c.get("cluster_type") == "FRACTURE_CLUSTER" for c in clusters):
        return "FRACTURE_RISK"
    if any(c.get("cluster_type") == "REGIME_CLUSTER" for c in clusters):
        return "REGIME_RISK"
    if any(c.get("cluster_type") == "PRESSURE_CLUSTER" for c in clusters):
        return "PRESSURE"
    if clusters or observations:
        return "WATCH"
    return "INSUFFICIENT_INPUTS"


def build_temporal_signal_compression_ledger(ledger_id: str, input_refs: tuple[TemporalCompressionInputRef, ...], compression_clusters: tuple[TemporalCompressionCluster, ...], compression_motifs: tuple[TemporalCompressionMotif, ...], pressure_bands: tuple[TemporalCompressionPressureBand, ...], observations: tuple[TemporalCompressionObservation, ...], recommendations: tuple[TemporalCompressionRecommendation, ...], ledger_status: str, ledger_posture: str, compression_policy: str, created_by_lane: str, authority_ref: dict | None) -> TemporalClimateSignalCompressionLedger:
    draft = TemporalClimateSignalCompressionLedger(SCHEMA_VERSION, ledger_id, input_refs, compression_clusters, compression_motifs, pressure_bands, observations, recommendations, ledger_status, ledger_posture, compression_policy, created_by_lane, authority_ref, True, False, False, False, False, False, False, False, False, False, False, False, "PENDING")
    return replace(draft, ledger_hash=temporal_signal_compression_ledger_hash(draft))


def derive_temporal_signal_compression_ledger(queues: Sequence[Mapping[str, Any]], input_refs: Sequence[Mapping[str, Any]] | None = None) -> TemporalClimateSignalCompressionLedger:
    refs = tuple(TemporalCompressionInputRef(str(r.get("source_type", "NOT_COMPUTABLE")), str(r.get("source_id", "")), str(r.get("source_hash", ""))) for r in (input_refs or []))
    if not queues:
        return build_temporal_signal_compression_ledger("ledger-1", refs, tuple(), tuple(), (TemporalCompressionPressureBand("pb-0", "NOT_COMPUTABLE", 0, False, True),), (TemporalCompressionObservation("ob-0", "NOT_COMPUTABLE", "NOT_COMPUTABLE", True, False),), (TemporalCompressionRecommendation("rec-0", "NOT_COMPUTABLE", False, False, False, False, False),), "NOT_COMPUTABLE", "NOT_COMPUTABLE", "PROJECTION_ONLY", "PROJECTION", None)

    q = queues[-1]
    clusters=[]
    observations=[]
    for i, it in enumerate(q.get("queue_items", ()), start=1):
        itype = str(it.get("item_type", "NOT_COMPUTABLE"))
        if itype == "PRESSURE_SPIKE":
            clusters.append(TemporalCompressionCluster(f"cl-{i}", "PRESSURE_CLUSTER", "WATCH", 1, tuple(it.get("source_ref_ids", ())), True, False, False))
            observations.append(TemporalCompressionObservation(f"ob-{i}", "PRESSURE_ESCALATION", "WATCH", True, False))
        elif itype == "REGIME_SHIFT":
            clusters.append(TemporalCompressionCluster(f"cl-{i}", "REGIME_CLUSTER", "WARN", 1, tuple(it.get("source_ref_ids", ())), True, False, False))
            observations.append(TemporalCompressionObservation(f"ob-{i}", "REGIME_DESTABILIZATION", "WARN", True, False))
        elif itype == "FRACTURE_CLUSTER":
            clusters.append(TemporalCompressionCluster(f"cl-{i}", "FRACTURE_CLUSTER", "WARN", 1, tuple(it.get("source_ref_ids", ())), True, False, False))
            observations.append(TemporalCompressionObservation(f"ob-{i}", "FRACTURE_DENSITY", "WARN", True, False))
        elif itype == "NONDETERMINISM_CLUSTER":
            clusters.append(TemporalCompressionCluster(f"cl-{i}", "NONDETERMINISM_CLUSTER", "BLOCKED", 1, tuple(it.get("source_ref_ids", ())), True, False, False))
            observations.append(TemporalCompressionObservation(f"ob-{i}", "NONDETERMINISM_ESCALATION", "BLOCKED", True, False))
        elif itype == "BLOCKED_HISTORY":
            clusters.append(TemporalCompressionCluster(f"cl-{i}", "BLOCKED_HISTORY_CLUSTER", "BLOCKED", 1, tuple(it.get("source_ref_ids", ())), True, False, False))
            observations.append(TemporalCompressionObservation(f"ob-{i}", "BLOCKED_HISTORY_ACCUMULATION", "BLOCKED", True, False))

    motifs=[]
    if any(c.cluster_type == "PRESSURE_CLUSTER" for c in clusters):
        motifs.append(TemporalCompressionMotif("m-1", "RECURSIVE_PRESSURE", 0.6, "MEDIUM", True, False))
    if any(c.cluster_type == "REGIME_CLUSTER" for c in clusters):
        motifs.append(TemporalCompressionMotif("m-2", "RECURRING_REGIME_SHIFT", 0.7, "HIGH", True, False))
    if any(c.cluster_type == "FRACTURE_CLUSTER" for c in clusters):
        motifs.append(TemporalCompressionMotif("m-3", "FRACTURE_PROPAGATION", 0.8, "HIGH", True, False))
    if any(c.cluster_type == "NONDETERMINISM_CLUSTER" for c in clusters):
        motifs.append(TemporalCompressionMotif("m-4", "NONDETERMINISM_RECURSION", 0.9, "BLOCKED", True, False))
    if any(c.cluster_type == "BLOCKED_HISTORY_CLUSTER" for c in clusters):
        motifs.append(TemporalCompressionMotif("m-5", "BLOCKED_HISTORY_RECURSION", 0.9, "BLOCKED", True, False))

    overloaded = len(clusters) >= 4 and any(m.motif_visibility in {"CRITICAL", "BLOCKED"} for m in motifs)
    bands = (
        TemporalCompressionPressureBand("pb-low", "LOW", sum(1 for c in clusters if c.cluster_posture == "PASS"), False, True),
        TemporalCompressionPressureBand("pb-high", "HIGH", sum(1 for c in clusters if c.cluster_posture in {"WATCH", "WARN"}), overloaded, True),
        TemporalCompressionPressureBand("pb-block", "BLOCKED", sum(1 for c in clusters if c.cluster_posture == "BLOCKED"), any(c.cluster_posture == "BLOCKED" for c in clusters), True),
    )

    posture = compute_temporal_signal_compression_posture([asdict(c) for c in clusters], [asdict(b) for b in bands], [asdict(o) for o in observations])
    if posture == "BLOCKED":
        status = "BLOCKED_HISTORY_VISIBLE" if any(c.cluster_type == "BLOCKED_HISTORY_CLUSTER" for c in clusters) else "COMPRESSED_NONDETERMINISM"
    elif posture == "NONDETERMINISM":
        status = "COMPRESSED_NONDETERMINISM"
    elif posture == "OVERLOADED":
        status = "SIGNAL_OVERLOAD"
    elif posture == "FRACTURE_RISK":
        status = "COMPRESSED_FRACTURE_RISK"
    elif posture == "REGIME_RISK":
        status = "COMPRESSED_REGIME_RISK"
    elif posture == "PRESSURE":
        status = "COMPRESSED_PRESSURE"
    elif posture == "STABLE":
        status = "COMPRESSED_STABLE"
    else:
        status = "COMPRESSED"

    rec = (TemporalCompressionRecommendation("rec-1", "REQUEST_OPERATOR_REVIEW" if status in {"SIGNAL_OVERLOAD","BLOCKED_HISTORY_VISIBLE","COMPRESSED_NONDETERMINISM","COMPRESSED_FRACTURE_RISK","COMPRESSED_REGIME_RISK","COMPRESSED_PRESSURE"} else "REVIEW_ONLY", False, False, False, False, False),)
    return build_temporal_signal_compression_ledger("ledger-1", refs, tuple(clusters), tuple(motifs), bands, tuple(observations), rec, status, posture, "PROJECTION_ONLY", "PROJECTION", None)


def write_temporal_signal_compression_ledger_contract_audit(base_dir: Path | str = ".") -> str:
    ledger_entry = derive_temporal_signal_compression_ledger([
        {"queue_items": ({"item_type": "PRESSURE_SPIKE", "source_ref_ids": ()}, {"item_type": "REGIME_SHIFT", "source_ref_ids": ()})}
    ], [{"source_type": "TEMPORAL_OPERATOR_REVIEW_QUEUE", "source_id": "q1", "source_hash": "h1"}])
    report = validate_temporal_signal_compression_ledger(ledger_entry)
    payload = {"status": report.status, "ledger_hash": ledger_entry.ledger_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": ledger_entry.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/temporal_climate_signal_compression_ledger_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)

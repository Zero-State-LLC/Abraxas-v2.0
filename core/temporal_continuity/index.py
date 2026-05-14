from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from .models import TemporalContinuityInputRef, TemporalContinuityComponentScore, TemporalContinuityMetric, TemporalContinuityFinding, TemporalContinuityRecommendation, TemporalContinuityIndex
from .validator import validate_temporal_continuity_index

SCHEMA_VERSION = "TemporalContinuityIndex.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_temporal_continuity_index_json(index: TemporalContinuityIndex | Mapping[str, Any]) -> str:
    payload = asdict(index) if isinstance(index, TemporalContinuityIndex) else dict(index)
    payload.pop("index_hash", None)
    return _canonical_json(payload)


def temporal_continuity_index_hash(index: TemporalContinuityIndex | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_temporal_continuity_index_json(index))


def compute_temporal_continuity_score(component_scores: Sequence[Mapping[str, Any]]) -> tuple[float, str]:
    weights = [float(c.get("weight", 0.0)) for c in component_scores]
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0, "NOT_COMPUTABLE"
    weighted = sum(max(0.0, min(1.0, float(c.get("normalized_score", 0.0)))) * float(c.get("weight", 0.0)) for c in component_scores) / total_weight
    score = round(weighted, 10)
    posture = "STABLE" if score >= 0.85 else ("MIXED" if score >= 0.55 else "UNSTABLE")
    return score, posture


def build_temporal_continuity_index(index_id: str, input_refs: tuple[TemporalContinuityInputRef, ...], component_scores: tuple[TemporalContinuityComponentScore, ...], metrics: tuple[TemporalContinuityMetric, ...], findings: tuple[TemporalContinuityFinding, ...], recommendations: tuple[TemporalContinuityRecommendation, ...], continuity_score: float, continuity_posture: str, index_status: str, index_policy: str, created_by_lane: str, authority_ref: dict | None) -> TemporalContinuityIndex:
    draft = TemporalContinuityIndex(SCHEMA_VERSION, index_id, input_refs, component_scores, metrics, findings, recommendations, continuity_score, continuity_posture, index_status, index_policy, created_by_lane, authority_ref, False, False, False, False, False, False, "PENDING")
    return replace(draft, index_hash=temporal_continuity_index_hash(draft))


def derive_temporal_continuity_index(consensus_reviews: Sequence[Mapping[str, Any]], input_refs: Sequence[Mapping[str, Any]] | None = None) -> TemporalContinuityIndex:
    refs = tuple(TemporalContinuityInputRef(str(r.get("source_type", "NOT_COMPUTABLE")), str(r.get("source_id", "")), str(r.get("source_hash", ""))) for r in (input_refs or []))
    if not consensus_reviews:
        f = (TemporalContinuityFinding("f-missing", "NOT_COMPUTABLE", "NOT_COMPUTABLE", tuple(), "No consensus reviews supplied.", False),)
        rec = (TemporalContinuityRecommendation("rec-1", "NOT_COMPUTABLE", "Continuity not computable without review history.", True, False, False, False, False),)
        m = (TemporalContinuityMetric("m-score", "NOT_COMPUTABLE", 0.0, "PRESERVE_ALL_LINEAGES", "NOT_COMPUTABLE"),)
        return build_temporal_continuity_index("index-1", refs, tuple(), m, f, rec, 0.0, "NOT_COMPUTABLE", "NOT_COMPUTABLE", "PRESERVE_ALL_LINEAGES", "FORECAST", None)

    statuses = [str(r.get("review_status", "NOT_COMPUTABLE")) for r in consensus_reviews]
    blocked = sum(1 for r in consensus_reviews for f in r.get("consensus_findings", ()) if str(f.get("severity", "")).upper() == "BLOCKED" or f.get("finding_type") == "BLOCKED_HISTORY_PRESENT")
    nondet = sum(1 for r in consensus_reviews for f in r.get("consensus_findings", ()) if f.get("finding_type") == "NONDETERMINISM_PRESSURE")
    n = len(consensus_reviews)
    strong = sum(1 for s in statuses if s in {"CONSENSUS_PRESENT", "STRONG_CONSENSUS"})
    partial = sum(1 for s in statuses if s in {"PARTIAL_CONSENSUS", "CONSENSUS_PARTIAL"})
    conflict = sum(1 for s in statuses if s in {"CONSENSUS_CONFLICT", "CONFLICTED"})

    components = (
        TemporalContinuityComponentScore("c-replay", "REPLAY_STABILITY", float(strong), strong / max(1, n), 1.0, "STABLE" if strong == n else "MIXED", False),
        TemporalContinuityComponentScore("c-consensus", "CONSENSUS_PERSISTENCE", float(strong), strong / max(1, n), 1.0, "STABLE" if strong == n else "MIXED", False),
        TemporalContinuityComponentScore("c-arb-vol", "ARBITRATION_VOLATILITY", float(conflict + partial), 1.0 - ((conflict + partial) / max(1, n)), 1.0, "UNSTABLE" if conflict else "MIXED", False),
        TemporalContinuityComponentScore("c-blocked", "BLOCKED_HISTORY_PRESSURE", float(blocked), 1.0 - min(1.0, blocked / max(1, n)), 1.0, "UNSTABLE" if blocked else "STABLE", False),
        TemporalContinuityComponentScore("c-nondet", "NONDETERMINISM_PRESSURE", float(nondet), 1.0 - min(1.0, nondet / max(1, n)), 1.0, "UNSTABLE" if nondet else "STABLE", False),
    )
    score, posture = compute_temporal_continuity_score([asdict(c) for c in components])
    findings = []
    if n < 2:
        posture = "INSUFFICIENT_HISTORY"
        findings.append(TemporalContinuityFinding("f-insuf", "INSUFFICIENT_HISTORY", "WARN", tuple(), "At least two review epochs required.", False))
        status = "INSUFFICIENT_HISTORY"
    elif blocked > 0 or nondet > 0:
        if blocked > 0:
            findings.append(TemporalContinuityFinding("f-blocked", "BLOCKED_HISTORY_PRESSURE", "BLOCKED", tuple(), "Blocked-history pressure remains visible.", False))
        if nondet > 0:
            findings.append(TemporalContinuityFinding("f-nondet", "NONDETERMINISM_PRESSURE", "BLOCKED", tuple(), "Nondeterminism pressure remains visible.", False))
        status = "OPERATOR_REVIEW_REQUIRED" if nondet > 0 else "CONTINUITY_UNSTABLE"
    elif strong == n:
        findings.append(TemporalContinuityFinding("f-stable", "CONTINUITY_STABLE", "INFO", tuple(), "Strong consensus persistence across windows.", False))
        status = "CONTINUITY_STABLE"
    elif strong > 0 and partial > 0:
        findings.append(TemporalContinuityFinding("f-mixed", "CONSENSUS_VOLATILITY", "WARN", tuple(), "Mixed strong and partial consensus windows.", False))
        status = "CONTINUITY_MIXED"
    else:
        findings.append(TemporalContinuityFinding("f-decay", "CONTINUITY_DECAY", "WARN", tuple(), "Continuity decay detected from conflicting windows.", False))
        status = "CONTINUITY_UNSTABLE"

    rec = (TemporalContinuityRecommendation("rec-1", "RECOMMEND_OPERATOR_REVIEW" if status in {"OPERATOR_REVIEW_REQUIRED", "CONTINUITY_UNSTABLE", "CONTINUITY_MIXED", "INSUFFICIENT_HISTORY"} else "RECOMMEND_PRESERVE_ALL_LINEAGES", "Deterministic temporal continuity recommendation.", True, False, False, False, False),)
    metrics = (TemporalContinuityMetric("m-score", "CONTINUITY_SCORE", score, "PRESERVE_ALL_LINEAGES", "PASS" if posture == "STABLE" else ("WARN" if posture in {"MIXED", "INSUFFICIENT_HISTORY"} else "BLOCKED" if posture == "UNSTABLE" else "NOT_COMPUTABLE")),)
    return build_temporal_continuity_index("index-1", refs, components, metrics, tuple(findings), rec, score, posture, status, "PRESERVE_ALL_LINEAGES", "FORECAST", None)


def write_temporal_continuity_index_contract_audit(base_dir: Path | str = ".") -> str:
    idx = derive_temporal_continuity_index([
        {"review_status": "CONSENSUS_PRESENT", "consensus_findings": ()},
        {"review_status": "CONSENSUS_PRESENT", "consensus_findings": ()},
    ], [{"source_type": "REPLAY_CONSENSUS_REVIEW", "source_id": "r1", "source_hash": "h1"}, {"source_type": "REPLAY_CONSENSUS_REVIEW", "source_id": "r2", "source_hash": "h2"}])
    report = validate_temporal_continuity_index(idx)
    payload = {"status": report.status, "index_hash": idx.index_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": idx.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/temporal_continuity_index_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)

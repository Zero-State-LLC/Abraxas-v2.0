from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from .models import ReplayArbitrationInputRef, ReplayLineageCandidate, ReplayArbitrationFinding, ReplayTemporalAuthorityScore, ReplayArbitrationRecommendation, ReplayTemporalArbitration
from .validator import validate_replay_temporal_arbitration

SCHEMA_VERSION = "ReplayTemporalArbitration.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _clamp(v: float) -> float:
    return min(1.0, max(0.0, v))


def canonical_replay_temporal_arbitration_json(arbitration: ReplayTemporalArbitration | Mapping[str, Any]) -> str:
    payload = asdict(arbitration) if isinstance(arbitration, ReplayTemporalArbitration) else dict(arbitration)
    payload.pop("arbitration_hash", None)
    return _canonical_json(payload)


def replay_temporal_arbitration_hash(arbitration: ReplayTemporalArbitration | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_replay_temporal_arbitration_json(arbitration))


def compute_temporal_authority_score(candidate: Mapping[str, Any]) -> ReplayTemporalAuthorityScore:
    c = dict(candidate)
    stability = 1.0 if c.get("stability_posture") == "STABLE" else (0.75 if c.get("stability_posture") == "MIXED" else (0.4 if c.get("stability_posture") == "UNSTABLE" else 0.2))
    completeness = 1.0 if c.get("ledger_ref_id") and c.get("replay_ref_ids") else 0.2
    rollback_integrity = _clamp(1.0 - (float(c.get("divergence_count", 0)) * 0.1))
    authority_lineage = 1.0 if c.get("lineage_preserved", True) else 0.0
    nondet_penalty = _clamp(float(c.get("nondeterminism_count", 0)) * 0.35)
    blocked_penalty = _clamp(float(c.get("blocked_count", 0)) * 0.25)
    score = _clamp(stability + completeness + rollback_integrity + authority_lineage - nondet_penalty - blocked_penalty)
    posture = "SECONDARY"
    if not c.get("ledger_ref_id"):
        posture = "INSUFFICIENT"
    elif c.get("nondeterminism_count", 0) > 0 or c.get("blocked_count", 0) > 0:
        posture = "CONFLICTED"
    return ReplayTemporalAuthorityScore(
        score_id=f"score-{c.get('candidate_id', 'na')}", candidate_id=str(c.get("candidate_id", "")), stability_component=round(stability, 10),
        lineage_completeness_component=round(completeness, 10), rollback_integrity_component=round(rollback_integrity, 10),
        authority_lineage_component=round(authority_lineage, 10), nondeterminism_penalty=round(nondet_penalty, 10),
        blocked_history_penalty=round(blocked_penalty, 10), authority_score=round(score, 10), authority_posture=posture, auto_select_allowed=False,
    )


def build_replay_temporal_arbitration(arbitration_id: str, input_refs: tuple[ReplayArbitrationInputRef, ...], lineage_candidates: tuple[ReplayLineageCandidate, ...], arbitration_findings: tuple[ReplayArbitrationFinding, ...], authority_scores: tuple[ReplayTemporalAuthorityScore, ...], recommendations: tuple[ReplayArbitrationRecommendation, ...], arbitration_status: str, arbitration_policy: str, created_by_lane: str, authority_ref: dict | None) -> ReplayTemporalArbitration:
    draft = ReplayTemporalArbitration(SCHEMA_VERSION, arbitration_id, input_refs, lineage_candidates, arbitration_findings, authority_scores, recommendations, arbitration_status, arbitration_policy, created_by_lane, authority_ref, False, False, False, False, "PENDING")
    return replace(draft, arbitration_hash=replay_temporal_arbitration_hash(draft))


def derive_replay_temporal_arbitration(lineage_candidates: Sequence[Mapping[str, Any]], input_refs: Sequence[Mapping[str, Any]] | None = None) -> ReplayTemporalArbitration:
    refs = tuple(ReplayArbitrationInputRef(str(r.get("source_type", "NOT_COMPUTABLE")), str(r.get("source_id", "")), str(r.get("source_hash", ""))) for r in (input_refs or []))
    candidates = tuple(ReplayLineageCandidate(str(c.get("candidate_id", f"c{i}")), str(c.get("lineage_id", f"l{i}")), str(c.get("ledger_ref_id", "")), tuple(c.get("diff_ref_ids", ())), tuple(c.get("replay_ref_ids", ())), str(c.get("stability_posture", "NOT_COMPUTABLE")), int(c.get("divergence_count", 0)), int(c.get("blocked_count", 0)), int(c.get("nondeterminism_count", 0)), bool(c.get("lineage_preserved", True))) for i, c in enumerate(lineage_candidates, start=1))
    findings: list[ReplayArbitrationFinding] = []
    if not candidates:
        status = "NOT_COMPUTABLE"
        findings.append(ReplayArbitrationFinding("f-missing", "NOT_COMPUTABLE", "NOT_COMPUTABLE", tuple(), "No lineage candidates supplied.", False))
    else:
        status = "NO_CONFLICT"
        fingerprints = {(c.stability_posture, c.divergence_count, c.blocked_count, c.nondeterminism_count) for c in candidates}
        if len(fingerprints) > 1:
            status = "CONFLICT_DETECTED"
            findings.append(ReplayArbitrationFinding("f-div", "DIVERGENT_LINEAGE", "WARN", tuple(c.candidate_id for c in candidates), "Lineages diverge across stability/divergence signals.", False))
        if any(c.nondeterminism_count > 0 for c in candidates):
            status = "CONFLICT_DETECTED"
            findings.append(ReplayArbitrationFinding("f-nondet", "NONDETERMINISM_CONFLICT", "BLOCKED", tuple(c.candidate_id for c in candidates if c.nondeterminism_count > 0), "Nondeterminism conflict present.", False))
        if any(c.blocked_count > 0 for c in candidates):
            if status == "NO_CONFLICT":
                status = "CONFLICT_DETECTED"
            findings.append(ReplayArbitrationFinding("f-blocked", "BLOCKED_HISTORY_PRESENT", "BLOCKED", tuple(c.candidate_id for c in candidates if c.blocked_count > 0), "Blocked history remains visible and preserved.", False))
        if any(c.divergence_count > 0 for c in candidates):
            findings.append(ReplayArbitrationFinding("f-rollback", "ROLLBACK_CONFLICT", "WARN", tuple(c.candidate_id for c in candidates if c.divergence_count > 0), "Rollback conflict indicators present.", False))
        if any(not c.ledger_ref_id for c in candidates):
            status = "AUTHORITY_INSUFFICIENT"
            findings.append(ReplayArbitrationFinding("f-auth", "AUTHORITY_MISMATCH", "NOT_COMPUTABLE", tuple(c.candidate_id for c in candidates if not c.ledger_ref_id), "Missing ledger refs for authority determination.", False))
        if status == "NO_CONFLICT":
            findings.append(ReplayArbitrationFinding("f-ok", "NO_CONFLICT", "INFO", tuple(c.candidate_id for c in candidates), "No effective temporal conflict; preserving all lineages.", False))

    scores = [compute_temporal_authority_score(asdict(c)) for c in candidates]
    if status in {"CONFLICT_DETECTED", "AUTHORITY_INSUFFICIENT", "NOT_COMPUTABLE"} and scores:
        top = max(s.authority_score for s in scores)
        top_count = sum(1 for s in scores if s.authority_score == top)
        for i, s in enumerate(scores):
            if s.nondeterminism_penalty > 0 or s.blocked_history_penalty > 0:
                scores[i] = replace(s, authority_posture="CONFLICTED")
            elif top_count > 1:
                scores[i] = replace(s, authority_posture="CONFLICTED")
            else:
                scores[i] = replace(s, authority_posture="SECONDARY")

    rec_type = "RECOMMEND_PRESERVE_ALL_LINEAGES" if status == "NO_CONFLICT" else ("RECOMMEND_OPERATOR_REVIEW" if status in {"CONFLICT_DETECTED", "AUTHORITY_INSUFFICIENT"} else "NOT_COMPUTABLE")
    recommendations = (ReplayArbitrationRecommendation("rec-1", rec_type, "Deterministic replay arbitration governance recommendation.", True, False, False),)
    return build_replay_temporal_arbitration("arb-1", refs, candidates, tuple(findings), tuple(scores), recommendations, status, "PRESERVE_DIVERGENCE", "FORECAST", None)


def write_replay_temporal_arbitration_contract_audit(base_dir: Path | str = ".") -> str:
    a = derive_replay_temporal_arbitration([{"candidate_id": "c1", "lineage_id": "l1", "ledger_ref_id": "ledger-1", "diff_ref_ids": ("d1",), "replay_ref_ids": ("r1",), "stability_posture": "STABLE", "divergence_count": 0, "blocked_count": 0, "nondeterminism_count": 0, "lineage_preserved": True}], [{"source_type": "REPLAY_LEDGER", "source_id": "ledger-1", "source_hash": "h1"}])
    report = validate_replay_temporal_arbitration(a)
    payload = {"status": report.status, "arbitration_hash": a.arbitration_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": a.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/replay_temporal_arbitration_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)

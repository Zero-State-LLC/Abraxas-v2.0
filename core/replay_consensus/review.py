from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from .models import *
from .validator import validate_replay_consensus_review

SCHEMA_VERSION = "ReplayConsensusReview.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_replay_consensus_review_json(review: ReplayConsensusReview | Mapping[str, Any]) -> str:
    payload = asdict(review) if isinstance(review, ReplayConsensusReview) else dict(review)
    payload.pop("review_hash", None)
    return _canonical_json(payload)


def replay_consensus_review_hash(review: ReplayConsensusReview | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_replay_consensus_review_json(review))


def compute_replay_consensus_posture(clusters: Sequence[Mapping[str, Any]], arbitration_count: int, lineage_count: int) -> ReplayConsensusPosture:
    if arbitration_count < 0 or lineage_count < 0:
        state = "NOT_COMPUTABLE"; cr = 0.0; xr = 0.0
    else:
        total = max(1, len(clusters))
        support = sum(1 for c in clusters if c.get("cluster_posture") == "CONSENSUS")
        conflicts = sum(1 for c in clusters if c.get("cluster_posture") == "CONFLICTED")
        cr = round(support / total, 10)
        xr = round(conflicts / total, 10)
        if arbitration_count < 2:
            state = "INSUFFICIENT_HISTORY"
        elif cr >= 0.80 and xr == 0.0:
            state = "STRONG_CONSENSUS"
        elif cr >= 0.50 and xr < 0.50:
            state = "PARTIAL_CONSENSUS"
        elif xr >= 0.50:
            state = "CONFLICTED"
        else:
            state = "NOT_COMPUTABLE"
    return ReplayConsensusPosture("posture-1", cr, xr, arbitration_count, lineage_count, state, False, False)


def build_replay_consensus_review(review_id: str, input_refs: tuple[ReplayConsensusInputRef, ...], consensus_clusters: tuple[ReplayConsensusCluster, ...], consensus_findings: tuple[ReplayConsensusFinding, ...], consensus_posture: ReplayConsensusPosture, recommendations: tuple[ReplayConsensusRecommendation, ...], review_status: str, review_policy: str, created_by_lane: str, authority_ref: dict | None) -> ReplayConsensusReview:
    draft = ReplayConsensusReview(SCHEMA_VERSION, review_id, input_refs, consensus_clusters, consensus_findings, consensus_posture, recommendations, review_status, review_policy, created_by_lane, authority_ref, False, False, False, False, False, "PENDING")
    return replace(draft, review_hash=replay_consensus_review_hash(draft))


def derive_replay_consensus_review(arbitrations: Sequence[Mapping[str, Any]], input_refs: Sequence[Mapping[str, Any]] | None = None) -> ReplayConsensusReview:
    refs = tuple(ReplayConsensusInputRef(str(r.get("source_type", "NOT_COMPUTABLE")), str(r.get("source_id", "")), str(r.get("source_hash", ""))) for r in (input_refs or []))
    if not arbitrations:
        posture = compute_replay_consensus_posture(tuple(), 0, 0)
        f = (ReplayConsensusFinding("f-missing", "NOT_COMPUTABLE", "NOT_COMPUTABLE", tuple(), tuple(), "No arbitrations supplied.", False),)
        rec = (ReplayConsensusRecommendation("rec-1", "NOT_COMPUTABLE", "Insufficient arbitration history for consensus review.", True, False, False, False),)
        return build_replay_consensus_review("review-1", refs, tuple(), f, posture, rec, "NOT_COMPUTABLE", "PRESERVE_ALL_LINEAGES", "FORECAST", None)

    clusters = []
    findings = []
    all_lineages = set()
    for i, a in enumerate(arbitrations, start=1):
        status = str(a.get("arbitration_status", "NOT_COMPUTABLE"))
        cands = tuple(a.get("lineage_candidates", ()))
        lineages = tuple(str(c.get("lineage_id", "")) for c in cands)
        all_lineages.update(lineages)
        posture = "CONSENSUS" if status == "NO_CONFLICT" else ("CONFLICTED" if status == "CONFLICT_DETECTED" else ("INSUFFICIENT" if status in {"AUTHORITY_INSUFFICIENT", "NOT_COMPUTABLE"} else "PARTIAL"))
        clusters.append(ReplayConsensusCluster(f"cl-{i}", tuple(str(c.get("candidate_id", "")) for c in cands), lineages, (str(a.get("arbitration_id", f"a{i}")),), posture, 1 if posture == "CONSENSUS" else 0, 1 if posture == "CONFLICTED" else 0, True, False))
        if any(f.get("finding_type") == "BLOCKED_HISTORY_PRESENT" for f in a.get("arbitration_findings", ())):
            findings.append(ReplayConsensusFinding(f"f-blocked-{i}", "BLOCKED_HISTORY_PRESENT", "BLOCKED", (f"cl-{i}",), lineages, "Blocked history remains visible in consensus review.", False))

    cluster_maps = [asdict(c) for c in clusters]
    posture = compute_replay_consensus_posture(cluster_maps, len(arbitrations), len(all_lineages))

    if len(arbitrations) == 1:
        review_status = "INSUFFICIENT_ARBITRATION_HISTORY"
        findings.append(ReplayConsensusFinding("f-insuf", "AUTHORITY_INSUFFICIENT", "WARN", tuple(c.cluster_id for c in clusters), tuple(all_lineages), "Single arbitration cannot establish consensus.", False))
    elif posture.consensus_state == "STRONG_CONSENSUS":
        review_status = "CONSENSUS_PRESENT"
        findings.append(ReplayConsensusFinding("f-consensus", "CONSENSUS_SIGNAL", "INFO", tuple(c.cluster_id for c in clusters), tuple(all_lineages), "Compatible arbitration packets indicate strong consensus.", False))
    elif posture.consensus_state == "PARTIAL_CONSENSUS":
        review_status = "PARTIAL_CONSENSUS"
        findings.append(ReplayConsensusFinding("f-partial", "PARTIAL_CONSENSUS_SIGNAL", "WARN", tuple(c.cluster_id for c in clusters), tuple(all_lineages), "Mixed arbitration packets indicate partial consensus.", False))
    elif posture.consensus_state == "CONFLICTED":
        review_status = "CONSENSUS_CONFLICT"
        findings.append(ReplayConsensusFinding("f-conflict", "CONFLICT_SIGNAL", "BLOCKED", tuple(c.cluster_id for c in clusters), tuple(all_lineages), "Conflicting arbitration packets require operator review.", False))
    else:
        review_status = "OPERATOR_REVIEW_REQUIRED"
        findings.append(ReplayConsensusFinding("f-nc", "NOT_COMPUTABLE", "NOT_COMPUTABLE", tuple(c.cluster_id for c in clusters), tuple(all_lineages), "Consensus state not computable from inputs.", False))

    rec_type = "RECOMMEND_PRESERVE_ALL_LINEAGES" if review_status == "CONSENSUS_PRESENT" else ("RECOMMEND_OPERATOR_REVIEW" if review_status in {"PARTIAL_CONSENSUS", "CONSENSUS_CONFLICT", "OPERATOR_REVIEW_REQUIRED", "INSUFFICIENT_ARBITRATION_HISTORY"} else "NOT_COMPUTABLE")
    rec = (ReplayConsensusRecommendation("rec-1", rec_type, "Deterministic consensus review recommendation.", True, False, False, False),)
    return build_replay_consensus_review("review-1", refs, tuple(clusters), tuple(findings), posture, rec, review_status, "PRESERVE_ALL_LINEAGES", "FORECAST", None)


def write_replay_consensus_review_contract_audit(base_dir: Path | str = ".") -> str:
    review = derive_replay_consensus_review([
        {"arbitration_id": "a1", "arbitration_status": "NO_CONFLICT", "lineage_candidates": ({"candidate_id": "c1", "lineage_id": "l1"},), "arbitration_findings": ()},
        {"arbitration_id": "a2", "arbitration_status": "NO_CONFLICT", "lineage_candidates": ({"candidate_id": "c2", "lineage_id": "l2"},), "arbitration_findings": ()},
    ], [{"source_type": "REPLAY_TEMPORAL_ARBITRATION", "source_id": "a1", "source_hash": "h1"}])
    report = validate_replay_consensus_review(review)
    payload = {"status": report.status, "review_hash": review.review_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": review.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/replay_consensus_review_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)

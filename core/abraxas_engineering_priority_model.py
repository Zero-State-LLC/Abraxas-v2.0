#!/usr/bin/env python3
"""Deterministic priority model for engineering candidates (v1) with governance stratification."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.abraxas_governance_decision_contract import resolve_governance_decision

def compute_scores(cand: Dict[str, Any], work_packet: Dict[str, Any] | None = None) -> Dict[str, float]:
    impact = float(cand.get("estimated_impact", 0.0))
    effort = float(cand.get("estimated_effort", 0.0))
    risk = float(cand.get("estimated_risk", 0.0))
    conf = float(cand.get("confidence", 0.0))

    # Governance stratification boost
    gov_boost = 0.0
    if work_packet:
        try:
            gov = resolve_governance_decision(cand, work_packet)
            if gov.get("automatic_under_engineering_approval"):
                gov_boost = 0.15  # Layer 0/1 executable engineering gets boost
            if gov.get("governance_layer", 0) >= 2:
                gov_boost = -0.25  # Layer 2/3 correctly penalized
        except Exception:
            pass

    impact_score = impact * 1.0
    centrality_score = 0.6 if "core/" in str(cand.get("affected_paths", [""])[0]) else 0.3
    gap_reduction_score = 0.8 if cand.get("candidate_class") in ("TEST", "GOVERNANCE", "HARDENING") else 0.4
    automation_multiplier = 0.5
    validation_readiness_score = 0.9 if cand.get("candidate_class") == "TEST" else 0.5
    evidence_confidence_score = conf

    effort_penalty = effort * 0.4
    risk_penalty = risk * 0.6
    governance_penalty = 0.05  # low for Layer 0/1

    final = (
        impact_score * 0.25 +
        centrality_score * 0.15 +
        gap_reduction_score * 0.15 +
        automation_multiplier * 0.05 +
        validation_readiness_score * 0.10 +
        evidence_confidence_score * 0.20 -
        effort_penalty * 0.05 -
        risk_penalty * 0.03 -
        governance_penalty * 0.02 +
        gov_boost
    )
    final = max(0.0, min(1.0, final))

    return {
        "impact_score": round(impact_score, 4),
        "centrality_score": round(centrality_score, 4),
        "gap_reduction_score": round(gap_reduction_score, 4),
        "automation_multiplier": round(automation_multiplier, 4),
        "validation_readiness_score": round(validation_readiness_score, 4),
        "evidence_confidence_score": round(evidence_confidence_score, 4),
        "effort_penalty": round(effort_penalty, 4),
        "risk_penalty": round(risk_penalty, 4),
        "governance_penalty": round(governance_penalty, 4),
        "governance_boost": round(gov_boost, 4),
        "final_priority_score": round(final, 4),
    }

def rank_candidates(cands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rank candidates using compute_scores and governance stratification.
    Returns list sorted by final_priority_score descending.
    """
    scored = []
    for c in cands:
        pkt = {"affected_paths": c.get("affected_paths", [])}
        scores = compute_scores(c, pkt)
        c = dict(c)  # copy
        c["priority"] = scores
        c["final_priority_score"] = scores["final_priority_score"]
        scored.append(c)
    scored.sort(key=lambda x: x.get("final_priority_score", 0.0), reverse=True)
    return scored

def main():
    cand = {"candidate_id": "00d0fb441ea388c2", "title": "Add tests for core/scoring/models.py", "estimated_impact": 0.7, "estimated_effort": 0.2, "estimated_risk": 0.1, "confidence": 0.85, "affected_paths": ["core/scoring/models.py"], "candidate_class": "HARDENING"}
    pkt = {"affected_paths": ["core/scoring/models.py"]}
    scores = compute_scores(cand, pkt)
    print(json.dumps(scores, indent=2))

if __name__ == "__main__":
    main()
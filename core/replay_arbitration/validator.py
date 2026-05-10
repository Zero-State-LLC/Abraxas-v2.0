from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import *


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_replay_temporal_arbitration(arbitration: ReplayTemporalArbitration | Mapping[str, Any]) -> ReplayArbitrationValidationReport:
    a = arbitration if isinstance(arbitration, ReplayTemporalArbitration) else ReplayTemporalArbitration(**dict(arbitration))
    findings = []
    status = "PASS"
    if a.history_rewrite_allowed or a.ledger_mutation_allowed or a.live_execution_allowed or a.routing_change_allowed:
        findings.append(ReplayArbitrationValidationFinding("FLAGS_FORBIDDEN", "error", "rewrite/mutation/execution/routing must be false.")); status = "BLOCKED"
    if any(not c.lineage_preserved for c in a.lineage_candidates):
        findings.append(ReplayArbitrationValidationFinding("LINEAGE_PRESERVE_REQUIRED", "error", "lineage_preserved must be true.")); status = "BLOCKED"
    if any(f.normalization_allowed for f in a.arbitration_findings):
        findings.append(ReplayArbitrationValidationFinding("NORMALIZATION_FORBIDDEN", "error", "normalization_allowed must be false.")); status = "BLOCKED"
    if any(s.auto_select_allowed for s in a.authority_scores):
        findings.append(ReplayArbitrationValidationFinding("AUTO_SELECT_FORBIDDEN", "error", "auto_select_allowed must be false.")); status = "BLOCKED"
    if any(r.history_rewrite_allowed or r.ledger_mutation_allowed for r in a.recommendations):
        findings.append(ReplayArbitrationValidationFinding("RECOMMENDATION_MUTATION_FORBIDDEN", "error", "recommendations cannot permit rewrite/mutation.")); status = "BLOCKED"
    if a.arbitration_status == "CONFLICT_DETECTED" and not any(f.severity != "INFO" for f in a.arbitration_findings):
        findings.append(ReplayArbitrationValidationFinding("CONFLICT_REQUIRES_NON_INFO", "error", "CONFLICT_DETECTED requires non-INFO finding.")); status = "BLOCKED"
    if a.arbitration_status == "NO_CONFLICT" and any(f.severity in {"BLOCKED", "NOT_COMPUTABLE"} for f in a.arbitration_findings):
        findings.append(ReplayArbitrationValidationFinding("NO_CONFLICT_INVALID", "error", "NO_CONFLICT cannot include BLOCKED/NOT_COMPUTABLE findings.")); status = "BLOCKED"
    if a.arbitration_status == "OPERATOR_REVIEW_REQUIRED" and not any(r.operator_review_required for r in a.recommendations):
        findings.append(ReplayArbitrationValidationFinding("REVIEW_REQUIRED_MISSING", "error", "OPERATOR_REVIEW_REQUIRED needs operator_review_required recommendation.")); status = "BLOCKED"
    for c in a.lineage_candidates:
        for s in a.authority_scores:
            if s.candidate_id == c.candidate_id and s.authority_posture == "PRIMARY" and (c.nondeterminism_count > 0 or c.blocked_count > 0):
                findings.append(ReplayArbitrationValidationFinding("PRIMARY_FORBIDDEN_ON_BLOCKED_OR_NONDET", "error", "PRIMARY forbidden for blocked or nondeterministic candidates.")); status = "BLOCKED"
    if a.created_by_lane == "SHADOW" and (a.arbitration_status == "NO_CONFLICT" or any(s.authority_posture == "PRIMARY" for s in a.authority_scores)):
        findings.append(ReplayArbitrationValidationFinding("SHADOW_AUTHORITY_BLOCKED", "error", "SHADOW cannot mark NO_CONFLICT or PRIMARY authority.")); status = "BLOCKED"
    if a.created_by_lane == "FORECAST" and any(s.authority_posture == "PRIMARY" for s in a.authority_scores):
        findings.append(ReplayArbitrationValidationFinding("FORECAST_PRIMARY_BLOCKED", "error", "FORECAST cannot mark PRIMARY authority.")); status = "BLOCKED"
    if a.created_by_lane == "PROJECTION" and a.authority_ref is not None:
        findings.append(ReplayArbitrationValidationFinding("PROJECTION_AUTH_BLOCKED", "error", "PROJECTION cannot create authority.")); status = "BLOCKED"
    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "arbitration_id": a.arbitration_id}))
    return ReplayArbitrationValidationReport(status, tuple(findings), receipt_hash)

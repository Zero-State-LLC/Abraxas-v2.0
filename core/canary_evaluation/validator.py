from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import CanaryEvaluationInputRef, CanaryEvaluationMetric, CanaryEvaluationDecision, CanaryEvaluationRecommendation, CanaryEvaluationReviewSummary, AuthorityRef, CanaryEvaluation, CanaryEvaluationValidationFinding, CanaryEvaluationValidationReport


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _to_eval(x: CanaryEvaluation | Mapping[str, Any]) -> CanaryEvaluation:
    if isinstance(x, CanaryEvaluation):
        return x
    d = dict(x)
    return CanaryEvaluation(
        d["schema_version"], d["evaluation_id"], d["activation_id"], d["activation_hash"], d["accumulation_id"], d["accumulation_hash"],
        tuple(CanaryEvaluationInputRef(**r) for r in d["input_refs"]), tuple(CanaryEvaluationMetric(**m) for m in d["metrics"]),
        CanaryEvaluationDecision(**d["decision"]), tuple(CanaryEvaluationRecommendation(**r) for r in d["recommendations"]),
        CanaryEvaluationReviewSummary(**d["review_summary"]), d["evaluation_status"], d["created_by_lane"], AuthorityRef(**d["authority_ref"]) if d.get("authority_ref") else None,
        d["promotion_allowed"], d["rollback_allowed"], d["mutation_allowed"], d["evaluation_hash"]
    )


def validate_canary_evaluation(evaluation: CanaryEvaluation | Mapping[str, Any]) -> CanaryEvaluationValidationReport:
    e = _to_eval(evaluation)
    findings=[]
    status="PASS"
    if e.schema_version != "CanaryEvaluation.v1":
        findings.append(CanaryEvaluationValidationFinding("SCHEMA_VERSION_INVALID","not_computable","schema_version must be CanaryEvaluation.v1."))
        status="NOT_COMPUTABLE"
    if not e.activation_id or not e.activation_hash or not e.accumulation_id or not e.accumulation_hash:
        findings.append(CanaryEvaluationValidationFinding("INPUT_REFS_REQUIRED","not_computable","Missing activation/accumulation refs."))
        status="NOT_COMPUTABLE" if status!="BLOCKED" else status
    if e.promotion_allowed:
        findings.append(CanaryEvaluationValidationFinding("PROMOTION_FORBIDDEN","error","promotion_allowed must be false."))
        status="BLOCKED"
    if e.rollback_allowed:
        findings.append(CanaryEvaluationValidationFinding("ROLLBACK_FORBIDDEN","error","rollback_allowed must be false."))
        status="BLOCKED"
    if e.mutation_allowed:
        findings.append(CanaryEvaluationValidationFinding("MUTATION_FORBIDDEN","error","mutation_allowed must be false."))
        status="BLOCKED"
    rs=e.review_summary
    if not rs.operator_review_required:
        findings.append(CanaryEvaluationValidationFinding("OP_REVIEW_REQUIRED","error","operator_review_required must be true."))
        status="BLOCKED"
    if rs.promotion_proposal_allowed:
        findings.append(CanaryEvaluationValidationFinding("PROMO_PROPOSAL_ALLOWED_FORBIDDEN","error","promotion_proposal_allowed must be false."))
        status="BLOCKED"
    if rs.rollback_proposal_allowed:
        findings.append(CanaryEvaluationValidationFinding("ROLLBACK_PROPOSAL_ALLOWED_FORBIDDEN","error","rollback_proposal_allowed must be false."))
        status="BLOCKED"
    if rs.execution_allowed:
        findings.append(CanaryEvaluationValidationFinding("EXECUTION_FORBIDDEN","error","execution_allowed must be false."))
        status="BLOCKED"
    if e.evaluation_status=="PASSED" and (e.decision.decision!="PASS" or (not e.metrics and not e.input_refs)):
        findings.append(CanaryEvaluationValidationFinding("PASSED_CONDITIONS_INVALID","error","PASSED requires decision PASS and metric/input refs."))
        status="BLOCKED"
    if e.evaluation_status=="FAILED" and e.decision.decision not in {"FAIL","GUARDRAIL_BREACH"}:
        findings.append(CanaryEvaluationValidationFinding("FAILED_DECISION_INVALID","error","FAILED requires FAIL or GUARDRAIL_BREACH decision."))
        status="BLOCKED"
    if e.evaluation_status=="REVIEW_REQUIRED" and not e.review_summary.operator_review_required:
        findings.append(CanaryEvaluationValidationFinding("REVIEW_SUMMARY_REQUIRED","error","REVIEW_REQUIRED requires operator review summary."))
        status="BLOCKED"
    if e.created_by_lane=="SHADOW" and e.evaluation_status in {"PASSED","FAILED"}:
        findings.append(CanaryEvaluationValidationFinding("SHADOW_FINALIZE_BLOCKED","error","SHADOW may draft but cannot mark PASSED or FAILED."))
        status="BLOCKED"
    if e.created_by_lane=="PROJECTION" and e.authority_ref is not None:
        findings.append(CanaryEvaluationValidationFinding("PROJECTION_AUTHORITY_BLOCKED","error","PROJECTION cannot create evaluation authority."))
        status="BLOCKED"
    if e.created_by_lane=="CANON" and e.evaluation_status in {"EVALUATION_READY","PASSED","FAILED","REVIEW_REQUIRED"}:
        findings.append(CanaryEvaluationValidationFinding("CANON_FINALIZE_BLOCKED","error","CANON may define schema/contracts only."))
        status="BLOCKED"
    receipt_hash=_sha256_text(_canonical_json({"status":status,"findings":[asdict(f) for f in findings],"evaluation_id":e.evaluation_id}))
    return CanaryEvaluationValidationReport(status, tuple(findings), receipt_hash)

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import CanaryEvaluationInputRef, CanaryEvaluationMetric, CanaryEvaluationDecision, CanaryEvaluationRecommendation, CanaryEvaluationReviewSummary, AuthorityRef, CanaryEvaluation

SCHEMA_VERSION = "CanaryEvaluation.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_canary_evaluation_json(evaluation: CanaryEvaluation | Mapping[str, Any]) -> str:
    payload = asdict(evaluation) if isinstance(evaluation, CanaryEvaluation) else dict(evaluation)
    payload.pop("evaluation_hash", None)
    return _canonical_json(payload)


def canary_evaluation_hash(evaluation: CanaryEvaluation | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_canary_evaluation_json(evaluation))


def build_canary_evaluation(
    evaluation_id: str,
    activation_id: str,
    activation_hash: str,
    accumulation_id: str,
    accumulation_hash: str,
    input_refs: tuple[CanaryEvaluationInputRef, ...],
    metrics: tuple[CanaryEvaluationMetric, ...],
    decision: CanaryEvaluationDecision,
    recommendations: tuple[CanaryEvaluationRecommendation, ...],
    review_summary: CanaryEvaluationReviewSummary,
    evaluation_status: str,
    created_by_lane: str,
    authority_ref: AuthorityRef | None,
) -> CanaryEvaluation:
    draft = CanaryEvaluation(SCHEMA_VERSION, evaluation_id, activation_id, activation_hash, accumulation_id, accumulation_hash, input_refs, metrics, decision, recommendations, review_summary, evaluation_status, created_by_lane, authority_ref, False, False, False, "PENDING")
    return replace(draft, evaluation_hash=canary_evaluation_hash(draft))


def derive_canary_evaluation_from_accumulation(accumulation: Mapping[str, Any], activation: Mapping[str, Any] | None = None) -> CanaryEvaluation:
    acc = dict(accumulation)
    status = str(acc.get("accumulation_status", "NOT_COMPUTABLE"))
    readiness = dict(acc.get("readiness_summary", {}))
    guardrails = list(acc.get("guardrail_observations", []))

    decision = "NOT_COMPUTABLE"
    eval_status = "NOT_COMPUTABLE"
    recs: list[CanaryEvaluationRecommendation] = [CanaryEvaluationRecommendation("NOT_COMPUTABLE", "Missing refs or invalid accumulation state.")]
    metrics: list[CanaryEvaluationMetric] = []
    if acc.get("activation_id") and acc.get("activation_hash") and acc.get("accumulation_id") and acc.get("accumulation_hash"):
        if status == "EVIDENCE_READY" and bool(readiness.get("guardrails_clear", False)):
            decision, eval_status = "PASS", "PASSED"
            recs = [CanaryEvaluationRecommendation("RECOMMEND_OPERATOR_REVIEW", "Operator review remains required."), CanaryEvaluationRecommendation("RECOMMEND_PROMOTION_PROPOSAL", "Promotion proposal may be prepared, not executed.")]
            metrics.append(CanaryEvaluationMetric("evidence_ratio", "EVIDENCE_COUNT", float(readiness.get("observed_evidence_count", 0)), {"min": float(readiness.get("minimum_evidence_count", 0))}, "GTE_MIN", "PASS"))
        elif status == "GUARDRAIL_BREACH":
            decision, eval_status = "GUARDRAIL_BREACH", "FAILED"
            recs = [CanaryEvaluationRecommendation("RECOMMEND_OPERATOR_REVIEW", "Guardrail breach requires operator review."), CanaryEvaluationRecommendation("RECOMMEND_ROLLBACK_PROPOSAL", "Rollback proposal may be prepared, not executed.")]
            breached = any(bool(g.get("breach_detected")) for g in guardrails)
            metrics.append(CanaryEvaluationMetric("guardrail_breach", "GUARDRAIL_STATUS", 1.0 if breached else 0.0, {"expected": 0.0}, "EXPECT_ZERO", "FAIL" if breached else "WARN"))
        elif status == "INSUFFICIENT_EVIDENCE":
            decision, eval_status = "INSUFFICIENT_EVIDENCE", "REVIEW_REQUIRED"
            recs = [CanaryEvaluationRecommendation("RECOMMEND_HOLD", "Insufficient evidence; continue observing."), CanaryEvaluationRecommendation("RECOMMEND_OPERATOR_REVIEW", "Operator review required before next step.")]
            metrics.append(CanaryEvaluationMetric("evidence_ratio", "EVIDENCE_COUNT", float(readiness.get("observed_evidence_count", 0)), {"min": float(readiness.get("minimum_evidence_count", 0))}, "GTE_MIN", "WARN"))

    review = CanaryEvaluationReviewSummary("review-summary-1", True, False, False, False, "Evaluation is advisory-only and requires operator review.")
    return build_canary_evaluation(
        evaluation_id=f"canary-eval:{acc.get('accumulation_id', 'unknown')}",
        activation_id=str(acc.get("activation_id", "")), activation_hash=str(acc.get("activation_hash", "")), accumulation_id=str(acc.get("accumulation_id", "")), accumulation_hash=str(acc.get("accumulation_hash", "")),
        input_refs=(CanaryEvaluationInputRef("CANARY_EVIDENCE_ACCUMULATION", str(acc.get("accumulation_id", "")), str(acc.get("accumulation_hash", ""))),),
        metrics=tuple(metrics), decision=CanaryEvaluationDecision(decision, f"Derived from accumulation status={status}."), recommendations=tuple(recs), review_summary=review,
        evaluation_status=eval_status, created_by_lane="FORECAST", authority_ref=None,
    )


def write_canary_evaluation_contract_audit(base_dir: Path | str = ".") -> str:
    accumulation = {
        "accumulation_id": "acc-1", "accumulation_hash": "acc-h1", "activation_id": "act-1", "activation_hash": "act-h1",
        "accumulation_status": "EVIDENCE_READY", "readiness_summary": {"minimum_evidence_count": 3, "observed_evidence_count": 3, "guardrails_clear": True}, "guardrail_observations": [],
    }
    evaluation = derive_canary_evaluation_from_accumulation(accumulation)
    from .validator import validate_canary_evaluation
    report = validate_canary_evaluation(evaluation)
    payload = {"status": report.status, "evaluation_hash": evaluation.evaluation_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": evaluation.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/canary_evaluation_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)

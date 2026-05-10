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


def _to_activation(a: CanaryActivation | Mapping[str, Any]) -> CanaryActivation:
    if isinstance(a, CanaryActivation):
        return a
    d = dict(a)
    return CanaryActivation(
        d["schema_version"], d["activation_id"], d["proposal_id"], d["proposal_hash"], CanaryScope(**d["scope"]), CanaryDurationPolicy(**d["duration_policy"]), tuple(CanaryGuardrail(**x) for x in d["guardrails"]), CanaryEvidenceRequirement(**d["evidence_requirements"]), CanaryRollbackLink(**d["rollback_link"]), CanaryOperatorApprovalRef(**d["operator_approval_ref"]), d["activation_status"], d["created_by_lane"], AuthorityRef(**d["authority_ref"]) if d.get("authority_ref") else None, d["global_activation_allowed"], d["mutation_limited_to_scope"], d["auto_promote"], d["auto_rollback"], d["activation_hash"]
    )


def validate_canary_activation(activation: CanaryActivation | Mapping[str, Any]) -> CanaryValidationReport:
    a = _to_activation(activation)
    findings: list[CanaryValidationFinding] = []
    status = "PASS"
    if a.schema_version != "CanaryActivation.v1":
        findings.append(CanaryValidationFinding("SCHEMA_VERSION_INVALID", "not_computable", "schema_version must be CanaryActivation.v1.")); status = "NOT_COMPUTABLE"
    if a.global_activation_allowed:
        findings.append(CanaryValidationFinding("GLOBAL_ACTIVATION_FORBIDDEN", "error", "global_activation_allowed must be false.")); status = "BLOCKED"
    if not a.mutation_limited_to_scope:
        findings.append(CanaryValidationFinding("SCOPE_LIMIT_REQUIRED", "error", "mutation_limited_to_scope must be true.")); status = "BLOCKED"
    if a.auto_promote:
        findings.append(CanaryValidationFinding("AUTO_PROMOTE_FORBIDDEN", "error", "auto_promote must be false.")); status = "BLOCKED"
    if a.auto_rollback:
        findings.append(CanaryValidationFinding("AUTO_ROLLBACK_FORBIDDEN", "error", "auto_rollback must be false.")); status = "BLOCKED"
    if a.activation_status == "READY_FOR_CANARY" and (not a.proposal_id or not a.proposal_hash or not a.guardrails or not a.rollback_link.rollback_plan_id or not a.operator_approval_ref.review_queue_ref):
        findings.append(CanaryValidationFinding("READY_REFS_REQUIRED", "not_computable", "READY_FOR_CANARY requires proposal refs, guardrails, rollback link, and operator approval ref.")); status = "NOT_COMPUTABLE" if status != "BLOCKED" else status
    if a.activation_status == "CANARY_ACTIVE":
        if not a.operator_approval_ref.operator_receipt_ref:
            findings.append(CanaryValidationFinding("ACTIVE_RECEIPT_REQUIRED", "error", "CANARY_ACTIVE requires operator receipt ref.")); status = "BLOCKED"
        if not a.rollback_link.rollback_available:
            findings.append(CanaryValidationFinding("ACTIVE_ROLLBACK_REQUIRED", "error", "CANARY_ACTIVE requires rollback_available=true.")); status = "BLOCKED"
        if a.scope.scope_type == "GLOBAL":
            findings.append(CanaryValidationFinding("ACTIVE_GLOBAL_SCOPE_FORBIDDEN", "error", "CANARY_ACTIVE must not allow GLOBAL scope.")); status = "BLOCKED"
    if a.activation_status == "CANARY_COMPLETE" and a.evidence_requirements.satisfied_evidence_count < a.evidence_requirements.minimum_evidence_count:
        findings.append(CanaryValidationFinding("EVIDENCE_INSUFFICIENT", "not_computable", "CANARY_COMPLETE requires minimum evidence count.")); status = "NOT_COMPUTABLE" if status != "BLOCKED" else status
    if a.activation_status == "CANARY_FAILED" and not any(g.breach_action in {"HALT_AND_REVIEW", "ROLLBACK_REQUIRED"} for g in a.guardrails):
        findings.append(CanaryValidationFinding("BREACH_REASON_REQUIRED", "not_computable", "CANARY_FAILED requires guardrail breach reason/action.")); status = "NOT_COMPUTABLE" if status != "BLOCKED" else status
    if a.activation_status == "ROLLED_BACK" and (not a.rollback_link.rollback_available or not a.rollback_link.rollback_artifacts):
        findings.append(CanaryValidationFinding("ROLLBACK_LINK_REQUIRED", "not_computable", "ROLLED_BACK requires rollback availability and artifacts.")); status = "NOT_COMPUTABLE" if status != "BLOCKED" else status
    if a.activation_status == "VOID" and not any(f.code == "VOID_REASON" for f in findings):
        findings.append(CanaryValidationFinding("VOID_REASON", "not_computable", "VOID requires reason/finding.")); status = "NOT_COMPUTABLE" if status != "BLOCKED" else status
    if a.created_by_lane == "SHADOW" and a.activation_status in {"READY_FOR_CANARY", "CANARY_ACTIVE"}:
        findings.append(CanaryValidationFinding("SHADOW_FINALIZE_BLOCKED", "error", "SHADOW may draft but cannot mark READY_FOR_CANARY or CANARY_ACTIVE.")); status = "BLOCKED"
    if a.created_by_lane == "FORECAST" and a.activation_status == "CANARY_ACTIVE":
        findings.append(CanaryValidationFinding("FORECAST_ACTIVATION_BLOCKED", "error", "FORECAST may submit READY_FOR_CANARY but cannot activate.")); status = "BLOCKED"
    if a.created_by_lane == "OPERATOR" and a.activation_status == "CANARY_ACTIVE" and a.authority_ref is None:
        findings.append(CanaryValidationFinding("OPERATOR_AUTHORITY_REQUIRED", "not_computable", "OPERATOR activation requires receipt authority.")); status = "NOT_COMPUTABLE" if status != "BLOCKED" else status
    if a.created_by_lane == "PROJECTION" and a.authority_ref is not None:
        findings.append(CanaryValidationFinding("PROJECTION_AUTHORITY_BLOCKED", "error", "PROJECTION cannot create canary authority.")); status = "BLOCKED"
    if a.created_by_lane == "CANON" and a.activation_status in {"READY_FOR_CANARY", "CANARY_ACTIVE", "CANARY_COMPLETE", "CANARY_FAILED", "ROLLED_BACK"}:
        findings.append(CanaryValidationFinding("CANON_FINALIZE_BLOCKED", "error", "CANON may define schema/contracts only.")); status = "BLOCKED"

    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "activation_id": a.activation_id}))
    return CanaryValidationReport(status, tuple(findings), receipt_hash)

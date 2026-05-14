from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import CanaryObservationWindow, CanaryEvidenceRef, CanaryGuardrailObservation, CanaryReadinessSummary, AuthorityRef, CanaryEvidenceAccumulation, CanaryEvidenceValidationFinding, CanaryEvidenceValidationReport


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _to_accumulation(x: CanaryEvidenceAccumulation | Mapping[str, Any]) -> CanaryEvidenceAccumulation:
    if isinstance(x, CanaryEvidenceAccumulation):
        return x
    d = dict(x)
    return CanaryEvidenceAccumulation(
        d["schema_version"], d["accumulation_id"], d["activation_id"], d["activation_hash"], tuple(CanaryObservationWindow(**w) for w in d["observation_windows"]), tuple(CanaryEvidenceRef(**e) for e in d["evidence_refs"]), tuple(CanaryGuardrailObservation(**g) for g in d["guardrail_observations"]), CanaryReadinessSummary(**d["readiness_summary"]), d["accumulation_status"], d["created_by_lane"], AuthorityRef(**d["authority_ref"]) if d.get("authority_ref") else None, d["promotion_allowed"], d["rollback_allowed"], d["mutation_allowed"], d["accumulation_hash"]
    )


def validate_canary_evidence_accumulation(accumulation: CanaryEvidenceAccumulation | Mapping[str, Any]) -> CanaryEvidenceValidationReport:
    a = _to_accumulation(accumulation)
    findings: list[CanaryEvidenceValidationFinding] = []
    status = "PASS"
    if a.schema_version != "CanaryEvidenceAccumulation.v1":
        findings.append(CanaryEvidenceValidationFinding("SCHEMA_VERSION_INVALID", "not_computable", "schema_version must be CanaryEvidenceAccumulation.v1."))
        status = "NOT_COMPUTABLE"
    if not a.activation_id or not a.activation_hash:
        findings.append(CanaryEvidenceValidationFinding("ACTIVATION_REF_REQUIRED", "not_computable", "activation_id and activation_hash are required."))
        status = "NOT_COMPUTABLE" if status != "BLOCKED" else status
    if a.promotion_allowed:
        findings.append(CanaryEvidenceValidationFinding("PROMOTION_FORBIDDEN", "error", "promotion_allowed must be false."))
        status = "BLOCKED"
    if a.rollback_allowed:
        findings.append(CanaryEvidenceValidationFinding("ROLLBACK_FORBIDDEN", "error", "rollback_allowed must be false."))
        status = "BLOCKED"
    if a.mutation_allowed:
        findings.append(CanaryEvidenceValidationFinding("MUTATION_FORBIDDEN", "error", "mutation_allowed must be false."))
        status = "BLOCKED"
    if a.readiness_summary.ready_for_promotion:
        findings.append(CanaryEvidenceValidationFinding("READY_FOR_PROMOTION_FORBIDDEN", "error", "readiness_summary.ready_for_promotion must be false."))
        status = "BLOCKED"
    if a.readiness_summary.ready_for_rollback:
        findings.append(CanaryEvidenceValidationFinding("READY_FOR_ROLLBACK_FORBIDDEN", "error", "readiness_summary.ready_for_rollback must be false."))
        status = "BLOCKED"
    if a.accumulation_status == "OBSERVING" and not a.observation_windows:
        findings.append(CanaryEvidenceValidationFinding("OBSERVATION_WINDOW_REQUIRED", "not_computable", "OBSERVING requires at least one observation window."))
        status = "NOT_COMPUTABLE" if status != "BLOCKED" else status
    if a.accumulation_status == "EVIDENCE_READY":
        if a.readiness_summary.observed_evidence_count < a.readiness_summary.minimum_evidence_count or not a.readiness_summary.guardrails_clear:
            findings.append(CanaryEvidenceValidationFinding("EVIDENCE_READY_CONDITIONS_FAILED", "error", "EVIDENCE_READY requires minimum evidence and clear guardrails."))
            status = "BLOCKED"
        if not a.readiness_summary.ready_for_operator_review:
            findings.append(CanaryEvidenceValidationFinding("OPERATOR_REVIEW_NOT_READY", "error", "EVIDENCE_READY requires ready_for_operator_review=true."))
            status = "BLOCKED"
    if a.accumulation_status == "GUARDRAIL_BREACH" and not any(g.breach_detected and g.breach_reason for g in a.guardrail_observations):
        findings.append(CanaryEvidenceValidationFinding("BREACH_REASON_REQUIRED", "not_computable", "GUARDRAIL_BREACH requires breach_detected=true with breach_reason."))
        status = "NOT_COMPUTABLE" if status != "BLOCKED" else status
    if a.accumulation_status == "INSUFFICIENT_EVIDENCE" and not (a.readiness_summary.observed_evidence_count < a.readiness_summary.minimum_evidence_count):
        findings.append(CanaryEvidenceValidationFinding("INSUFFICIENT_EVIDENCE_MISMATCH", "error", "INSUFFICIENT_EVIDENCE requires observed_evidence_count < minimum_evidence_count."))
        status = "BLOCKED"
    if a.accumulation_status == "VOID":
        findings.append(CanaryEvidenceValidationFinding("VOID_REASON_REQUIRED", "not_computable", "VOID requires reason/finding."))
        status = "NOT_COMPUTABLE" if status != "BLOCKED" else status
    if a.created_by_lane == "SHADOW" and a.accumulation_status == "EVIDENCE_READY":
        findings.append(CanaryEvidenceValidationFinding("SHADOW_READY_BLOCKED", "error", "SHADOW may draft observations but cannot mark EVIDENCE_READY."))
        status = "BLOCKED"
    if a.created_by_lane == "PROJECTION" and a.authority_ref is not None:
        findings.append(CanaryEvidenceValidationFinding("PROJECTION_AUTHORITY_BLOCKED", "error", "PROJECTION cannot create canary evidence authority."))
        status = "BLOCKED"
    if a.created_by_lane == "CANON" and a.accumulation_status in {"OBSERVING", "EVIDENCE_READY", "INSUFFICIENT_EVIDENCE", "GUARDRAIL_BREACH"}:
        findings.append(CanaryEvidenceValidationFinding("CANON_FINALIZE_BLOCKED", "error", "CANON may define schema/contracts only."))
        status = "BLOCKED"

    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "accumulation_id": a.accumulation_id}))
    return CanaryEvidenceValidationReport(status, tuple(findings), receipt_hash)

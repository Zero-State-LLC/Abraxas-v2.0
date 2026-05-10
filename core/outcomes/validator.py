from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import AuthorityRef, BindingStatus, OutcomeBinding, OutcomeBindingValidationFinding, OutcomeBindingValidationReport, OutcomeCriterion, ResolutionSourceRef, ResolutionWindow, VerdictRule

ALLOWED_SOURCE_TYPES = {"OFFICIAL_API", "PUBLIC_WEB", "MANUAL_RECEIPT", "MARKET_SOURCE", "SPORTS_DATA_SOURCE", "REPO_FIXTURE", "NOT_COMPUTABLE"}
ALLOWED_RULE_TYPES = {"BOOLEAN_EVENT", "THRESHOLD_NUMERIC", "CATEGORICAL_MATCH", "RANGE_INCLUSION", "MANUAL_REVIEW_REQUIRED", "NOT_COMPUTABLE"}


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _to_binding(binding: OutcomeBinding | Mapping[str, Any]) -> OutcomeBinding:
    if isinstance(binding, OutcomeBinding):
        return binding
    data = dict(binding)
    return OutcomeBinding(
        schema_version=data["schema_version"],
        binding_id=data["binding_id"],
        forecast_id=data["forecast_id"],
        forecast_hash=data["forecast_hash"],
        criteria=tuple(OutcomeCriterion(**x) for x in data["criteria"]),
        resolution_sources=tuple(ResolutionSourceRef(**x) for x in data["resolution_sources"]),
        resolution_window=ResolutionWindow(**data["resolution_window"]),
        verdict_rule=VerdictRule(**data["verdict_rule"]),
        binding_status=BindingStatus(data["binding_status"]),
        created_by_lane=data["created_by_lane"],
        authority_ref=AuthorityRef(**data["authority_ref"]) if data.get("authority_ref") else None,
        void_reason=data.get("void_reason"),
        binding_hash=data["binding_hash"],
    )


def validate_outcome_binding(binding: OutcomeBinding | Mapping[str, Any]) -> OutcomeBindingValidationReport:
    obj = _to_binding(binding)
    findings: list[OutcomeBindingValidationFinding] = []
    status = "PASS"

    if obj.schema_version != "OutcomeBinding.v1":
        findings.append(OutcomeBindingValidationFinding("SCHEMA_VERSION_INVALID", "not_computable", "schema_version must be OutcomeBinding.v1."))
        status = "NOT_COMPUTABLE"
    if not obj.forecast_id or not obj.forecast_hash:
        findings.append(OutcomeBindingValidationFinding("FORECAST_REF_MISSING", "not_computable", "forecast_id and forecast_hash are required."))
        status = "NOT_COMPUTABLE"

    if obj.binding_status == BindingStatus.DRAFT:
        findings.append(OutcomeBindingValidationFinding("DRAFT_NOT_SCORE_READY", "warning", "DRAFT binding is not score-ready."))
        if status == "PASS":
            status = "WARN"

    if obj.binding_status == BindingStatus.BOUND:
        if not obj.criteria:
            findings.append(OutcomeBindingValidationFinding("BOUND_CRITERIA_REQUIRED", "error", "BOUND requires at least one criterion."))
            status = "BLOCKED"
        if not obj.resolution_sources:
            findings.append(OutcomeBindingValidationFinding("BOUND_RESOLUTION_SOURCE_REQUIRED", "error", "BOUND requires at least one resolution source."))
            status = "BLOCKED"
        if obj.authority_ref is None:
            findings.append(OutcomeBindingValidationFinding("BOUND_AUTHORITY_REQUIRED", "not_computable", "BOUND requires authority_ref."))
            if status != "BLOCKED":
                status = "NOT_COMPUTABLE"

    if obj.binding_status == BindingStatus.RESOLVED and obj.verdict_rule.rule_type == "NOT_COMPUTABLE":
        findings.append(OutcomeBindingValidationFinding("RESOLVED_VERDICT_RULE_INVALID", "not_computable", "RESOLVED requires computable verdict rule."))
        status = "NOT_COMPUTABLE"

    if obj.binding_status == BindingStatus.VOID and not obj.void_reason:
        findings.append(OutcomeBindingValidationFinding("VOID_REASON_REQUIRED", "not_computable", "VOID requires a reason."))
        status = "NOT_COMPUTABLE"

    if obj.created_by_lane == "SHADOW" and obj.binding_status in {BindingStatus.BOUND, BindingStatus.RESOLUTION_PENDING, BindingStatus.RESOLVED}:
        findings.append(OutcomeBindingValidationFinding("SHADOW_BOUND_BLOCKED", "error", "SHADOW may not bind authoritative outcomes."))
        status = "BLOCKED"
    if obj.created_by_lane == "PROJECTION" and obj.binding_status != BindingStatus.DRAFT:
        findings.append(OutcomeBindingValidationFinding("PROJECTION_AUTHORITY_BLOCKED", "error", "PROJECTION may not create outcome authority."))
        status = "BLOCKED"
    if obj.created_by_lane == "CANON" and obj.binding_status != BindingStatus.DRAFT:
        findings.append(OutcomeBindingValidationFinding("CANON_BINDING_BLOCKED", "error", "CANON may define contracts only."))
        status = "BLOCKED"

    for source in obj.resolution_sources:
        if source.source_type not in ALLOWED_SOURCE_TYPES:
            findings.append(OutcomeBindingValidationFinding("RESOLUTION_SOURCE_TYPE_INVALID", "not_computable", "Unknown resolution source type."))
            if status != "BLOCKED":
                status = "NOT_COMPUTABLE"
    if obj.verdict_rule.rule_type not in ALLOWED_RULE_TYPES:
        findings.append(OutcomeBindingValidationFinding("VERDICT_RULE_TYPE_INVALID", "not_computable", "Unknown verdict rule type."))
        if status != "BLOCKED":
            status = "NOT_COMPUTABLE"

    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "binding_id": obj.binding_id}))
    return OutcomeBindingValidationReport(status=status, findings=tuple(findings), receipt_hash=receipt_hash)

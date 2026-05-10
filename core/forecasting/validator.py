from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import ForecastObject, ForecastValidationFinding, ForecastValidationReport, OutcomeBindingStatus


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _to_object(forecast: ForecastObject | Mapping[str, Any]) -> ForecastObject:
    if isinstance(forecast, ForecastObject):
        return forecast
    data = dict(forecast)
    from .models import ForecastAuthorityRef, ForecastClaim, ForecastEvidenceRef, ForecastProbability

    authority = data.get("authority_ref")
    authority_ref = ForecastAuthorityRef(**authority) if authority else None
    refs = tuple(ForecastEvidenceRef(**ref) for ref in data.get("evidence_refs", ()))
    return ForecastObject(
        schema_version=data["schema_version"],
        forecast_id=data["forecast_id"],
        claim=ForecastClaim(**data["claim"]),
        probability=ForecastProbability(**data["probability"]),
        domain=data["domain"],
        horizon=data["horizon"],
        created_by_lane=data["created_by_lane"],
        promotion_state=data["promotion_state"],
        authority_ref=authority_ref,
        evidence_refs=refs,
        outcome_binding_status=OutcomeBindingStatus(data["outcome_binding_status"]),
        calibration_ready=data["calibration_ready"],
        forecast_hash=data["forecast_hash"],
    )


def validate_forecast_object(forecast: ForecastObject | Mapping[str, Any]) -> ForecastValidationReport:
    obj = _to_object(forecast)
    findings: list[ForecastValidationFinding] = []
    status = "PASS"

    if obj.schema_version != "ForecastObject.v1":
        findings.append(ForecastValidationFinding("SCHEMA_VERSION_INVALID", "not_computable", "schema_version must be ForecastObject.v1."))
        status = "NOT_COMPUTABLE"

    p = obj.probability.value
    if p < 0.0 or p > 1.0:
        findings.append(ForecastValidationFinding("PROBABILITY_OUT_OF_RANGE", "error", "Probability must be within [0,1]."))
        status = "BLOCKED"

    if obj.calibration_ready and obj.outcome_binding_status not in {OutcomeBindingStatus.BOUND, OutcomeBindingStatus.RESOLVED}:
        findings.append(ForecastValidationFinding("CALIBRATION_READINESS_INVALID", "error", "Calibration-ready requires BOUND or RESOLVED outcome status."))
        status = "BLOCKED"

    lane = obj.created_by_lane
    if lane == "FORECAST" and obj.authority_ref is None:
        findings.append(ForecastValidationFinding("AUTHORITY_REF_MISSING", "not_computable", "FORECAST lane requires authority_ref."))
        if status != "BLOCKED":
            status = "NOT_COMPUTABLE"
    if lane == "SHADOW" and obj.promotion_state in {"CANARY", "LIMITED_PROMOTION", "CANON_ACTIVE"}:
        findings.append(ForecastValidationFinding("SHADOW_FINALIZED_BLOCKED", "error", "SHADOW lane cannot emit finalized forecast authority."))
        status = "BLOCKED"
    if lane == "PROJECTION" and obj.authority_ref is not None:
        findings.append(ForecastValidationFinding("PROJECTION_AUTHORITY_BLOCKED", "error", "PROJECTION lane cannot emit authoritative forecasts."))
        status = "BLOCKED"
    if lane == "CANON" and obj.probability.value != 0.0:
        findings.append(ForecastValidationFinding("CANON_PROBABILITY_BLOCKED", "error", "CANON lane cannot emit probability claims."))
        status = "BLOCKED"
    if lane == "OPERATOR" and not obj.evidence_refs:
        findings.append(ForecastValidationFinding("OPERATOR_EVIDENCE_REQUIRED", "warning", "OPERATOR lane should not substitute probability without evidence refs."))
        if status == "PASS":
            status = "WARN"

    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "forecast_id": obj.forecast_id}))
    return ForecastValidationReport(status=status, findings=tuple(findings), receipt_hash=receipt_hash)

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import (
    ForecastAuthorityRef,
    ForecastClaim,
    ForecastEvidenceRef,
    ForecastObject,
    ForecastProbability,
    ForecastValidationFinding,
    ForecastValidationReport,
    OutcomeBindingStatus,
)


SCHEMA_VERSION = "ForecastObject.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _as_payload(forecast: ForecastObject | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(forecast, ForecastObject):
        return asdict(forecast)
    return dict(forecast)


def canonical_forecast_json(forecast: ForecastObject | Mapping[str, Any]) -> str:
    payload = _as_payload(forecast)
    payload.pop("forecast_hash", None)
    return _canonical_json(payload)


def forecast_object_hash(forecast: ForecastObject | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_forecast_json(forecast))


def build_forecast_object(
    forecast_id: str,
    claim_statement: str,
    probability_value: float,
    domain: str,
    horizon: str,
    created_by_lane: str,
    promotion_state: str,
    authority_ref: ForecastAuthorityRef | None,
    evidence_refs: tuple[ForecastEvidenceRef, ...] = (),
    outcome_binding_status: OutcomeBindingStatus = OutcomeBindingStatus.UNBOUND,
    calibration_ready: bool = False,
    ci_low: float | None = None,
    ci_high: float | None = None,
) -> ForecastObject:
    draft = ForecastObject(
        schema_version=SCHEMA_VERSION,
        forecast_id=forecast_id,
        claim=ForecastClaim(statement=claim_statement),
        probability=ForecastProbability(value=probability_value, ci_low=ci_low, ci_high=ci_high),
        domain=domain,
        horizon=horizon,
        created_by_lane=created_by_lane,
        promotion_state=promotion_state,
        authority_ref=authority_ref,
        evidence_refs=tuple(evidence_refs),
        outcome_binding_status=outcome_binding_status,
        calibration_ready=calibration_ready,
        forecast_hash="PENDING",
    )
    return replace(draft, forecast_hash=forecast_object_hash(draft))


def validate_forecast_object(forecast: ForecastObject | Mapping[str, Any]) -> ForecastValidationReport:
    from .validator import validate_forecast_object

    return validate_forecast_object(forecast)


def write_forecast_object_contract_audit(base_dir: Path | str = ".") -> str:
    base = Path(base_dir)
    sample = build_forecast_object(
        forecast_id="forecast-object-contract-v1",
        claim_statement="Canonical forecast contract remains deterministic.",
        probability_value=0.5,
        domain="governance",
        horizon="2026-Q4",
        created_by_lane="FORECAST",
        promotion_state="SHADOW_ONLY",
        authority_ref=ForecastAuthorityRef(authority_type="CANON_FIXTURE", authority_id="fixture://forecast/authority", label="Forecast authority fixture"),
        evidence_refs=(ForecastEvidenceRef(source_type="REPO_FILE", source_id="contracts/forecasting/forecast_object.v1.schema.json", label="Contract schema"),),
        outcome_binding_status=OutcomeBindingStatus.UNBOUND,
        calibration_ready=False,
    )
    report = validate_forecast_object(sample)
    payload = {
        "status": report.status,
        "forecast_hash": sample.forecast_hash,
        "receipt_hash": report.receipt_hash,
        "findings": [asdict(f) for f in report.findings],
        "schema_version": sample.schema_version,
    }
    text = _canonical_json(payload) + "\n"
    out = base / "out/audit/forecast_object_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)

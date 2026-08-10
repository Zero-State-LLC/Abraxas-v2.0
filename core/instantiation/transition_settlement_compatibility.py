"""Resolve transition–settlement binding compatibility using fixture-only inputs.

The resolver is intentionally pure and read-only.  It takes already-loaded
artifact dictionaries (typically fixture payloads) and validates that forecast
references remain consistent when a transition participates in settlement
binding.

Conventions used here:
* ``transition`` is the instantiation transition fixture.
* ``settlement`` is a full settlement artifact referenced by ``settlement_ref``.
* ``forecast`` is an optional full forecast artifact referenced by ``forecast_ref``.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.contract_validation import (
    ContractValidationFinding as TransitionSettlementCompatibilityFinding,
)
from core.contract_validation import ContractValidationReport, build_validation_report

INCOMPATIBLE_CODE = "INVALID_NOT_COMPUTABLE"
INCOMPATIBLE_SEVERITY = "not_computable"


def _ref_pair(
    source: str,
    payload: Mapping[str, Any] | None,
    findings: list[TransitionSettlementCompatibilityFinding],
) -> tuple[str, str] | None:
    """Read a fixture object ref with deterministic failure signaling."""
    if payload is None:
        return None
    if not isinstance(payload, Mapping):
        findings.append(
            TransitionSettlementCompatibilityFinding(
                code=INCOMPATIBLE_CODE,
                severity=INCOMPATIBLE_SEVERITY,
                message=(
                    f"{source} must be a mapping with object_id and canonical_hash,"
                    f" got {type(payload).__name__}."
                ),
            )
        )
        return None

    object_id = str(payload.get("object_id", "")).strip()
    canonical_hash = str(payload.get("canonical_hash", "")).strip()
    if not object_id or not canonical_hash:
        findings.append(
            TransitionSettlementCompatibilityFinding(
                code=INCOMPATIBLE_CODE,
                severity=INCOMPATIBLE_SEVERITY,
                message=f"{source} requires object_id and canonical_hash.",
            )
        )
        return None

    return object_id, canonical_hash


def _settlement_forecast_ref(
    settlement: Mapping[str, Any],
    findings: list[TransitionSettlementCompatibilityFinding],
) -> tuple[str, str] | None:
    """Read ``forecast_id`` / ``forecast_hash`` from a settlement artifact."""
    if not isinstance(settlement, Mapping):
        findings.append(
            TransitionSettlementCompatibilityFinding(
                code=INCOMPATIBLE_CODE,
                severity=INCOMPATIBLE_SEVERITY,
                message=(
                    "settlement must be a mapping with forecast_id and forecast_hash"
                    f", got {type(settlement).__name__}."
                ),
            )
        )
        return None

    forecast_id = str(settlement.get("forecast_id", "")).strip()
    forecast_hash = str(settlement.get("forecast_hash", "")).strip()
    if not forecast_id or not forecast_hash:
        findings.append(
            TransitionSettlementCompatibilityFinding(
                code=INCOMPATIBLE_CODE,
                severity=INCOMPATIBLE_SEVERITY,
                message="settlement requires forecast_id and forecast_hash fields.",
            )
        )
        return None
    return forecast_id, forecast_hash


def _forecast_ref(
    forecast: Mapping[str, Any],
    findings: list[TransitionSettlementCompatibilityFinding],
) -> tuple[str, str] | None:
    """Read ``forecast_id`` / ``forecast_hash`` from a forecast artifact."""
    if not isinstance(forecast, Mapping):
        findings.append(
            TransitionSettlementCompatibilityFinding(
                code=INCOMPATIBLE_CODE,
                severity=INCOMPATIBLE_SEVERITY,
                message=(
                    "forecast must be a mapping with forecast_id and forecast_hash,"
                    f" got {type(forecast).__name__}."
                ),
            )
        )
        return None

    forecast_id = str(forecast.get("forecast_id", "")).strip()
    forecast_hash = str(forecast.get("forecast_hash", "")).strip()
    if not forecast_id or not forecast_hash:
        findings.append(
            TransitionSettlementCompatibilityFinding(
                code=INCOMPATIBLE_CODE,
                severity=INCOMPATIBLE_SEVERITY,
                message="forecast requires forecast_id and forecast_hash fields.",
            )
        )
        return None
    return forecast_id, forecast_hash


def validate_transition_settlement_compatibility(
    transition: Mapping[str, Any],
    *,
    settlement: Mapping[str, Any] | None = None,
    forecast: Mapping[str, Any] | None = None,
) -> ContractValidationReport:
    """Return a deterministic PASS / NOT_COMPUTABLE report.

    Rules:
    - transition + settlement with aligned forecast references: PASS
    - transition + no forecast and no settlement: NOT_COMPUTABLE
    - transition with forecast but no settlement ref: INVALID_NOT_COMPUTABLE
    - transition with settlement ref but missing settlement artifact: INVALID_NOT_COMPUTABLE
    - transition forecast_ref and settlement forecast mismatch: INVALID_NOT_COMPUTABLE
    - settlement forecast_ref mismatch against provided forecast artifact: INVALID_NOT_COMPUTABLE
    """
    if not isinstance(transition, Mapping):
        raise TypeError("transition must be a mapping")

    findings: list[TransitionSettlementCompatibilityFinding] = []

    transition_id = str(transition.get("transition_id") or "unknown_transition")
    transition_forecast = _ref_pair("forecast_ref", transition.get("forecast_ref"), findings)
    settlement_ref = _ref_pair("settlement_ref", transition.get("settlement_ref"), findings)

    status = "PASS"

    # No forecast and no settlement binding is computability-limited but not an
    # internal validation error.
    if transition_forecast is None and settlement_ref is None:
        status = "NOT_COMPUTABLE"
        return build_validation_report(
            status,
            tuple(findings),
            subject_key="transition_id",
            subject_id=transition_id,
        )

    # Forecast-only transitions are settlement-unbound.
    if transition_forecast is not None and settlement_ref is None:
        findings.append(
            TransitionSettlementCompatibilityFinding(
                code=INCOMPATIBLE_CODE,
                severity=INCOMPATIBLE_SEVERITY,
                message=(
                    "transition has forecast_ref without settlement_ref and is"
                    " therefore not settlement-bound."
                ),
            )
        )
        status = "NOT_COMPUTABLE"

    # Settlement binding requires a provided settlement artifact for compatibility checks.
    if settlement_ref is not None and settlement is None:
        findings.append(
            TransitionSettlementCompatibilityFinding(
                code=INCOMPATIBLE_CODE,
                severity=INCOMPATIBLE_SEVERITY,
                message=(
                    f"settlement artifact is missing for settlement_ref={settlement_ref[0]}."
                ),
            )
        )
        status = "NOT_COMPUTABLE"

    settlement_forecast = None
    if settlement is not None and settlement_ref is not None:
        settlement_forecast = _settlement_forecast_ref(settlement, findings)
        if settlement_forecast is None:
            status = "NOT_COMPUTABLE"

    # When both are available, enforce direct compatibility.
    if transition_forecast is not None and settlement_forecast is not None:
        if transition_forecast != settlement_forecast:
            findings.append(
                TransitionSettlementCompatibilityFinding(
                    code=INCOMPATIBLE_CODE,
                    severity=INCOMPATIBLE_SEVERITY,
                    message=(
                        "transition forecast reference does not match settlement"
                        " forecast reference."
                    ),
                )
            )
            status = "NOT_COMPUTABLE"

    # Optional cross-check: settlement forecast should match provided forecast artifact.
    if settlement_forecast is not None and forecast is not None:
        forecast_ref = _forecast_ref(forecast, findings)
        if forecast_ref is not None and forecast_ref != settlement_forecast:
            findings.append(
                TransitionSettlementCompatibilityFinding(
                    code=INCOMPATIBLE_CODE,
                    severity=INCOMPATIBLE_SEVERITY,
                    message=(
                        "settlement forecast reference does not match provided"
                        " forecast artifact."
                    ),
                )
            )
            status = "NOT_COMPUTABLE"

    if status != "PASS" and not any(f.code == INCOMPATIBLE_CODE for f in findings):
        findings.append(
            TransitionSettlementCompatibilityFinding(
                code=INCOMPATIBLE_CODE,
                severity=INCOMPATIBLE_SEVERITY,
                message="transition / settlement compatibility is not computable.",
            )
        )

    return build_validation_report(
        status,
        tuple(findings),
        subject_key="transition_id",
        subject_id=transition_id,
    )


__all__ = [
    "INCOMPATIBLE_CODE",
    "TransitionSettlementCompatibilityFinding",
    "validate_transition_settlement_compatibility",
]

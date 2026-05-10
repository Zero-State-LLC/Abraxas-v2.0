from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OutcomeBindingStatus(str, Enum):
    UNBOUND = "UNBOUND"
    BINDING_DRAFTED = "BINDING_DRAFTED"
    BOUND = "BOUND"
    RESOLVED = "RESOLVED"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"


@dataclass(frozen=True)
class ForecastClaim:
    statement: str


@dataclass(frozen=True)
class ForecastProbability:
    value: float
    ci_low: float | None = None
    ci_high: float | None = None


@dataclass(frozen=True)
class ForecastEvidenceRef:
    source_type: str
    source_id: str
    label: str


@dataclass(frozen=True)
class ForecastAuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class ForecastObject:
    schema_version: str
    forecast_id: str
    claim: ForecastClaim
    probability: ForecastProbability
    domain: str
    horizon: str
    created_by_lane: str
    promotion_state: str
    authority_ref: ForecastAuthorityRef | None
    evidence_refs: tuple[ForecastEvidenceRef, ...]
    outcome_binding_status: OutcomeBindingStatus
    calibration_ready: bool
    forecast_hash: str


@dataclass(frozen=True)
class ForecastValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class ForecastValidationReport:
    status: str
    findings: tuple[ForecastValidationFinding, ...]
    receipt_hash: str

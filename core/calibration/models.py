from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CalibrationInputRef:
    ledger_entry_id: str
    ledger_hash: str


@dataclass(frozen=True)
class CalibrationBucket:
    bucket_id: str
    lower_bound: float
    upper_bound: float
    entry_count: int
    mean_probability: float
    mean_outcome: float
    mean_brier_score: float
    calibration_gap: float


@dataclass(frozen=True)
class CalibrationAggregate:
    entry_count: int
    mean_brier_score: float
    mean_probability: float
    mean_outcome: float
    expected_calibration_error: float
    sample_policy: str


@dataclass(frozen=True)
class CalibrationReliabilityObservation:
    observation_id: str
    scope_type: str
    scope_id: str
    entry_count: int
    mean_brier_score: float
    reliability_posture: str
    mutation_allowed: bool


@dataclass(frozen=True)
class AuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class CalibrationLedger:
    schema_version: str
    calibration_ledger_id: str
    input_entries: tuple[CalibrationInputRef, ...]
    buckets: tuple[CalibrationBucket, ...]
    aggregate: CalibrationAggregate
    reliability_observations: tuple[CalibrationReliabilityObservation, ...]
    calibration_status: str
    calibration_policy: str
    created_by_lane: str
    authority_ref: AuthorityRef | None
    calibration_hash: str


@dataclass(frozen=True)
class CalibrationValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class CalibrationValidationReport:
    status: str
    findings: tuple[CalibrationValidationFinding, ...]
    receipt_hash: str

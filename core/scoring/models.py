from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BrierScoreInputRef:
    ref_type: str
    ref_id: str
    label: str


@dataclass(frozen=True)
class BrierScoreResult:
    score: float
    rounding_policy: str


@dataclass(frozen=True)
class BrierScorePolicy:
    score_type: str
    rounding_policy: str
    partial_policy: str
    void_policy: str
    conflict_policy: str


@dataclass(frozen=True)
class AuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class BrierLedgerEntry:
    schema_version: str
    ledger_entry_id: str
    forecast_id: str
    forecast_hash: str
    settlement_id: str
    settlement_hash: str
    probability: float
    settlement_decision: str
    outcome_value: float
    score_result: BrierScoreResult
    score_policy: BrierScorePolicy
    created_by_lane: str
    authority_ref: AuthorityRef | None
    ledger_hash: str


@dataclass(frozen=True)
class BrierValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class BrierValidationReport:
    status: str
    findings: tuple[BrierValidationFinding, ...]
    receipt_hash: str

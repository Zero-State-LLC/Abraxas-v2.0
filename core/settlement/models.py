from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SettlementDecision(str, Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    PARTIAL = "PARTIAL"
    VOID = "VOID"
    CONFLICTING = "CONFLICTING"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"


class SettlementStatus(str, Enum):
    DRAFT = "DRAFT"
    SETTLED = "SETTLED"
    CONFLICTING = "CONFLICTING"
    VOID = "VOID"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"


@dataclass(frozen=True)
class SettlementInputRef:
    ref_type: str
    ref_id: str
    label: str


@dataclass(frozen=True)
class SettlementReason:
    reason_id: str
    reason_type: str
    description: str
    source_ref_ids: tuple[str, ...]
    policy: str


@dataclass(frozen=True)
class SettlementConflictSummary:
    has_conflicts: bool
    conflict_ids: tuple[str, ...]
    conflict_policy: str
    resolution_posture: str


@dataclass(frozen=True)
class AuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class SettlementVerdict:
    schema_version: str
    settlement_id: str
    forecast_id: str
    forecast_hash: str
    binding_id: str
    binding_hash: str
    evidence_packet_id: str
    evidence_hash: str
    decision: SettlementDecision
    reasons: tuple[SettlementReason, ...]
    conflict_summary: SettlementConflictSummary
    settlement_status: SettlementStatus
    created_by_lane: str
    authority_ref: AuthorityRef | None
    settlement_hash: str


@dataclass(frozen=True)
class SettlementValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class SettlementValidationReport:
    status: str
    findings: tuple[SettlementValidationFinding, ...]
    receipt_hash: str

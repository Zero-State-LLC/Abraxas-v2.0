from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BindingStatus(str, Enum):
    DRAFT = "DRAFT"
    BOUND = "BOUND"
    RESOLUTION_PENDING = "RESOLUTION_PENDING"
    RESOLVED = "RESOLVED"
    VOID = "VOID"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"


@dataclass(frozen=True)
class OutcomeCriterion:
    criterion_id: str
    description: str


@dataclass(frozen=True)
class ResolutionSourceRef:
    source_type: str
    source_id: str
    label: str


@dataclass(frozen=True)
class ResolutionWindow:
    opens_at_policy: str
    closes_at_policy: str
    timezone_policy: str


@dataclass(frozen=True)
class VerdictRule:
    rule_type: str
    rule_value: str


@dataclass(frozen=True)
class AuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class OutcomeBinding:
    schema_version: str
    binding_id: str
    forecast_id: str
    forecast_hash: str
    criteria: tuple[OutcomeCriterion, ...]
    resolution_sources: tuple[ResolutionSourceRef, ...]
    resolution_window: ResolutionWindow
    verdict_rule: VerdictRule
    binding_status: BindingStatus
    created_by_lane: str
    authority_ref: AuthorityRef | None
    void_reason: str | None
    binding_hash: str


@dataclass(frozen=True)
class OutcomeBindingValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class OutcomeBindingValidationReport:
    status: str
    findings: tuple[OutcomeBindingValidationFinding, ...]
    receipt_hash: str

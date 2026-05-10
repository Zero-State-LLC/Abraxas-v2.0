from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class CanaryObservationWindow:
    window_id: str
    window_index: int
    window_policy: str
    expected_evidence_count: int
    observed_evidence_count: int
    window_status: str


@dataclass(frozen=True)
class CanaryEvidenceRef:
    source_type: str
    source_id: str
    source_hash: str
    evidence_policy: str


@dataclass(frozen=True)
class CanaryGuardrailObservation:
    guardrail_id: str
    guardrail_type: str
    observed_value_policy: str
    threshold_policy: Mapping[str, Any]
    breach_detected: bool
    breach_reason: str
    recommended_action: str


@dataclass(frozen=True)
class CanaryReadinessSummary:
    minimum_evidence_count: int
    observed_evidence_count: int
    requirements_met: bool
    guardrails_clear: bool
    ready_for_operator_review: bool
    ready_for_promotion: bool
    ready_for_rollback: bool


@dataclass(frozen=True)
class AuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class CanaryEvidenceAccumulation:
    schema_version: str
    accumulation_id: str
    activation_id: str
    activation_hash: str
    observation_windows: tuple[CanaryObservationWindow, ...]
    evidence_refs: tuple[CanaryEvidenceRef, ...]
    guardrail_observations: tuple[CanaryGuardrailObservation, ...]
    readiness_summary: CanaryReadinessSummary
    accumulation_status: str
    created_by_lane: str
    authority_ref: AuthorityRef | None
    promotion_allowed: bool
    rollback_allowed: bool
    mutation_allowed: bool
    accumulation_hash: str


@dataclass(frozen=True)
class CanaryEvidenceValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class CanaryEvidenceValidationReport:
    status: str
    findings: tuple[CanaryEvidenceValidationFinding, ...]
    receipt_hash: str

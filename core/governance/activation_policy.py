"""Bounded product activation policy (Governance V3).

Context-sensitive lanes replace blanket "all execution blocked" ceremony for
LOCAL_DEV / SANDBOX while preserving hard controls for EXTERNAL_PRODUCTION,
canon mutation, and SHADOW→FORECAST escalation.

This module is the single runtime authority for activation-lane evaluation.
Documentation and historical receipts must not override these rules.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ActivationLane(str, Enum):
    LOCAL_DEV = "LOCAL_DEV"
    SANDBOX = "SANDBOX"
    INTERNAL_CANARY = "INTERNAL_CANARY"
    EXTERNAL_PRODUCTION = "EXTERNAL_PRODUCTION"


class ActivationDecision(str, Enum):
    ALLOW = "ALLOW"
    CONDITIONAL_ALLOW = "CONDITIONAL_ALLOW"
    DENY = "DENY"
    OPERATOR_GATE = "OPERATOR_GATE"


class ActivationStatusVocabulary(str, Enum):
    DEV_ACTIVATION_ALLOWED = "DEV_ACTIVATION_ALLOWED"
    SANDBOX_ACTIVATION_ALLOWED = "SANDBOX_ACTIVATION_ALLOWED"
    INTERNAL_CANARY_CONDITIONAL = "INTERNAL_CANARY_CONDITIONAL"
    EXTERNAL_PRODUCTION_OPERATOR_GATED = "EXTERNAL_PRODUCTION_OPERATOR_GATED"


class ActivationControls(BaseModel):
    """Required controls for one activation lane."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    authorization_packet_required: bool = False
    deterministic_config_required: bool = False
    test_evidence_required: bool = False
    isolation_required: bool = False
    reversibility_required: bool = False
    bounded_credentials_required: bool = False
    deployment_manifest_required: bool = False
    observability_required: bool = False
    rollback_required: bool = False
    credential_boundary_required: bool = False
    operator_review_required: bool = False
    explicit_operator_approval_required: bool = False
    release_evidence_required: bool = False
    security_gate_required: bool = False
    production_credentials_required: bool = False
    # Evidence from outside the candidate (core/governance/activation_evidence.py).
    independent_evidence_required: bool = False
    external_side_effects: str = "denied_by_default"


LANE_POLICY: dict[ActivationLane, ActivationControls] = {
    ActivationLane.LOCAL_DEV: ActivationControls(
        authorization_packet_required=False,
        deterministic_config_required=True,
        test_evidence_required=True,
        external_side_effects="denied_by_default",
    ),
    ActivationLane.SANDBOX: ActivationControls(
        authorization_packet_required=False,
        isolation_required=True,
        reversibility_required=True,
        bounded_credentials_required=True,
        external_side_effects="allowlisted_only",
    ),
    ActivationLane.INTERNAL_CANARY: ActivationControls(
        deployment_manifest_required=True,
        observability_required=True,
        rollback_required=True,
        credential_boundary_required=True,
        operator_review_required=True,
        independent_evidence_required=True,
        external_side_effects="allowlisted_only",
    ),
    ActivationLane.EXTERNAL_PRODUCTION: ActivationControls(
        explicit_operator_approval_required=True,
        release_evidence_required=True,
        security_gate_required=True,
        rollback_required=True,
        production_credentials_required=True,
        operator_review_required=True,
        external_side_effects="operator_authorized_only",
    ),
}

LANE_DEFAULT_DECISION: dict[ActivationLane, ActivationDecision] = {
    ActivationLane.LOCAL_DEV: ActivationDecision.ALLOW,
    ActivationLane.SANDBOX: ActivationDecision.ALLOW,
    ActivationLane.INTERNAL_CANARY: ActivationDecision.CONDITIONAL_ALLOW,
    ActivationLane.EXTERNAL_PRODUCTION: ActivationDecision.OPERATOR_GATE,
}

LANE_STATUS_VOCABULARY: dict[ActivationLane, ActivationStatusVocabulary] = {
    ActivationLane.LOCAL_DEV: ActivationStatusVocabulary.DEV_ACTIVATION_ALLOWED,
    ActivationLane.SANDBOX: ActivationStatusVocabulary.SANDBOX_ACTIVATION_ALLOWED,
    ActivationLane.INTERNAL_CANARY: ActivationStatusVocabulary.INTERNAL_CANARY_CONDITIONAL,
    ActivationLane.EXTERNAL_PRODUCTION: (
        ActivationStatusVocabulary.EXTERNAL_PRODUCTION_OPERATOR_GATED
    ),
}

# Hard boundaries preserved across all lanes (not ceremony).
HARD_BOUNDARIES: tuple[str, ...] = (
    "autonomous_canon_promotion",
    "shadow_to_forecast_escalation_without_promotion_path",
    "broad_or_persistent_external_writeback",
    "unbounded_credentials_or_secret_exposure",
    "destructive_mutation_without_rollback",
    "fabricated_evidence_or_fake_readiness_claims",
    "public_production_deployment_without_operator_approval",
)


class ActivationRequest(BaseModel):
    """Declarative request describing intended effects of a runtime path."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    lane: ActivationLane
    external_side_effects: bool = False
    uses_production_credentials: bool = False
    mutates_canon: bool = False
    escalates_shadow_to_forecast: bool = False
    irreversible_mutation: bool = False
    billing_or_customer_data: bool = False
    deployment_manifest_present: bool = False
    observability_present: bool = False
    rollback_present: bool = False
    credential_boundary_present: bool = False
    operator_review_present: bool = False
    explicit_operator_approval_present: bool = False
    release_evidence_present: bool = False
    security_gate_present: bool = False
    isolation_present: bool = False
    reversibility_present: bool = False
    bounded_credentials_present: bool = False
    deterministic_config_present: bool = True
    test_evidence_present: bool = True
    # EvidenceStatus value from verify_activation_evidence; only "VERIFIED"
    # satisfies independent_evidence_required. Self-declared booleans cannot.
    independent_evidence_status: str | None = None
    notes: tuple[str, ...] = Field(default_factory=tuple)


class ActivationEvaluation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    lane: ActivationLane
    decision: ActivationDecision
    status_vocabulary: ActivationStatusVocabulary
    controls: ActivationControls
    missing_controls: tuple[str, ...]
    hard_boundary_violations: tuple[str, ...]
    authorization_packet_required: bool
    permitted: bool
    reasons: tuple[str, ...]


def controls_for(lane: ActivationLane | str) -> ActivationControls:
    resolved = ActivationLane(lane)
    return LANE_POLICY[resolved]


def policy_matrix() -> dict[str, dict[str, Any]]:
    """Return the canonical lane matrix as plain JSON-serializable data."""
    matrix: dict[str, dict[str, Any]] = {}
    for lane, controls in LANE_POLICY.items():
        matrix[lane.value] = {
            "default_decision": LANE_DEFAULT_DECISION[lane].value,
            "status_vocabulary": LANE_STATUS_VOCABULARY[lane].value,
            "controls": controls.model_dump(mode="python"),
        }
    return matrix


def _missing_controls(request: ActivationRequest, controls: ActivationControls) -> list[str]:
    missing: list[str] = []
    checks: tuple[tuple[bool, str, bool], ...] = (
        (controls.deterministic_config_required, "deterministic_config", request.deterministic_config_present),
        (controls.test_evidence_required, "test_evidence", request.test_evidence_present),
        (controls.isolation_required, "isolation", request.isolation_present),
        (controls.reversibility_required, "reversibility", request.reversibility_present),
        (controls.bounded_credentials_required, "bounded_credentials", request.bounded_credentials_present),
        (controls.deployment_manifest_required, "deployment_manifest", request.deployment_manifest_present),
        (controls.observability_required, "observability", request.observability_present),
        (controls.rollback_required, "rollback", request.rollback_present),
        (controls.credential_boundary_required, "credential_boundary", request.credential_boundary_present),
        (controls.operator_review_required, "operator_review", request.operator_review_present),
        (
            controls.explicit_operator_approval_required,
            "explicit_operator_approval",
            request.explicit_operator_approval_present,
        ),
        (controls.release_evidence_required, "release_evidence", request.release_evidence_present),
        (controls.security_gate_required, "security_gate", request.security_gate_present),
        (
            controls.production_credentials_required,
            "production_credentials",
            request.uses_production_credentials,
        ),
    )
    if controls.independent_evidence_required and request.independent_evidence_status != "VERIFIED":
        missing.append(f"independent_evidence:{request.independent_evidence_status or 'ABSENT'}")
    for required, name, present in checks:
        if required and not present:
            missing.append(name)
    return missing


def _hard_boundary_violations(request: ActivationRequest) -> list[str]:
    violations: list[str] = []
    if request.mutates_canon:
        violations.append("autonomous_canon_promotion")
    if request.escalates_shadow_to_forecast:
        violations.append("shadow_to_forecast_escalation_without_promotion_path")
    if request.irreversible_mutation and not request.rollback_present:
        violations.append("destructive_mutation_without_rollback")
    if request.uses_production_credentials and request.lane != ActivationLane.EXTERNAL_PRODUCTION:
        violations.append("unbounded_credentials_or_secret_exposure")
    if (
        request.billing_or_customer_data
        and request.lane != ActivationLane.EXTERNAL_PRODUCTION
    ):
        violations.append("public_production_deployment_without_operator_approval")
    if request.external_side_effects and request.lane == ActivationLane.LOCAL_DEV:
        violations.append("broad_or_persistent_external_writeback")
    return violations


def evaluate_activation(request: ActivationRequest | Mapping[str, Any]) -> ActivationEvaluation:
    """Evaluate whether a requested activation is permitted under lane policy."""
    req = (
        request
        if isinstance(request, ActivationRequest)
        else ActivationRequest.model_validate(dict(request))
    )
    controls = controls_for(req.lane)
    missing = _missing_controls(req, controls)
    hard = _hard_boundary_violations(req)
    reasons: list[str] = []

    if hard:
        decision = ActivationDecision.DENY
        permitted = False
        reasons.append("hard_boundary_violation")
        reasons.extend(hard)
    elif req.lane == ActivationLane.EXTERNAL_PRODUCTION:
        decision = ActivationDecision.OPERATOR_GATE
        permitted = False
        reasons.append("external_production_requires_separate_operator_decision")
        if missing:
            reasons.append("missing_controls:" + ",".join(missing))
    elif req.lane == ActivationLane.INTERNAL_CANARY:
        if missing:
            decision = ActivationDecision.DENY
            permitted = False
            reasons.append("missing_controls:" + ",".join(missing))
        else:
            decision = ActivationDecision.CONDITIONAL_ALLOW
            permitted = True
            reasons.append("internal_canary_conditional_controls_satisfied")
    else:
        # LOCAL_DEV / SANDBOX
        if missing:
            decision = ActivationDecision.DENY
            permitted = False
            reasons.append("missing_controls:" + ",".join(missing))
        else:
            decision = LANE_DEFAULT_DECISION[req.lane]
            permitted = True
            reasons.append(f"{req.lane.value.lower()}_activation_allowed")

    return ActivationEvaluation(
        lane=req.lane,
        decision=decision,
        status_vocabulary=LANE_STATUS_VOCABULARY[req.lane],
        controls=controls,
        missing_controls=tuple(missing),
        hard_boundary_violations=tuple(hard),
        authorization_packet_required=controls.authorization_packet_required,
        permitted=permitted,
        reasons=tuple(reasons),
    )


def authorization_packet_required_for(lane: ActivationLane | str) -> bool:
    """Routine LOCAL_DEV/SANDBOX engineering does not require authorization packets."""
    return controls_for(lane).authorization_packet_required

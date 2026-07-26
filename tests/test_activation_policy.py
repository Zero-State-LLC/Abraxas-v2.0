"""Exhaustive lane tests for bounded activation policy."""

from __future__ import annotations

import pytest

from core.governance.activation_policy import (
    ActivationDecision,
    ActivationLane,
    ActivationRequest,
    ActivationStatusVocabulary,
    authorization_packet_required_for,
    evaluate_activation,
    policy_matrix,
)


@pytest.mark.parametrize("lane", list(ActivationLane))
def test_policy_matrix_covers_all_lanes(lane: ActivationLane) -> None:
    matrix = policy_matrix()
    assert lane.value in matrix
    assert "controls" in matrix[lane.value]
    assert "default_decision" in matrix[lane.value]


def test_local_dev_allows_without_authorization_packet() -> None:
    result = evaluate_activation(
        ActivationRequest(
            lane=ActivationLane.LOCAL_DEV,
            deterministic_config_present=True,
            test_evidence_present=True,
        )
    )
    assert result.permitted is True
    assert result.decision == ActivationDecision.ALLOW
    assert result.authorization_packet_required is False
    assert result.status_vocabulary == ActivationStatusVocabulary.DEV_ACTIVATION_ALLOWED
    assert authorization_packet_required_for(ActivationLane.LOCAL_DEV) is False


def test_local_dev_denies_missing_test_evidence() -> None:
    result = evaluate_activation(
        ActivationRequest(
            lane=ActivationLane.LOCAL_DEV,
            deterministic_config_present=True,
            test_evidence_present=False,
        )
    )
    assert result.permitted is False
    assert result.decision == ActivationDecision.DENY
    assert "test_evidence" in result.missing_controls


def test_local_dev_denies_external_side_effects() -> None:
    result = evaluate_activation(
        ActivationRequest(
            lane=ActivationLane.LOCAL_DEV,
            external_side_effects=True,
        )
    )
    assert result.permitted is False
    assert "broad_or_persistent_external_writeback" in result.hard_boundary_violations


def test_sandbox_allows_when_isolated_and_reversible() -> None:
    result = evaluate_activation(
        ActivationRequest(
            lane=ActivationLane.SANDBOX,
            isolation_present=True,
            reversibility_present=True,
            bounded_credentials_present=True,
        )
    )
    assert result.permitted is True
    assert result.decision == ActivationDecision.ALLOW
    assert result.authorization_packet_required is False


def test_sandbox_denies_without_isolation() -> None:
    result = evaluate_activation(
        ActivationRequest(
            lane=ActivationLane.SANDBOX,
            isolation_present=False,
            reversibility_present=True,
            bounded_credentials_present=True,
        )
    )
    assert result.permitted is False
    assert "isolation" in result.missing_controls


def test_internal_canary_conditional_when_controls_present() -> None:
    result = evaluate_activation(
        ActivationRequest(
            lane=ActivationLane.INTERNAL_CANARY,
            deployment_manifest_present=True,
            observability_present=True,
            rollback_present=True,
            credential_boundary_present=True,
            operator_review_present=True,
        )
    )
    assert result.permitted is True
    assert result.decision == ActivationDecision.CONDITIONAL_ALLOW
    assert (
        result.status_vocabulary
        == ActivationStatusVocabulary.INTERNAL_CANARY_CONDITIONAL
    )


def test_internal_canary_denies_incomplete_controls() -> None:
    result = evaluate_activation(
        ActivationRequest(
            lane=ActivationLane.INTERNAL_CANARY,
            deployment_manifest_present=True,
        )
    )
    assert result.permitted is False
    assert result.decision == ActivationDecision.DENY


def test_external_production_is_operator_gated_even_with_controls() -> None:
    result = evaluate_activation(
        ActivationRequest(
            lane=ActivationLane.EXTERNAL_PRODUCTION,
            explicit_operator_approval_present=True,
            release_evidence_present=True,
            security_gate_present=True,
            rollback_present=True,
            uses_production_credentials=True,
            operator_review_present=True,
        )
    )
    assert result.permitted is False
    assert result.decision == ActivationDecision.OPERATOR_GATE
    assert (
        result.status_vocabulary
        == ActivationStatusVocabulary.EXTERNAL_PRODUCTION_OPERATOR_GATED
    )


def test_canon_mutation_hard_boundary() -> None:
    result = evaluate_activation(
        ActivationRequest(
            lane=ActivationLane.LOCAL_DEV,
            mutates_canon=True,
        )
    )
    assert result.permitted is False
    assert "autonomous_canon_promotion" in result.hard_boundary_violations


def test_shadow_to_forecast_hard_boundary() -> None:
    result = evaluate_activation(
        ActivationRequest(
            lane=ActivationLane.SANDBOX,
            isolation_present=True,
            reversibility_present=True,
            bounded_credentials_present=True,
            escalates_shadow_to_forecast=True,
        )
    )
    assert result.permitted is False
    assert (
        "shadow_to_forecast_escalation_without_promotion_path"
        in result.hard_boundary_violations
    )

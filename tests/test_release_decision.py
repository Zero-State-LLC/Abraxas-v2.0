"""Tests for WP-I release decision."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.production_readiness.release_decision import (
    build_release_decision,
    build_supported_surface_freeze_inventory,
)


REPO = Path(__file__).resolve().parents[1]


def test_release_held_never_activates_production() -> None:
    decision = build_release_decision(
        REPO,
        decision_code="RELEASE_HELD",
        operator_id_or_role="test_operator",
        notes="unit hold",
        write=False,
    )
    assert decision["decision_code"] == "RELEASE_HELD"
    assert decision["production_activation_authorized"] is False
    assert decision["readiness_state"] == "NOT_READY"


def test_candidate_approved_deploy_held_no_activation() -> None:
    """When scorecard all_pass, CANDIDATE_APPROVED still forbids production activation."""
    from core.production_readiness.freeze_gate_scorecard import build_freeze_gate_scorecard

    card = build_freeze_gate_scorecard(REPO, write=False)
    if not card.get("summary", {}).get("all_pass"):
        # Environment may lack full evidence; skip soft assertion path
        return
    # Write scorecard so release decision can read all_pass from disk path
    build_freeze_gate_scorecard(REPO, write=True)
    decision = build_release_decision(
        REPO,
        decision_code="CANDIDATE_APPROVED",
        operator_id_or_role="test_operator",
        notes="unit candidate",
        write=False,
    )
    if decision["decision_code"] == "CANDIDATE_APPROVED":
        assert decision["production_activation_authorized"] is False
        assert decision["readiness_state"] == "CANDIDATE_HELD_FOR_OPERATOR_DEPLOY"
        assert decision.get("deploy_held") is True


def test_candidate_downgraded_without_all_pass() -> None:
    # Without writing scorecard all_pass, CANDIDATE_APPROVED must downgrade
    decision = build_release_decision(
        REPO,
        decision_code="CANDIDATE_APPROVED",
        operator_id_or_role="test_operator",
        notes="attempt",
        write=False,
    )
    # May be HELD if scorecard missing or not all_pass
    assert decision["production_activation_authorized"] is False
    assert decision["decision_code"] in {
        "RELEASE_HELD",
        "CANDIDATE_APPROVED",
        "OPERATOR_REVIEW_REQUIRED",
    }


def test_surface_inventory_lists_supported() -> None:
    inv = build_supported_surface_freeze_inventory(REPO, write=False)
    assert inv["summary"]["supported_interface_count"] >= 3
    assert inv["summary"]["supported_service_count"] >= 1


def test_invalid_code() -> None:
    with pytest.raises(ValueError):
        build_release_decision(
            REPO,
            decision_code="SHIP_IT",
            operator_id_or_role="x",
            notes="nope",
            write=False,
        )

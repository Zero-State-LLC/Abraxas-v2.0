"""Tests for WP-P+ threat model operator decision record."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.production_readiness.threat_model_operator_decision_record import (
    build_threat_model_operator_decision_record,
)


REPO = Path(__file__).resolve().parents[1]


def test_accept_partial_never_authorizes_production() -> None:
    rec = build_threat_model_operator_decision_record(
        REPO,
        decision_code="ACCEPT_PARTIAL_BASELINE",
        operator_id_or_role="test_operator",
        notes="unit test acceptance",
        write=False,
    )
    assert rec["decision_code"] == "ACCEPT_PARTIAL_BASELINE"
    assert rec["operator_review_state"] == "ACCEPTED_PARTIAL"
    assert rec["production_activation_authorized"] is False
    assert rec["readiness_state"] == "NOT_READY"
    assert "RR-01" in rec["acknowledged_residual_risk_ids"]


def test_invalid_code_rejected() -> None:
    with pytest.raises(ValueError):
        build_threat_model_operator_decision_record(
            REPO,
            decision_code="ACCEPT_PRODUCTION",
            operator_id_or_role="x",
            notes="nope",
            write=False,
        )

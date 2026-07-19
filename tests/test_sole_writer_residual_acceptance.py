"""Tests for WP-Q sole-writer residual acceptance."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.sole_writer_residual_acceptance import (
    build_sole_writer_residual_acceptance,
)


REPO = Path(__file__).resolve().parents[1]


def test_accept_known_residual_no_fail_closed() -> None:
    packet = build_sole_writer_residual_acceptance(
        REPO,
        operator_id_or_role="test_operator",
        decision="ACCEPT_KNOWN_RESIDUAL",
        notes="unit test",
        write=False,
    )
    assert packet["schema_version"] == "sole_writer_residual_acceptance.v1"
    assert packet["fail_closed_enabled"] is False
    assert packet["production_activation_authorized"] is False
    assert packet["observed"]["finding_count"] >= 0
    if packet["under_threshold"]:
        assert packet["gate_4_satisfied"] is True
        assert packet["acceptance_status"] == "ACCEPTED_KNOWN_RESIDUAL"

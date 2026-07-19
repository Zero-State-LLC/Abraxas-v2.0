"""Tests for WP-AUTH production activation authority gate."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.production_activation_authority_gate import (
    build_production_activation_authority_gate,
)


REPO = Path(__file__).resolve().parents[1]


def test_activation_gate_denied_fail_closed() -> None:
    gate = build_production_activation_authority_gate(REPO, write=False)
    assert gate["schema_version"] == "production_activation_authority_gate.v1"
    assert gate["status"] == "DENIED"
    assert gate["production_activation_authorized"] is False
    assert gate["fail_closed"] is True
    assert gate["authorization_token_honored"] is False

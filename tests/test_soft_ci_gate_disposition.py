"""Tests for WP-N2 soft CI gate disposition."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.soft_ci_gate_disposition import (
    build_soft_ci_gate_disposition,
)


REPO = Path(__file__).resolve().parents[1]


def test_disposition_keeps_fail_closed_off() -> None:
    packet = build_soft_ci_gate_disposition(REPO, write=False)
    assert packet["schema_version"] == "soft_ci_gate_disposition.v1"
    assert packet["fail_closed_enabled"] is False
    assert packet["summary"]["fail_closed_promotions"] == 0
    assert packet["summary"]["disposition_count"] >= 3

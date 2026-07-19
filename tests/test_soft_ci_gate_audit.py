"""Tests for WP-N soft CI gate audit."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.soft_ci_gate_audit import build_soft_ci_gate_audit


REPO = Path(__file__).resolve().parents[1]


def test_soft_ci_audit_finds_continue_on_error() -> None:
    audit = build_soft_ci_gate_audit(REPO, write=False)
    assert audit["schema_version"] == "soft_ci_gate_audit.v1"
    assert audit["summary"]["workflow_continue_on_error_count"] >= 1
    kinds = {f["kind"] for f in audit["findings"]}
    assert "workflow_continue_on_error" in kinds
    assert "fast_ci_advisory_fail_open" in kinds or "fast_ci_advisory_command" in kinds

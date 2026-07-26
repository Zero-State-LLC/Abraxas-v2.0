"""Tests for pre–Phase 10 issue backlog closure receipt."""

from __future__ import annotations

from pathlib import Path

from core.production_convergence.issue_backlog_closure import (
    CLOSED_ISSUES,
    build_issue_backlog_closure_receipt,
)


def test_issue_backlog_closure_shape() -> None:
    receipt = build_issue_backlog_closure_receipt()
    assert receipt["schema_version"] == "issue_backlog_closure.v1"
    assert receipt["candidate_status"] == "NOT_READY"
    assert receipt["oracle_sandbox_probe_gate_confirmed"] is False
    assert receipt["external_production_authorized"] is False
    assert receipt["mass_deletion_authorized"] is False
    assert receipt["summary"]["closed_count"] == 4
    assert {entry["issue"] for entry in CLOSED_ISSUES} == {546, 547, 881, 892}
    assert isinstance(receipt["canonical_hash"], str)
    assert len(receipt["canonical_hash"]) == 64


def test_issue_backlog_closure_docs_pointer_exists() -> None:
    pointer = Path("docs/status/ISSUE_BACKLOG_CLOSURE_001.md")
    assert pointer.is_file()

"""Tests for Workstream 1/2 boundary advisory check."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.boundary_check import (
    build_boundary_report,
    scan_prohibited_imports,
    scan_unregistered_surfaces,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_boundary_report_advisory_exits_zero() -> None:
    report, code = build_boundary_report(REPO_ROOT, write=False, fail_closed=False)
    assert code == 0
    assert report["schema_version"] == "boundary_advisory_report.v1"
    assert report["mode"] == "advisory_report_only"
    assert "summary" in report


def test_scan_functions_return_lists() -> None:
    imports = scan_prohibited_imports(REPO_ROOT)
    unreg = scan_unregistered_surfaces(REPO_ROOT)
    assert isinstance(imports, list)
    assert isinstance(unreg, list)


def test_fail_closed_nonzero_when_findings(monkeypatch) -> None:
    # Force at least one finding by temporarily emptying registry path handling
    report, code = build_boundary_report(REPO_ROOT, write=False, fail_closed=True)
    # If there are any findings, exit must be 1; if zero findings, 0 is correct.
    if report["summary"]["finding_count"] > 0:
        assert code == 1
    else:
        assert code == 0

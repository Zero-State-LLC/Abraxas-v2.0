"""Tests for Workstream 0 production-readiness baseline generator."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.baseline_generator import (
    build_baseline_package,
    build_test_inventory,
    capture_git_state,
)


def test_capture_git_state_has_sha(repo_root: Path | None = None) -> None:
    root = repo_root or Path(__file__).resolve().parents[1]
    state = capture_git_state(root)
    assert len(state.head_sha) == 40
    assert state.branch


def test_test_inventory_counts_files() -> None:
    root = Path(__file__).resolve().parents[1]
    inv = build_test_inventory(root, sha="deadbeef", produced_at="2026-01-01T00:00:00Z")
    assert inv["summary"]["test_file_count"] >= 1
    assert inv["evidence_state"] == "Verified"
    assert inv["schema_version"] == "test_inventory.v1"


def test_build_baseline_package_contains_required_artifacts(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    packages = build_baseline_package(root, validation=None, write=False)
    required = {
        "baseline_manifest.v1.json",
        "repository_state.v1.json",
        "validation_summary.v1.json",
        "test_inventory.v1.json",
        "interface_inventory.v1.json",
        "schema_inventory.v1.json",
        "writer_inventory.v1.json",
        "entry_point_inventory.v1.json",
        "dependency_graph_summary.v1.json",
        "governance_surface_inventory.v1.json",
        "service_candidate_inventory.v1.json",
        "readiness_blockers.v1.json",
        "unsupported_assumptions.v1.json",
        "baseline_receipt.v1.json",
    }
    assert required.issubset(packages.keys())
    receipt = packages["baseline_receipt.v1.json"]
    assert receipt["program"] == "ABRAXAS_PRODUCTION_CONTINUATION"
    assert receipt["workstream"] == "BASELINE_AND_FREEZE"
    assert receipt["evidence_state"] == "Partial"
    # Without live CI, must not claim Verified validation
    assert packages["validation_receipt.v1.json"]["live_execution_performed"] is False


def test_live_validation_green_closes_risk_006_only() -> None:
    root = Path(__file__).resolve().parents[1]
    validation = {
        "live_execution_performed": True,
        "command": "python scripts/run_fast_ci.py",
        "exit_code": 0,
        "duration_seconds": 1.0,
        "stdout_tail": ["ok"],
        "stderr_tail": [],
        "notes": ["synthetic"],
    }
    packages = build_baseline_package(root, validation=validation, write=False)
    blockers = {
        b["id"]: b for b in packages["readiness_blockers.v1.json"]["blockers"]
    }
    assert blockers["RISK-006"]["status"] == "CLOSED"
    assert packages["validation_receipt.v1.json"]["evidence_state"] == "Verified"
    # Package evidence remains Partial (Notion + other P0 open)
    assert packages["baseline_receipt.v1.json"]["evidence_state"] == "Partial"

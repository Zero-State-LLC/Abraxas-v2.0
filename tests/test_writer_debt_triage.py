"""Tests for WP-A writer debt triage."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.writer_debt_triage import (
    build_writer_debt_triage,
    classify_path,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_classify_runtime_and_skills() -> None:
    assert classify_path("core/brier/runtime.py") == "RUNTIME_PACKET_WRITER"
    assert classify_path("skills/abx-neon-genie/x.py") == "SKILL_OUT_WRITER"
    assert classify_path("abx-afe/afe/cli.py") == "ABX_AFE_WRITER"
    assert classify_path("core/abraxas_oracle_execution_boundary.py") == (
        "ORACLE_EXECUTION_WRITER"
    )


def test_triage_report_shape() -> None:
    report = build_writer_debt_triage(REPO_ROOT, write=False)
    assert report["schema_version"] == "writer_debt_triage.v1"
    assert report["work_package"] == "WP-A_WRITER_DEBT_TRIAGE"
    assert report["summary"]["classified_finding_count"] >= 1
    assert report["summary"]["fail_closed_ready"] is False
    assert any(c["debt_class"] == "RUNTIME_PACKET_WRITER" for c in report["classes"])
    assert len(report["consolidation_decisions"]) >= 2

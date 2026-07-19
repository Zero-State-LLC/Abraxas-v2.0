"""Tests for production readiness docs crosslink check."""

from __future__ import annotations

from pathlib import Path

from core.production_readiness.docs_crosslink_check import build_docs_crosslink_check


REPO = Path(__file__).resolve().parents[1]


def test_docs_crosslink_check_runs() -> None:
    report = build_docs_crosslink_check(REPO, write=False)
    assert report["schema_version"] == "production_readiness_docs_crosslink_check.v1"
    assert report["summary"]["docs_scanned"] >= 3
    # Primary docs must exist
    assert (REPO / "out/production_readiness/README.md").is_file()
    assert (REPO / "docs/production_readiness/ENGINEERING_GUIDEBOOK.md").is_file()

"""WP-D4-C2: core ingest scheduler module is pure (no out/ publication)."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_scheduler_core_has_no_write_helpers() -> None:
    text = (REPO / "core/ingest/scheduler.py").read_text(encoding="utf-8")
    assert "write_canonical_json(" not in text
    assert "from core.canonical.json import write_canonical_json" not in text
    assert "write_scheduler_outputs" not in text


def test_governance_audit_core_has_no_write_helper() -> None:
    text = (
        REPO / "core/ingest/controlled_ingest_scheduler_governance_audit.py"
    ).read_text(encoding="utf-8")
    assert "write_canonical_json(" not in text
    assert "from core.canonical.json import write_canonical_json" not in text
    assert "def write_controlled_ingest_scheduler_governance_audit" not in text


def test_ingest_scheduler_runner_exists() -> None:
    assert (REPO / "scripts/ingest/run_ingest_scheduler.py").is_file()

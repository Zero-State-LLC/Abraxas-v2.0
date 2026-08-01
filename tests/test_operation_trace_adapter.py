"""Tests for Slice D OperationTrace adapter (AI OS kernel)."""

from __future__ import annotations

import json
from pathlib import Path

from core.ingest.familiar_ingestion_receipt import (
    build_familiar_ingestion_receipt_from_path,
)
from core.signal.operation_trace_adapter import (
    receipt_to_operation_trace,
    touchpoint_to_operation_trace,
    write_operation_trace,
)
from core.signal.spine_bridge import build_touchpoint_from_pack_path

REPO = Path(__file__).resolve().parents[1]
FIXTURE = (
    REPO
    / "skills"
    / "abx-familiar-signal-forager"
    / "fixtures"
    / "evidence_pack_hermes_skill_os_2026-07-27.v0.json"
)


def test_receipt_to_trace_fixture():
    receipt = build_familiar_ingestion_receipt_from_path(FIXTURE, repo_root=REPO)
    trace = receipt_to_operation_trace(receipt)
    assert trace["task_class"] == "signal_forage"
    assert "OS_SIGNAL_OBSERVED" in trace["validation_results"]
    assert trace["evidence_status"] == "OBSERVED"
    assert trace["advisory_only"] is True
    assert trace["authority"]["execution_authority"] is False
    assert "trace_hash" in trace


def test_touchpoint_to_trace():
    tp = build_touchpoint_from_pack_path(FIXTURE, repo_root=REPO)
    trace = touchpoint_to_operation_trace(tp)
    assert trace["task_class"] == "signal_spine_projection"
    assert any("SPINE_TOUCH" in v for v in trace["validation_results"])


def test_write_trace(tmp_path: Path):
    receipt = build_familiar_ingestion_receipt_from_path(FIXTURE, repo_root=REPO)
    trace = receipt_to_operation_trace(receipt)
    out = write_operation_trace(trace, out_dir=tmp_path)
    assert out.exists()
    loaded = json.loads(out.read_text())
    assert loaded["operation_id"] == trace["operation_id"]

from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash
from core.viz01_live_feed_enhancement_receipt import (
    DEFAULT_OUT_PATH,
    STATUS,
    build_viz01_live_feed_enhancement_receipt,
)
from scripts import run_viz01_live_feed_enhancement_receipt


def test_viz01_receipt_status_and_locks() -> None:
    packet = build_viz01_live_feed_enhancement_receipt()
    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False


def test_viz01_receipt_canonical_hash_is_stable() -> None:
    first = build_viz01_live_feed_enhancement_receipt()
    second = build_viz01_live_feed_enhancement_receipt()
    assert first["canonical_hash"] == second["canonical_hash"]
    without_hash = dict(first)
    without_hash.pop("canonical_hash")
    assert first["canonical_hash"] == canonical_hash(without_hash)


def test_viz01_receipt_runner_writes_packet(tmp_path: Path) -> None:
    out_path = tmp_path / "viz01.latest.json"
    packet = run_viz01_live_feed_enhancement_receipt.run(out_path=out_path)
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert written == packet
    assert written["status"] == STATUS


def test_viz01_default_out_path_is_audit_receipt() -> None:
    assert DEFAULT_OUT_PATH == "out/audit/viz01_live_feed_enhancement_receipt_001.latest.json"

from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash
from core.temporal_continuity_p80_authorization_record_regeneration_receipt import (
    DEFAULT_OUT_PATH,
    STATUS,
    build_temporal_continuity_p80_authorization_record_regeneration_receipt,
)
from Scripts import (  # noqa: E501
    run_temporal_continuity_p80_authorization_record_regeneration_receipt as runner,
)


def test_slice51_receipt_wraps_existing_p80_regeneration_plan() -> None:
    packet = build_temporal_continuity_p80_authorization_record_regeneration_receipt()
    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert packet["p80_regeneration_summary"]["p80_regeneration_plan_status"] in {
        "NOT_COMPUTABLE",
        "P80_REGENERATION_PLAN_READY",
        "P80_REGENERATION_PLAN_BLOCKED",
        "P80_REGENERATION_NOT_REQUIRED",
    }


def test_slice51_authority_locks_are_false() -> None:
    packet = build_temporal_continuity_p80_authorization_record_regeneration_receipt()
    assert packet["authority_locks"]
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False


def test_slice51_canonical_hash_is_stable() -> None:
    first = build_temporal_continuity_p80_authorization_record_regeneration_receipt()
    second = build_temporal_continuity_p80_authorization_record_regeneration_receipt()
    assert first["canonical_hash"] == second["canonical_hash"]
    without_hash = dict(first)
    without_hash.pop("canonical_hash")
    assert first["canonical_hash"] == canonical_hash(without_hash)


def test_slice51_runner_writes_receipt(tmp_path: Path) -> None:
    out_path = tmp_path / "slice51.latest.json"
    packet = runner.run(out_path=out_path)
    written = json.loads(out_path.read_text(encoding="utf-8"))
    assert written == packet
    assert written["status"] == STATUS


def test_slice51_default_out_path_is_audit_receipt() -> None:
    assert DEFAULT_OUT_PATH == (
        "out/audit/"
        "temporal_continuity_p80_authorization_record_"
        "regeneration_receipt_001.latest.json"
    )

from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash
from core.continuity_namespace_migration_preflight import (
    AUTHORITY_LOCKS,
    DEFAULT_OUT_PATH,
    DEGRADED_STATUS,
    MIGRATION_RUN_RECEIPT_PATH,
    STATUS,
    build_continuity_namespace_migration_preflight_receipt,
)
from scripts.temporal.run_continuity_namespace_migration_preflight_receipt import run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_migration_preflight_receipt_is_ready_and_advisory() -> None:
    packet = build_continuity_namespace_migration_preflight_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["preflight_summary"]["held_count"] == 0
    assert packet["preflight_summary"]["valid_for_implementation"] is False


def test_migration_preflight_hash_is_canonical() -> None:
    packet = build_continuity_namespace_migration_preflight_receipt(repo_root=REPO_ROOT)
    without_hash = {
        key: value for key, value in packet.items() if key != "canonical_hash"
    }

    assert packet["canonical_hash"] == canonical_hash(without_hash)


def test_migration_preflight_checks_required_surfaces() -> None:
    packet = build_continuity_namespace_migration_preflight_receipt(repo_root=REPO_ROOT)
    check_ids = {check["check_id"] for check in packet["preflight_checks"]}

    assert "continuity_namespace_migration_run_001.latest_observed" in check_ids
    assert "continuity_namespace_migration_run_001.latest_authority_locks" in check_ids
    assert "migration_runner_execution_posture" in check_ids
    assert "alias_design_remains_held" in check_ids
    assert all(check["authority_granted"] is False for check in packet["preflight_checks"])


def test_migration_preflight_fails_closed_when_sources_missing(tmp_path: Path) -> None:
    packet = build_continuity_namespace_migration_preflight_receipt(repo_root=tmp_path)

    assert packet["status"] == DEGRADED_STATUS
    assert packet["source_status"] == "READY_WITH_FINDINGS"
    assert packet["preflight_summary"]["held_count"] > 0
    assert all(value is False for value in packet["authority_locks"].values())


def test_migration_preflight_fails_closed_when_runner_authority_changes(monkeypatch) -> None:
    import core.continuity_namespace_migration_preflight as module

    original_read_json = module._read_json

    def _patched(path: Path):
        payload, status = original_read_json(path)
        if path == REPO_ROOT / MIGRATION_RUN_RECEIPT_PATH:
            payload = dict(payload)
            payload["authority_locks"] = {
                **payload.get("authority_locks", {}),
                "runtime_activation": True,
            }
        return payload, status

    monkeypatch.setattr(module, "_read_json", _patched)
    packet = module.build_continuity_namespace_migration_preflight_receipt(
        repo_root=REPO_ROOT
    )

    assert packet["status"] == DEGRADED_STATUS
    assert any(
        check["check_id"] == "continuity_namespace_migration_run_001.latest_authority_locks"
        and check["result"] == "HELD"
        for check in packet["preflight_checks"]
    )


def test_migration_preflight_runner_writes_receipt(tmp_path: Path) -> None:
    out_path = tmp_path / "receipt.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=out_path)
    written = json.loads(out_path.read_text(encoding="utf-8"))

    assert out_path.exists()
    assert written == packet
    assert written["status"] == STATUS
    assert DEFAULT_OUT_PATH.endswith(".latest.json")

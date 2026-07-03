from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.live_console_migration_runner_posture import (
    AUTHORITY_LOCKS,
    DEFAULT_OUT_PATH,
    PROJECTION_BUNDLE_PATH,
    STATUS,
    SUBSYSTEM_HEALTH_RECEIPT_PATH,
    build_live_console_migration_runner_posture_receipt,
    write_live_console_migration_runner_posture_receipt,
)
from Scripts.run_live_console_migration_runner_posture_receipt import run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_live_console_migration_runner_posture_receipt_contains_expected_sections() -> None:
    packet = build_live_console_migration_runner_posture_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert packet["canonical_source_path"] == SUBSYSTEM_HEALTH_RECEIPT_PATH
    assert packet["projection_bundle_path"] == PROJECTION_BUNDLE_PATH
    assert (
        packet["migration_runner_posture_summary"]["dashboard_posture"]["status"]
        == "CONTINUITY_NAMESPACE_MIGRATION_RUNNER_READY_ADVISORY_ONLY"
    )
    assert packet["migration_runner_posture_summary"]["live_visibility_ready"] is True


def test_live_console_migration_runner_posture_authority_locks_false() -> None:
    packet = build_live_console_migration_runner_posture_receipt(repo_root=REPO_ROOT)

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False
    assert packet["boundary"]["runtime_activation"] is False


def test_live_console_migration_runner_posture_canonical_hash_stable() -> None:
    packet = build_live_console_migration_runner_posture_receipt(repo_root=REPO_ROOT)
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    assert observed == canonical_hash(without_hash)
    assert (
        build_live_console_migration_runner_posture_receipt(repo_root=REPO_ROOT)[
            "canonical_hash"
        ]
        == observed
    )


def test_live_console_migration_runner_posture_runner_writes_receipt(
    tmp_path: Path,
) -> None:
    target = tmp_path / "live_console_migration_runner_posture_001.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=target)

    assert target.exists()
    assert packet["canonical_hash"]
    assert packet["status"] == STATUS


def test_live_console_migration_runner_posture_writer_preserves_hash(
    tmp_path: Path,
) -> None:
    target = tmp_path / "receipt.json"
    packet = build_live_console_migration_runner_posture_receipt(repo_root=REPO_ROOT)
    write_live_console_migration_runner_posture_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert DEFAULT_OUT_PATH in packet["validation_plan"][2]


def test_live_console_migration_runner_posture_fails_closed_when_dashboard_missing(
    monkeypatch,
) -> None:
    import core.live_console_migration_runner_posture as module

    real_load_json = module._load_json

    def _patched(path: Path):
        if path == REPO_ROOT / SUBSYSTEM_HEALTH_RECEIPT_PATH:
            return {}, "MISSING"
        return real_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    packet = module.build_live_console_migration_runner_posture_receipt(
        repo_root=REPO_ROOT
    )

    assert (
        packet["migration_runner_posture_summary"]["dashboard_posture"]["source_status"]
        == "MISSING"
    )
    assert packet["migration_runner_posture_summary"]["live_visibility_ready"] is False


def test_live_console_migration_runner_posture_fails_closed_when_bundle_missing(
    monkeypatch,
) -> None:
    import core.live_console_migration_runner_posture as module

    real_load_json = module._load_json

    def _patched(path: Path):
        if path == REPO_ROOT / PROJECTION_BUNDLE_PATH:
            return {}, "MISSING"
        return real_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    packet = module.build_live_console_migration_runner_posture_receipt(
        repo_root=REPO_ROOT
    )

    assert (
        packet["migration_runner_posture_summary"]["bundle_posture"]["source_status"]
        == "MISSING"
    )
    assert packet["migration_runner_posture_summary"]["live_visibility_ready"] is False

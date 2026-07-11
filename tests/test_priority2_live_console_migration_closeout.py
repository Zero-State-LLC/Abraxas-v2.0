from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.priority2_live_console_migration_closeout import (
    AUTHORITY_LOCKS,
    STATUS,
    build_priority2_live_console_migration_closeout_receipt,
    write_priority2_live_console_migration_closeout_receipt,
)
from scripts.run_priority2_live_console_migration_closeout_receipt import run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_closeout_receipt_contains_expected_sections() -> None:
    packet = build_priority2_live_console_migration_closeout_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["summary"]["documentation_only"] is True
    assert packet["lane_deliverables"]["authority_granted"] is False
    assert packet["current_route"]["start"] == "docs/status/SUBSYSTEM_HEALTH_DASHBOARD.md"


def test_closeout_receipt_authority_locks_are_false() -> None:
    packet = build_priority2_live_console_migration_closeout_receipt(repo_root=REPO_ROOT)

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["navigation_only"] is True


def test_closeout_receipt_canonical_hash_stable() -> None:
    packet = build_priority2_live_console_migration_closeout_receipt(repo_root=REPO_ROOT)
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    assert observed == canonical_hash(without_hash)
    assert (
        build_priority2_live_console_migration_closeout_receipt(
            repo_root=REPO_ROOT
        )["canonical_hash"]
        == observed
    )


def test_closeout_runner_writes_receipt(tmp_path: Path) -> None:
    target = tmp_path / "priority2_live_console_migration_closeout_001.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=target)

    assert target.exists()
    assert packet["status"] == STATUS
    assert packet["canonical_hash"]


def test_closeout_writer_preserves_hash(tmp_path: Path) -> None:
    target = tmp_path / "receipt.json"
    packet = build_priority2_live_console_migration_closeout_receipt(repo_root=REPO_ROOT)
    write_priority2_live_console_migration_closeout_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert "Slice61-Slice68" in packet["notion_closeout_text"]

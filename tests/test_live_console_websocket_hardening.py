from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.live_console_websocket_hardening import (
    AUTHORITY_LOCKS,
    DEFAULT_OUT_PATH,
    STATUS,
    build_live_console_websocket_hardening_receipt,
    write_live_console_websocket_hardening_receipt,
)
from scripts.run_live_console_websocket_hardening_receipt import run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_websocket_hardening_receipt_contains_expected_sections() -> None:
    packet = build_live_console_websocket_hardening_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert packet["transport_posture"]["retry_policy"]["strategy"] == "DETERMINISTIC_EXPONENTIAL_BACKOFF"
    assert packet["transport_posture"]["authority_granted"] is False
    assert "retry_delay_ms" in packet["transport_posture"]["diagnostics_fields"]


def test_websocket_hardening_receipt_authority_locks_false() -> None:
    packet = build_live_console_websocket_hardening_receipt(repo_root=REPO_ROOT)

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False


def test_websocket_hardening_receipt_canonical_hash_stable() -> None:
    packet = build_live_console_websocket_hardening_receipt(repo_root=REPO_ROOT)
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    assert observed == canonical_hash(without_hash)
    assert (
        build_live_console_websocket_hardening_receipt(repo_root=REPO_ROOT)["canonical_hash"]
        == observed
    )


def test_websocket_hardening_runner_writes_receipt(tmp_path: Path) -> None:
    target = tmp_path / "live_console_websocket_hardening_001.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=target)

    assert target.exists()
    assert packet["status"] == STATUS
    assert packet["canonical_hash"]


def test_websocket_hardening_writer_preserves_hash(tmp_path: Path) -> None:
    target = tmp_path / "receipt.json"
    packet = build_live_console_websocket_hardening_receipt(repo_root=REPO_ROOT)
    write_live_console_websocket_hardening_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert DEFAULT_OUT_PATH in packet["validation_plan"][1]

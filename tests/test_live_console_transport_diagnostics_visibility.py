from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.live_console_transport_diagnostics_visibility import (
    AUTHORITY_LOCKS,
    DEFAULT_OUT_PATH,
    STATUS,
    build_live_console_transport_diagnostics_visibility_receipt,
    write_live_console_transport_diagnostics_visibility_receipt,
)
from scripts.viz.run_live_console_transport_diagnostics_visibility_receipt import run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_transport_diagnostics_visibility_receipt_contains_expected_surface() -> None:
    packet = build_live_console_transport_diagnostics_visibility_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert packet["diagnostic_surface"]["panel"] == "TransportDiagnosticsPanel"
    assert packet["diagnostic_surface"]["display_only"] is True
    assert packet["diagnostic_surface"]["socket_control_authority"] is False
    assert "connection_retry_delay_ms" in packet["diagnostic_surface"]["source_fields"]


def test_transport_diagnostics_visibility_receipt_authority_locks_false() -> None:
    packet = build_live_console_transport_diagnostics_visibility_receipt(repo_root=REPO_ROOT)

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["socket_control_authority"] is False


def test_transport_diagnostics_visibility_receipt_canonical_hash_stable() -> None:
    packet = build_live_console_transport_diagnostics_visibility_receipt(repo_root=REPO_ROOT)
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    assert observed == canonical_hash(without_hash)
    assert (
        build_live_console_transport_diagnostics_visibility_receipt(repo_root=REPO_ROOT)[
            "canonical_hash"
        ]
        == observed
    )


def test_transport_diagnostics_visibility_runner_writes_receipt(tmp_path: Path) -> None:
    target = tmp_path / "live_console_transport_diagnostics_visibility_001.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=target)

    assert target.exists()
    assert packet["status"] == STATUS
    assert packet["canonical_hash"]


def test_transport_diagnostics_visibility_writer_preserves_hash(tmp_path: Path) -> None:
    target = tmp_path / "receipt.json"
    packet = build_live_console_transport_diagnostics_visibility_receipt(repo_root=REPO_ROOT)
    write_live_console_transport_diagnostics_visibility_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert DEFAULT_OUT_PATH in packet["validation_plan"][1]

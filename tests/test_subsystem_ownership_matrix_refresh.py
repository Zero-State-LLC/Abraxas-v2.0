from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.subsystem_ownership_matrix_refresh import (
    AUTHORITY_LOCKS,
    DEFAULT_OUT_PATH,
    STATUS,
    build_subsystem_ownership_matrix_markdown,
    build_subsystem_ownership_matrix_refresh_receipt,
    write_subsystem_ownership_matrix_refresh_receipt,
)
from Scripts.run_subsystem_ownership_matrix_refresh_receipt import run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_subsystem_ownership_matrix_receipt_has_repo_native_rows() -> None:
    packet = build_subsystem_ownership_matrix_refresh_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert packet["source_status"] == "READY_WITH_FINDINGS"
    assert packet["matrix_summary"]["subsystem_count"] >= 10
    assert packet["matrix_summary"]["missing_contract_count"] >= 1
    assert any(row["subsystem"] == "Oracle Signal Layer" for row in packet["ownership_rows"])
    assert any(row["subsystem"] == "AAL-Viz" for row in packet["ownership_rows"])


def test_subsystem_ownership_matrix_authority_locks_false() -> None:
    packet = build_subsystem_ownership_matrix_refresh_receipt(repo_root=REPO_ROOT)

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False
    assert packet["boundary"]["runtime_activation"] is False
    assert packet["boundary"]["canon_mutation"] is False
    assert packet["boundary"]["notion_writeback"] is False


def test_subsystem_ownership_matrix_canonical_hash_stable() -> None:
    packet = build_subsystem_ownership_matrix_refresh_receipt(repo_root=REPO_ROOT)
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    assert observed == canonical_hash(without_hash)
    assert build_subsystem_ownership_matrix_refresh_receipt(repo_root=REPO_ROOT)["canonical_hash"] == observed


def test_subsystem_ownership_matrix_runner_writes_receipt(tmp_path: Path) -> None:
    target = tmp_path / "subsystem_ownership_matrix_refresh_001.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=target)

    assert target.exists()
    assert packet["canonical_hash"]
    assert packet["status"] == STATUS


def test_subsystem_ownership_matrix_writer_preserves_hash(tmp_path: Path) -> None:
    target = tmp_path / "receipt.json"
    packet = build_subsystem_ownership_matrix_refresh_receipt(repo_root=REPO_ROOT)
    write_subsystem_ownership_matrix_refresh_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert DEFAULT_OUT_PATH in packet["validation_plan"][1]


def test_subsystem_ownership_matrix_markdown_includes_key_routes() -> None:
    markdown = build_subsystem_ownership_matrix_markdown(repo_root=REPO_ROOT)

    assert "# Subsystem Ownership Matrix" in markdown
    assert "Oracle Signal Layer" in markdown
    assert "AAL-Viz" in markdown
    assert "out/audit/subsystem_ownership_matrix_refresh_001.latest.json" in markdown

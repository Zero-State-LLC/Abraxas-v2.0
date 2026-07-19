from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.docs_navigation_refresh import (
    AUTHORITY_LOCKS,
    DEFAULT_OUT_PATH,
    STATUS,
    build_docs_navigation_refresh_receipt,
    write_docs_navigation_refresh_receipt,
)
from scripts.readiness.run_docs_navigation_refresh_receipt import run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_docs_navigation_refresh_receipt_has_required_routes() -> None:
    packet = build_docs_navigation_refresh_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert packet["source_status"] == "READY"
    assert packet["navigation_quality"]["missing_targets"] == []
    assert packet["navigation_quality"]["new_contributor_path_minutes"] == 5
    assert all(row["observed"] for row in packet["required_link_rows"])


def test_docs_navigation_refresh_authority_locks_false() -> None:
    packet = build_docs_navigation_refresh_receipt(repo_root=REPO_ROOT)

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False
    assert packet["boundary"]["runtime_activation"] is False
    assert packet["boundary"]["canon_mutation"] is False
    assert packet["boundary"]["notion_writeback"] is False


def test_docs_navigation_refresh_canonical_hash_stable() -> None:
    packet = build_docs_navigation_refresh_receipt(repo_root=REPO_ROOT)
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    assert observed == canonical_hash(without_hash)
    assert build_docs_navigation_refresh_receipt(repo_root=REPO_ROOT)[
        "canonical_hash"
    ] == observed


def test_docs_navigation_refresh_runner_writes_receipt(tmp_path: Path) -> None:
    target = tmp_path / "docs_navigation_refresh_001.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=target)

    assert target.exists()
    assert packet["canonical_hash"]
    assert packet["status"] == STATUS


def test_docs_navigation_refresh_writer_preserves_hash(tmp_path: Path) -> None:
    target = tmp_path / "receipt.json"
    packet = build_docs_navigation_refresh_receipt(repo_root=REPO_ROOT)
    write_docs_navigation_refresh_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert DEFAULT_OUT_PATH in packet["validation_plan"][1]

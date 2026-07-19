from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.canon_code_binding_audit import (
    AUTHORITY_LOCKS,
    DEFAULT_OUT_PATH,
    STATUS,
    WORK_ORDER,
    build_canon_code_binding_audit_receipt,
    write_canon_code_binding_audit_receipt,
)
from scripts.readiness.run_canon_code_binding_audit_receipt import run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_canon_code_binding_audit_maps_required_fields() -> None:
    packet = build_canon_code_binding_audit_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["work_order"] == WORK_ORDER
    assert packet["brier_score"] == "0.10"
    assert packet["coverage_summary"]["bound_count"] >= 6
    assert packet["coverage_summary"]["required_binding_count"] == len(
        packet["binding_rows"]
    )
    assert {row["subsystem"] for row in packet["binding_rows"]} >= {
        "repository_navigation",
        "artifact_registry_classifier",
        "continuity_namespace_migration_preflight",
        "live_console_migration_preflight_projection",
    }


def test_canon_code_binding_audit_authority_locks_false() -> None:
    packet = build_canon_code_binding_audit_receipt(repo_root=REPO_ROOT)

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["runtime_activation"] is False
    assert packet["boundary"]["canon_mutation"] is False
    assert packet["boundary"]["notion_writeback"] is False
    assert packet["boundary"]["queue_mutation"] is False


def test_canon_code_binding_audit_hash_stable() -> None:
    packet = build_canon_code_binding_audit_receipt(repo_root=REPO_ROOT)
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    assert observed == canonical_hash(without_hash)
    assert (
        build_canon_code_binding_audit_receipt(repo_root=REPO_ROOT)[
            "canonical_hash"
        ]
        == observed
    )


def test_canon_code_binding_audit_runner_writes_receipt(tmp_path: Path) -> None:
    target = tmp_path / "canon_code_binding_audit_001.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=target)

    assert target.exists()
    assert packet["canonical_hash"]
    assert packet["status"] == STATUS


def test_canon_code_binding_audit_writer_preserves_hash(tmp_path: Path) -> None:
    target = tmp_path / "receipt.json"
    packet = build_canon_code_binding_audit_receipt(repo_root=REPO_ROOT)
    write_canon_code_binding_audit_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert DEFAULT_OUT_PATH in packet["validation_plan"][1]

from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.continuity_namespace_migration_runner import (
    AUTHORITY_LOCKS,
    CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH,
    CONTINUITY_NAMESPACE_AUDIT_PATH,
    CONTINUITY_NAMESPACE_MIGRATION_PLAN_PATH,
    CONTINUITY_NAMESPACE_READINESS_REVIEW_PATH,
    CONTINUITY_NAMESPACE_STABILIZATION_RECEIPT_PATH,
    CONTINUITY_NAMESPACE_TOOLING_REFRESH_RECEIPT_PATH,
    DEFAULT_OUT_PATH,
    MIGRATION_RUN_ID,
    STATUS,
    build_continuity_namespace_migration_run_receipt,
    write_continuity_namespace_migration_run_receipt,
)
from scripts.temporal import run_continuity_namespace_migration_runner

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_migration_runner_receipt_contains_expected_sections() -> None:
    packet = build_continuity_namespace_migration_run_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["migration_run_id"] == MIGRATION_RUN_ID
    assert packet["brier_score"] == "0.10"
    assert packet["safe_next_surface"] == (
        "CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY"
    )
    assert packet["run_summary"]["selected_policy"] == (
        "D_HYBRID_CANONICAL_GLOBAL_IDS_WITH_BRANCH_LOCAL_ALIASES"
    )
    stage_ids = [row["stage_id"] for row in packet["run_stage_rows"]]
    assert stage_ids == [
        "START",
        "INVENTORY",
        "ALIAS_BINDING_SCAFFOLD",
        "ROUTE_REWRITE_SCAFFOLD",
        "RECEIPT_REBINDING_SCAFFOLD",
        "ROLLBACK_PATH",
        "FINAL_STATUS",
    ]


def test_migration_runner_authority_locks_false() -> None:
    packet = build_continuity_namespace_migration_run_receipt(repo_root=REPO_ROOT)

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False
    assert packet["boundary"]["runtime_activation"] is False
    assert packet["boundary"]["canon_mutation"] is False
    assert packet["boundary"]["notion_writeback"] is False


def test_migration_runner_canonical_hash_stable() -> None:
    packet = build_continuity_namespace_migration_run_receipt(repo_root=REPO_ROOT)
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    assert observed == canonical_hash(without_hash)
    assert (
        build_continuity_namespace_migration_run_receipt(repo_root=REPO_ROOT)[
            "canonical_hash"
        ]
        == observed
    )


def test_migration_runner_source_paths_present() -> None:
    packet = build_continuity_namespace_migration_run_receipt(repo_root=REPO_ROOT)
    source_rows = {row["path"]: row for row in packet["source_status_table"]}

    for path in (
        CONTINUITY_NAMESPACE_AUDIT_PATH,
        CONTINUITY_NAMESPACE_MIGRATION_PLAN_PATH,
        CONTINUITY_NAMESPACE_STABILIZATION_RECEIPT_PATH,
        CONTINUITY_NAMESPACE_READINESS_REVIEW_PATH,
        CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH,
        CONTINUITY_NAMESPACE_TOOLING_REFRESH_RECEIPT_PATH,
    ):
        assert source_rows[path]["source_status"] == "OBSERVED"


def test_migration_runner_execute_like_request_is_held() -> None:
    packet = build_continuity_namespace_migration_run_receipt(
        repo_root=REPO_ROOT,
        requested_mode="execute-like",
    )

    assert packet["requested_execution_posture"]["requested_mode"] == "execute-like"
    assert packet["requested_execution_posture"]["result"] == "HELD"
    assert packet["requested_execution_posture"]["effective_mode"] == "advisory"
    assert packet["run_stage_rows"][-1]["resulting_advisory_posture"] == "HELD"


def test_migration_runner_writer_preserves_hash(tmp_path: Path) -> None:
    target = tmp_path / "receipt.json"
    packet = build_continuity_namespace_migration_run_receipt(repo_root=REPO_ROOT)
    write_continuity_namespace_migration_run_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert DEFAULT_OUT_PATH in packet["validation_plan"][1]


def test_migration_runner_runner_writes_receipt(tmp_path: Path) -> None:
    target = tmp_path / "continuity_namespace_migration_run_001.latest.json"
    packet = run_continuity_namespace_migration_runner.run(
        repo_root=REPO_ROOT,
        output_path=target,
    )

    assert target.exists()
    assert packet["canonical_hash"]
    assert packet["status"] == STATUS


def test_migration_runner_fails_closed_when_alias_plan_missing(monkeypatch) -> None:
    import core.continuity_namespace_migration_runner as module

    original_load_json = module._load_json

    def _patched(path: Path):
        if path == REPO_ROOT / CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH:
            return {}, "MISSING"
        return original_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    packet = module.build_continuity_namespace_migration_run_receipt(repo_root=REPO_ROOT)

    assert packet["source_status"] == "READY_WITH_FINDINGS"
    assert packet["requested_execution_posture"]["result"] == "HELD"
    assert packet["run_summary"]["stack_ready"] is False


from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.continuity_namespace_migration_tooling_refresh import (
    AUTHORITY_LOCKS,
    CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH,
    CONTINUITY_NAMESPACE_READINESS_REVIEW_PATH,
    DEFAULT_OUT_PATH,
    STATUS,
    build_continuity_namespace_migration_tooling_refresh_receipt,
    write_continuity_namespace_migration_tooling_refresh_receipt,
)
from scripts.temporal.run_continuity_namespace_migration_tooling_refresh_receipt import run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_continuity_namespace_migration_tooling_refresh_receipt_contains_expected_routes() -> None:
    packet = build_continuity_namespace_migration_tooling_refresh_receipt(
        repo_root=REPO_ROOT
    )

    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert packet["readiness_status"] == "READY_FOR_ADDITIVE_ALIAS_PLAN"
    assert (
        packet["safe_next_surface"]
        == "CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY"
    )
    assert packet["alias_plan_status"] == "ADDITIVE_ALIAS_PLAN_EMITTED"
    assert packet["continuity_invariants"]["highest_observed_lane"] == "P102G"
    assert packet["continuity_invariants"]["lane_count"] == 58
    phases = {row["phase"] for row in packet["current_repo_migration_phase_rows"]}
    assert {
        "audit present",
        "migration plan present",
        "stabilization receipt present",
        "readiness review present",
        "additive alias plan present",
    } == phases


def test_continuity_namespace_migration_tooling_refresh_authority_locks_false() -> None:
    packet = build_continuity_namespace_migration_tooling_refresh_receipt(
        repo_root=REPO_ROOT
    )

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False
    assert packet["boundary"]["runtime_activation"] is False
    assert packet["boundary"]["canon_mutation"] is False
    assert packet["boundary"]["notion_writeback"] is False


def test_continuity_namespace_migration_tooling_refresh_canonical_hash_stable() -> None:
    packet = build_continuity_namespace_migration_tooling_refresh_receipt(
        repo_root=REPO_ROOT
    )
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    assert observed == canonical_hash(without_hash)
    assert (
        build_continuity_namespace_migration_tooling_refresh_receipt(
            repo_root=REPO_ROOT
        )["canonical_hash"]
        == observed
    )


def test_continuity_namespace_migration_tooling_refresh_runner_writes_receipt(
    tmp_path: Path,
) -> None:
    target = tmp_path / "continuity_namespace_migration_tooling_refresh_001.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=target)

    assert target.exists()
    assert packet["canonical_hash"]
    assert packet["status"] == STATUS


def test_continuity_namespace_migration_tooling_refresh_writer_preserves_hash(
    tmp_path: Path,
) -> None:
    target = tmp_path / "receipt.json"
    packet = build_continuity_namespace_migration_tooling_refresh_receipt(
        repo_root=REPO_ROOT
    )
    write_continuity_namespace_migration_tooling_refresh_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert DEFAULT_OUT_PATH in packet["validation_plan"][1]


def test_continuity_namespace_migration_tooling_refresh_fails_closed_when_alias_plan_missing(
    monkeypatch,
) -> None:
    import core.continuity_namespace_migration_tooling_refresh as module

    original_load_json = module._load_json

    def _patched(path: Path):
        if path == REPO_ROOT / CONTINUITY_NAMESPACE_ALIAS_PLAN_PATH:
            return {}, "MISSING"
        return original_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    packet = module.build_continuity_namespace_migration_tooling_refresh_receipt(
        repo_root=REPO_ROOT
    )

    assert packet["source_status"] == "READY_WITH_FINDINGS"
    assert packet["current_route_class"] == "NOT_COMPUTABLE / HELD"
    assert packet["alias_plan_status"] == "NOT_COMPUTABLE"
    assert any(
        finding["code"] == "ALIAS_PLAN_SOURCE_MISSING"
        for finding in packet["critical_unresolved_findings"]
    )


def test_continuity_namespace_migration_tooling_refresh_fails_closed_when_readiness_review_malformed(
    monkeypatch,
) -> None:
    import core.continuity_namespace_migration_tooling_refresh as module

    original_load_json = module._load_json

    def _patched(path: Path):
        if path == REPO_ROOT / CONTINUITY_NAMESPACE_READINESS_REVIEW_PATH:
            return {}, "NOT_COMPUTABLE"
        return original_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    packet = module.build_continuity_namespace_migration_tooling_refresh_receipt(
        repo_root=REPO_ROOT
    )

    assert packet["source_status"] == "READY_WITH_FINDINGS"
    assert packet["current_route_class"] == "NOT_COMPUTABLE / HELD"
    assert packet["readiness_status"] == "NOT_COMPUTABLE"
    assert packet["safe_next_surface"] == "NOT_COMPUTABLE"

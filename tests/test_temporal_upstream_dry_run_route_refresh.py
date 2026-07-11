from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.temporal_upstream_dry_run_route_refresh import (
    AUTHORITY_LOCKS,
    DEFAULT_OUT_PATH,
    P77_RECEIPT_PATH,
    STATUS,
    build_temporal_upstream_dry_run_route_refresh_receipt,
    write_temporal_upstream_dry_run_route_refresh_receipt,
)
from scripts.run_temporal_upstream_dry_run_route_refresh_receipt import run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_temporal_upstream_dry_run_route_refresh_contains_expected_routes() -> None:
    packet = build_temporal_upstream_dry_run_route_refresh_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert packet["dry_run_plan_status"] == "DRY_RUN_READY_WITH_MISSING_INPUTS"
    assert packet["safe_next_surface"] == "P78_TEMPORAL_CONTINUITY_UPSTREAM_INPUT_REGENERATION_EXECUTION_PLAN"
    assert packet["current_route_class"] == "ACTIVE NAVIGATION"
    stages = {row["stage"] for row in packet["route_stage_rows"]}
    assert {
        "P75_GENERATOR_DISCOVERY_PLAN",
        "P76_UPSTREAM_INPUT_RESTORATION_PLAN",
        "P77_UPSTREAM_INPUT_REGENERATION_DRY_RUN_PLAN",
    } == stages
    assert all(row["observed"] for row in packet["route_target_rows"])


def test_temporal_upstream_dry_run_route_refresh_authority_locks_false() -> None:
    packet = build_temporal_upstream_dry_run_route_refresh_receipt(repo_root=REPO_ROOT)

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False
    assert packet["boundary"]["runtime_activation"] is False
    assert packet["boundary"]["canon_mutation"] is False
    assert packet["boundary"]["notion_writeback"] is False


def test_temporal_upstream_dry_run_route_refresh_canonical_hash_stable() -> None:
    packet = build_temporal_upstream_dry_run_route_refresh_receipt(repo_root=REPO_ROOT)
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    assert observed == canonical_hash(without_hash)
    assert (
        build_temporal_upstream_dry_run_route_refresh_receipt(repo_root=REPO_ROOT)[
            "canonical_hash"
        ]
        == observed
    )


def test_temporal_upstream_dry_run_route_refresh_runner_writes_receipt(
    tmp_path: Path,
) -> None:
    target = tmp_path / "temporal_upstream_dry_run_route_refresh_001.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=target)

    assert target.exists()
    assert packet["canonical_hash"]
    assert packet["status"] == STATUS


def test_temporal_upstream_dry_run_route_refresh_writer_preserves_hash(
    tmp_path: Path,
) -> None:
    target = tmp_path / "receipt.json"
    packet = build_temporal_upstream_dry_run_route_refresh_receipt(repo_root=REPO_ROOT)
    write_temporal_upstream_dry_run_route_refresh_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert DEFAULT_OUT_PATH in packet["validation_plan"][1]


def test_temporal_upstream_dry_run_route_refresh_fails_closed_when_p77_missing(
    monkeypatch,
) -> None:
    import core.temporal_upstream_dry_run_route_refresh as module

    original_load_json = module._load_json

    def _patched(path: Path):
        if path == REPO_ROOT / P77_RECEIPT_PATH:
            return {}, "MISSING"
        return original_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    packet = module.build_temporal_upstream_dry_run_route_refresh_receipt(
        repo_root=REPO_ROOT
    )

    assert packet["source_status"] == "NOT_COMPUTABLE"
    assert packet["current_route_class"] == "NOT_COMPUTABLE / HELD"
    assert packet["safe_next_surface"] == "NOT_COMPUTABLE"

from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.continuity_lineage_map_refresh import (
    AUTHORITY_LOCKS,
    DEFAULT_OUT_PATH,
    STATUS,
    build_continuity_lineage_map_refresh_receipt,
    write_continuity_lineage_map_refresh_receipt,
)
from scripts.run_continuity_lineage_map_refresh_receipt import run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_continuity_lineage_map_refresh_receipt_contains_expected_routes() -> None:
    packet = build_continuity_lineage_map_refresh_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert packet["continuity_spine_summary"]["highest_observed_lane"] == "P102G"
    assert packet["continuity_spine_summary"]["lane_count"] >= 58
    spans = {row["span"] for row in packet["route_groups"]}
    assert {"P71-P76", "P77-P85", "P86-P101", "P102-P102G"} == spans
    blocked_edge_ids = {edge["edge_id"] for edge in packet["blocked_edges"]}
    assert "P74_RESTORATION_PENDING" in blocked_edge_ids
    assert "P85_EXECUTION_PLAN_BLOCKED" in blocked_edge_ids
    assert "P102G_HISTORICAL_RECOVERY_HELD" in blocked_edge_ids
    assert all(row["observed"] for row in packet["route_target_rows"])


def test_continuity_lineage_map_refresh_authority_locks_false() -> None:
    packet = build_continuity_lineage_map_refresh_receipt(repo_root=REPO_ROOT)

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False
    assert packet["boundary"]["runtime_activation"] is False
    assert packet["boundary"]["canon_mutation"] is False
    assert packet["boundary"]["notion_writeback"] is False


def test_continuity_lineage_map_refresh_canonical_hash_stable() -> None:
    packet = build_continuity_lineage_map_refresh_receipt(repo_root=REPO_ROOT)
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    assert observed == canonical_hash(without_hash)
    assert (
        build_continuity_lineage_map_refresh_receipt(repo_root=REPO_ROOT)[
            "canonical_hash"
        ]
        == observed
    )


def test_continuity_lineage_map_refresh_runner_writes_receipt(tmp_path: Path) -> None:
    target = tmp_path / "continuity_lineage_map_refresh_001.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=target)

    assert target.exists()
    assert packet["canonical_hash"]
    assert packet["status"] == STATUS


def test_continuity_lineage_map_refresh_writer_preserves_hash(tmp_path: Path) -> None:
    target = tmp_path / "receipt.json"
    packet = build_continuity_lineage_map_refresh_receipt(repo_root=REPO_ROOT)
    write_continuity_lineage_map_refresh_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert DEFAULT_OUT_PATH in packet["validation_plan"][1]


def test_continuity_lineage_map_refresh_fails_closed_when_spine_missing(
    monkeypatch,
) -> None:
    import core.continuity_lineage_map_refresh as module

    original_load_json = module._load_json

    def _patched(path: Path):
        if path.name == "continuity-spine.json":
            return {}, "MISSING"
        return original_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    packet = module.build_continuity_lineage_map_refresh_receipt(repo_root=REPO_ROOT)

    assert packet["source_status"] == "NOT_COMPUTABLE"
    assert packet["continuity_spine_summary"]["highest_observed_lane"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"

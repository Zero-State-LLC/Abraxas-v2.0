from __future__ import annotations

from pathlib import Path

from core.notion_p131_p133_stale_spec_reconciliation_packet import (
    build_notion_p131_p133_stale_spec_reconciliation_packet,
    write_notion_p131_p133_stale_spec_reconciliation_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_notion_reconciliation_packet_ready() -> None:
    packet = build_notion_p131_p133_stale_spec_reconciliation_packet(REPO_ROOT)
    assert packet["status"] == "NOTION_P131_P133_STALE_SPEC_RECONCILIATION_PACKET_READY"
    assert packet["notion_writeback_allowed"] is False
    assert packet["manual_operator_copy_paste_only"] is True
    assert len(packet["stale_lane_records"]) == 3
    p131 = next(
        rec for rec in packet["stale_lane_records"]
        if rec["notion_lane_id"].startswith("P131_")
    )
    assert p131["repo_authorization_observed"] is True
    assert "6/6" in p131["repo_truth"]
    p132 = next(
        rec for rec in packet["stale_lane_records"]
        if rec["notion_lane_id"].startswith("P132_")
    )
    assert "6/6" in p132["repo_truth"]
    p133 = next(
        rec for rec in packet["stale_lane_records"]
        if rec["notion_lane_id"].startswith("P133_")
    )
    assert p133["repo_authorization_observed"] is False


def test_notion_reconciliation_deterministic() -> None:
    first = build_notion_p131_p133_stale_spec_reconciliation_packet(REPO_ROOT)
    second = build_notion_p131_p133_stale_spec_reconciliation_packet(REPO_ROOT)
    assert first == second


def test_notion_reconciliation_writer(tmp_path: Path) -> None:
    out = tmp_path / "packet.json"
    packet = write_notion_p131_p133_stale_spec_reconciliation_packet(REPO_ROOT, out_path=out)
    assert out.exists()
    assert packet["sync_packet_hash"]

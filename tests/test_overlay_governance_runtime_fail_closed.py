from __future__ import annotations

from core.overlay_governance.runtime import run_overlay_governance_ledger


def _valid_inputs() -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    return (
        [{"overlay": {"deterministic_overlay_hash": "overlay-hash-1"}}],
        [{"fusion": {"deterministic_fusion_hash": "fusion-hash-1"}}],
        [{"schedule": {"deterministic_schedule_hash": "schedule-hash-1"}}],
        [{"candidate": {"deterministic_candidate_hash": "candidate-hash-1"}}],
    )


def test_empty_upstream_packets_fail_closed() -> None:
    packet = run_overlay_governance_ledger([{}], [{}], [{}], [{}])
    assert packet["status"] == "failed"
    assert packet["validator"]["status"] == "failed"
    assert packet["continuity"]["continuity_score"] == 0.0
    assert packet["operator_review"]["status"] == "pending"
    assert packet["events"] == []
    assert any(
        d.get("diagnostic_type") == "continuity_gap"
        and "missing upstream evidence" in d.get("diagnostic_message", "")
        for d in packet["diagnostics"]
    )
    assert all(
        event.get("source_packet_hash")
        not in {"canary", "obs", "sched", "promo", "unknown"}
        for event in packet["events"]
    )


def test_sentinel_source_hashes_are_rejected() -> None:
    packet = run_overlay_governance_ledger(
        [{"overlay": {"deterministic_overlay_hash": "canary"}}],
        [{"fusion": {"deterministic_fusion_hash": "obs"}}],
        [{"schedule": {"deterministic_schedule_hash": "sched"}}],
        [{"candidate": {"deterministic_candidate_hash": "promo"}}],
    )
    assert packet["status"] == "failed"
    assert packet["events"] == []


def test_valid_upstream_hashes_pass() -> None:
    canary, obs, sched, promo = _valid_inputs()
    packet = run_overlay_governance_ledger(canary, obs, sched, promo)
    assert packet["status"] == "passed"
    assert packet["operator_review"]["status"] == "approved"
    assert packet["continuity"]["continuity_score"] == 1.0
    assert [event["source_packet_hash"] for event in packet["events"]] == [
        "overlay-hash-1",
        "fusion-hash-1",
        "schedule-hash-1",
        "candidate-hash-1",
    ]


def test_runner_refuses_missing_upstream_fallback() -> None:
    source = (
        __import__("pathlib")
        .Path("scripts/viz/run_overlay_governance_ledger.py")
        .read_text(encoding="utf-8")
    )
    assert "return [{}]" not in source
    assert "refuse empty-packet fallback" in source


def test_partial_missing_upstream_fails_closed() -> None:
    canary, obs, sched, _promo = _valid_inputs()
    packet = run_overlay_governance_ledger(canary, obs, sched, [{}])
    assert packet["status"] == "failed"
    assert "promotion_reviewed" in packet["continuity"]["missing_event_types"]
    assert packet["operator_review"]["status"] == "pending"

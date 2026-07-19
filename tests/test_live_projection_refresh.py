from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from core.canonical.json import canonical_hash
from core.config import RuntimePaths
from core.generated_artifact_registry import (
    build_generated_artifact_registry,
    list_ci_drift_artifact_paths,
)
from core.live_projection_refresh import (
    NOT_COMPUTABLE,
    ProjectionRefreshScheduler,
    build_live_projection_refresh_packet,
    build_projection_continuity_receipt,
    build_projection_refresh_cycle,
    build_projection_refresh_ledger,
    build_projection_refresh_snapshot,
    build_refresh_markdown,
    check_refresh_drift,
    validate_snapshot_lineage,
    verify_projection_continuity,
)
from scripts.viz import run_live_projection_refresh


def _packet(value: int = 1) -> dict[str, object]:
    return {
        "schema": "RuntimeProjectionPacket.v1",
        "packet_id": "runtime_projection_test",
        "final_status": "ADVISORY_ONLY",
        "value": value,
    }


def _snapshot(*, refresh_id: str = "refresh_0", equivalent: bool = True) -> dict[str, object]:
    packet = _packet(value=1 if equivalent else 2)
    source_hash = canonical_hash(_packet(value=1))
    if equivalent:
        source_hash = canonical_hash(packet)
    return build_projection_refresh_snapshot(
        refresh_id=refresh_id,
        cycle_id="cycle_0",
        source_projection_hash=source_hash,
        refreshed_packet=packet,
        refresh_reason="scheduled_advisory",
        refresh_timestamp="ts_0",
        refresh_duration_ns=0,
    )


def _assert_hard_invariants(payload: dict[str, object]) -> None:
    assert payload["projection_only"] is True
    assert payload["advisory_only"] is True
    assert payload["analytics_only"] is True
    assert payload["detection_only"] is True
    assert payload["authority_granted"] is False
    assert payload["mutation_allowed"] is False
    assert payload["promotion_allowed"] is False
    assert payload["inference_authority"] is False
    assert payload["forecast_authority"] is False
    assert payload["execution_authority"] is False
    assert payload["command_channel"] is False
    assert payload["bidirectional_control"] is False
    assert payload["autonomous_adaptation"] is False


def test_snapshot_hash_stability() -> None:
    s1 = _snapshot(refresh_id="r0")
    s2 = _snapshot(refresh_id="r0")
    assert s1["snapshot_hash"] == s2["snapshot_hash"]


def test_cycle_hash_stability() -> None:
    c1 = build_projection_refresh_cycle(cycle_id="cycle_0", cycle_index=0, snapshots=[_snapshot()])
    c2 = build_projection_refresh_cycle(cycle_id="cycle_0", cycle_index=0, snapshots=[_snapshot()])
    assert c1["cycle_hash"] == c2["cycle_hash"]


def test_ledger_hash_stability() -> None:
    cycle = build_projection_refresh_cycle(cycle_id="cycle_0", cycle_index=0, snapshots=[_snapshot()])
    l1 = build_projection_refresh_ledger(ledger_id="ledger_0", cycles=[cycle])
    l2 = build_projection_refresh_ledger(ledger_id="ledger_0", cycles=[cycle])
    assert l1["ledger_hash"] == l2["ledger_hash"]


def test_continuity_receipt_stability() -> None:
    cycle = build_projection_refresh_cycle(cycle_id="cycle_0", cycle_index=0, snapshots=[_snapshot()])
    ledger = build_projection_refresh_ledger(ledger_id="ledger_0", cycles=[cycle])
    lineage = ledger["projection_lineage"]
    r1 = build_projection_continuity_receipt(
        receipt_id="receipt_0",
        ledger=ledger,
        source_packet_hash=str(lineage[0]),
        final_packet_hash=str(lineage[-1]),
    )
    r2 = build_projection_continuity_receipt(
        receipt_id="receipt_0",
        ledger=ledger,
        source_packet_hash=str(lineage[0]),
        final_packet_hash=str(lineage[-1]),
    )
    assert r1["receipt_hash"] == r2["receipt_hash"]


def test_packet_hash_stability() -> None:
    p1 = build_live_projection_refresh_packet(
        packet_id="live_projection_refresh_001",
        max_cycles=1,
        refresh_reasons=["scheduled_advisory"],
        timestamps=["live_projection_refresh_001_ts_0"],
        durations_ns=[0],
    )
    p2 = build_live_projection_refresh_packet(
        packet_id="live_projection_refresh_001",
        max_cycles=1,
        refresh_reasons=["scheduled_advisory"],
        timestamps=["live_projection_refresh_001_ts_0"],
        durations_ns=[0],
    )
    assert p1["packet_hash"] == p2["packet_hash"]
    assert p1["projection_id"] == p2["projection_id"]
    assert p1["projection_timestamp"] == p2["projection_timestamp"]


def test_snapshot_spine_compatibility_fields_present() -> None:
    packet = build_live_projection_refresh_packet(
        packet_id="live_projection_refresh_001",
        max_cycles=1,
        refresh_reasons=["scheduled_advisory"],
        timestamps=["live_projection_refresh_001_ts_0"],
        durations_ns=[0],
    )
    assert isinstance(packet["projection_id"], str)
    assert packet["projection_id"]
    assert isinstance(packet["projection_timestamp"], str)
    assert packet["projection_timestamp"] == "live_projection_refresh_001_ts_0"


def test_markdown_newline_stability() -> None:
    packet = build_live_projection_refresh_packet(
        timestamps=["live_projection_refresh_001_ts_0"], durations_ns=[0]
    )
    markdown = build_refresh_markdown(packet)
    assert markdown.endswith("\n")


def test_scheduler_deterministic_output() -> None:
    s1 = ProjectionRefreshScheduler(max_cycles=1)
    s2 = ProjectionRefreshScheduler(max_cycles=1)
    l1 = s1.run_refresh_loop(timestamps=["fixed_ts"], durations_ns=[0])
    l2 = s2.run_refresh_loop(timestamps=["fixed_ts"], durations_ns=[0])
    assert l1["ledger_hash"] == l2["ledger_hash"]


def test_scheduler_max_cycles_behavior() -> None:
    scheduler = ProjectionRefreshScheduler(max_cycles=2)
    scheduler.run_refresh_loop(timestamps=["fixed_ts"], durations_ns=[0])
    assert len(scheduler._cycles) == 2


def test_fail_closed_packet_build_behavior() -> None:
    with patch("core.live_projection_refresh.build_runtime_projection_packet", side_effect=RuntimeError("boom")):
        packet = build_live_projection_refresh_packet(timestamps=["fixed_ts"], durations_ns=[0])
    assert packet["final_status"] == NOT_COMPUTABLE


def test_not_computable_sentinel_behavior() -> None:
    scheduler = ProjectionRefreshScheduler(max_cycles=1)
    with patch("core.live_projection_refresh.build_runtime_projection_packet", side_effect=RuntimeError("boom")):
        ledger = scheduler.run_refresh_loop(timestamps=["fixed_ts"], durations_ns=[0])
    assert ledger["overall_continuity"] == NOT_COMPUTABLE
    assert NOT_COMPUTABLE in ledger["projection_lineage"]


def test_drift_detection_when_projection_equivalence_false() -> None:
    cycle = build_projection_refresh_cycle(
        cycle_id="cycle_0",
        cycle_index=0,
        snapshots=[_snapshot(equivalent=False)],
    )
    report = check_refresh_drift([cycle])
    assert report["drift_detected"] is True
    assert report["drift_event_count"] == 1


def test_no_drift_when_all_snapshots_equivalent() -> None:
    cycle = build_projection_refresh_cycle(
        cycle_id="cycle_0",
        cycle_index=0,
        snapshots=[_snapshot(equivalent=True), _snapshot(refresh_id="refresh_1", equivalent=True)],
    )
    report = check_refresh_drift([cycle])
    assert report["drift_detected"] is False
    assert report["drift_event_count"] == 0


def test_continuity_verification_rejects_not_computable_lineage_hashes() -> None:
    report = verify_projection_continuity(
        {
            "projection_lineage": [NOT_COMPUTABLE],
            "overall_continuity": "STABLE",
            "drift_summary": {},
        }
    )
    assert report["continuity_verified"] is False


def test_snapshot_lineage_validation_catches_missing_refresh_id() -> None:
    snapshot = _snapshot()
    snapshot["refresh_id"] = ""
    report = validate_snapshot_lineage([snapshot])
    assert report["lineage_valid"] is False
    assert any("missing_refresh_id" in violation for violation in report["violations"])


def test_snapshot_lineage_validation_catches_wrong_schema() -> None:
    snapshot = _snapshot()
    snapshot["schema"] = "WrongSchema"
    report = validate_snapshot_lineage([snapshot])
    assert report["lineage_valid"] is False
    assert any("wrong_schema" in violation for violation in report["violations"])


def test_all_hard_invariants_remain_locked() -> None:
    packet = build_live_projection_refresh_packet(
        timestamps=["live_projection_refresh_001_ts_0"], durations_ns=[0]
    )
    _assert_hard_invariants(packet)
    _assert_hard_invariants(packet["ledger"])
    _assert_hard_invariants(packet["continuity_receipt"])
    _assert_hard_invariants(packet["continuity_verification"])
    _assert_hard_invariants(packet["drift_report"])
    _assert_hard_invariants(packet["snapshot_lineage_validation"])
    _assert_hard_invariants(packet["aal_viz_refresh_cadence_extension"])


def test_artifact_registry_classifies_live_projection_refresh_as_derived_optional() -> None:
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    json_entry = next(
        entry
        for entry in registry.entries
        if entry.artifact_path == "out/projections/live_projection_refresh_001.latest.json"
    )
    md_entry = next(
        entry
        for entry in registry.entries
        if entry.artifact_path == "out/projections/live_projection_refresh_001.latest.md"
    )
    assert json_entry.determinism_class == "DERIVED_OPTIONAL"
    assert md_entry.determinism_class == "DERIVED_OPTIONAL"
    assert (
        "out/projections/live_projection_refresh_001.latest.json"
        not in list_ci_drift_artifact_paths(registry)
    )


def test_runner_writes_json_and_markdown_artifacts(tmp_path: Path) -> None:
    runtime_paths = RuntimePaths(contracts_dir=tmp_path / "contracts", out_dir=tmp_path / "out")
    with (
        patch.object(run_live_projection_refresh, "_PATHS", runtime_paths),
        patch.object(run_live_projection_refresh, "OUT_PATH", runtime_paths.live_projection_refresh_latest),
    ):
        run_live_projection_refresh.main()
    assert runtime_paths.live_projection_refresh_latest.exists()
    assert runtime_paths.live_projection_refresh_latest.with_suffix(".md").exists()
    json_payload = json.loads(runtime_paths.live_projection_refresh_latest.read_text(encoding="utf-8"))
    _assert_hard_invariants(json_payload)


def test_authority_mutation_forecast_execution_command_fields_never_true() -> None:
    packet = build_live_projection_refresh_packet(timestamps=["fixed_ts"], durations_ns=[0])

    def _assert_false_flags(payload: dict[str, object]) -> None:
        for field in (
            "authority_granted",
            "mutation_allowed",
            "forecast_authority",
            "execution_authority",
            "command_channel",
            "bidirectional_control",
            "autonomous_adaptation",
        ):
            assert payload[field] is False

    _assert_false_flags(packet)
    _assert_false_flags(packet["ledger"])
    _assert_false_flags(packet["continuity_receipt"])
    _assert_false_flags(packet["continuity_verification"])
    _assert_false_flags(packet["drift_report"])
    _assert_false_flags(packet["snapshot_lineage_validation"])
    _assert_false_flags(packet["aal_viz_refresh_cadence_extension"])


def test_compatibility_with_runtimepaths_live_projection_refresh_latest() -> None:
    path = RuntimePaths.from_env().live_projection_refresh_latest
    assert path.as_posix().endswith("out/projections/live_projection_refresh_001.latest.json")

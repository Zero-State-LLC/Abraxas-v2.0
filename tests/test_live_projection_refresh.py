"""Deterministic tests for PATCH-P14-LIVE-PROJECTION-REFRESH-LOOP-001.

Proves:
- refresh ordering stability
- stable snapshot lineage
- projection hash equivalence
- deterministic refresh packet generation
- projection continuity behavior
- missing-artifact handling
- authority/mutation/promotion false
- projection_only invariants
- no runtime/replay/canon mutation
"""

from __future__ import annotations

from typing import Any

from core.live_projection_refresh import (
    NOT_COMPUTABLE,
    PATCH_ID,
    ProjectionRefreshScheduler,
    build_aal_viz_refresh_cadence_extension,
    build_live_projection_refresh_packet,
    build_projection_continuity_receipt,
    build_projection_refresh_cycle,
    build_projection_refresh_ledger,
    build_projection_refresh_snapshot,
    check_refresh_drift,
    validate_snapshot_lineage,
    verify_projection_continuity,
)
from core.canonical.json import canonical_hash


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


def _make_base_packet() -> dict[str, Any]:
    """Return a minimal projection packet for hash testing."""
    return {
        "schema": "RuntimeProjectionPacket.v1",
        "patch_id": "PATCH-P13-AAL-VIZ-RUNTIME-PROJECTION-INTEGRATION-001",
        "packet_id": "test_packet",
        "value": 42,
        "final_posture": {"final_status": "ADVISORY_ONLY"},
    }


def _make_snapshot(
    *,
    refresh_id: str = "rid_001",
    cycle_id: str = "cid_001",
    source_hash: str | None = None,
    refreshed_packet: dict[str, Any] | None = None,
    refresh_reason: str = "manual_trigger",
    refresh_timestamp: str = "ts_001",
    refresh_duration_ns: int = 100,
    advisory_flags: list[str] | None = None,
    equivalent: bool = True,
) -> dict[str, Any]:
    base_pkt = _make_base_packet()
    if refreshed_packet is None:
        if equivalent:
            pkt = base_pkt
        else:
            # Different packet so hashes diverge
            pkt = {**base_pkt, "value": 99}
    else:
        pkt = refreshed_packet

    # When equivalent=True and no explicit source_hash, derive it from the
    # refreshed packet so projection_equivalence is True.
    # When equivalent=False and no explicit source_hash, derive it from the
    # base packet so the source differs from the refreshed packet.
    if source_hash is not None:
        effective_source_hash = source_hash
    elif equivalent:
        effective_source_hash = canonical_hash(pkt)
    else:
        effective_source_hash = canonical_hash(base_pkt)

    return build_projection_refresh_snapshot(
        refresh_id=refresh_id,
        cycle_id=cycle_id,
        source_projection_hash=effective_source_hash,
        refreshed_packet=pkt,
        refresh_reason=refresh_reason,
        refresh_timestamp=refresh_timestamp,
        refresh_duration_ns=refresh_duration_ns,
        advisory_flags=advisory_flags,
    )


# ---------------------------------------------------------------------------
# ProjectionRefreshSnapshot tests
# ---------------------------------------------------------------------------


class TestProjectionRefreshSnapshot:
    def test_schema(self) -> None:
        s = _make_snapshot()
        assert s["schema"] == "ProjectionRefreshSnapshot.v1"

    def test_patch_id(self) -> None:
        s = _make_snapshot()
        assert s["patch_id"] == PATCH_ID

    def test_authority_invariants(self) -> None:
        s = _make_snapshot()
        assert s["projection_only"] is True
        assert s["advisory_only"] is True
        assert s["authority_granted"] is False
        assert s["mutation_allowed"] is False
        assert s["promotion_allowed"] is False
        assert s["inference_authority"] is False

    def test_lineage_is_two_element_list(self) -> None:
        s = _make_snapshot()
        assert isinstance(s["projection_lineage"], list)
        assert len(s["projection_lineage"]) == 2

    def test_lineage_first_element_is_source(self) -> None:
        s = _make_snapshot(source_hash="my_source")
        assert s["projection_lineage"][0] == "my_source"

    def test_equivalence_when_same_hash(self) -> None:
        pkt = _make_base_packet()
        src = canonical_hash(pkt)
        s = build_projection_refresh_snapshot(
            refresh_id="rid",
            cycle_id="cid",
            source_projection_hash=src,
            refreshed_packet=pkt,
            refresh_reason="manual",
            refresh_timestamp="ts0",
            refresh_duration_ns=0,
        )
        assert s["projection_equivalence"] is True
        assert s["continuity_status"] == "EQUIVALENT"

    def test_divergence_when_different_hash(self) -> None:
        s = _make_snapshot(equivalent=False)
        assert s["projection_equivalence"] is False
        assert s["continuity_status"] == "DIVERGED"

    def test_snapshot_hash_stable(self) -> None:
        s1 = _make_snapshot()
        s2 = _make_snapshot()
        assert s1["snapshot_hash"] == s2["snapshot_hash"]

    def test_advisory_flags_sorted(self) -> None:
        s = _make_snapshot(advisory_flags=["z_flag", "a_flag"])
        assert s["advisory_flags"] == sorted(s["advisory_flags"])

    def test_refresh_id_present(self) -> None:
        s = _make_snapshot(refresh_id="test_rid_123")
        assert s["refresh_id"] == "test_rid_123"

    def test_refresh_duration_ns(self) -> None:
        s = _make_snapshot(refresh_duration_ns=12345)
        assert s["refresh_duration_ns"] == 12345


# ---------------------------------------------------------------------------
# ProjectionRefreshCycle tests
# ---------------------------------------------------------------------------


class TestProjectionRefreshCycle:
    def _two_snapshots(self) -> list[dict[str, Any]]:
        return [
            _make_snapshot(refresh_id="r1", cycle_id="c1"),
            _make_snapshot(refresh_id="r2", cycle_id="c1"),
        ]

    def test_schema(self) -> None:
        snaps = self._two_snapshots()
        c = build_projection_refresh_cycle(
            cycle_id="cid_001", cycle_index=0, snapshots=snaps
        )
        assert c["schema"] == "ProjectionRefreshCycle.v1"

    def test_snapshot_count(self) -> None:
        snaps = self._two_snapshots()
        c = build_projection_refresh_cycle(
            cycle_id="cid_001", cycle_index=0, snapshots=snaps
        )
        assert c["snapshot_count"] == 2

    def test_continuity_posture_stable_when_equivalent(self) -> None:
        snaps = self._two_snapshots()
        c = build_projection_refresh_cycle(
            cycle_id="cid_001", cycle_index=0, snapshots=snaps
        )
        assert c["continuity_posture"] == "STABLE"

    def test_continuity_posture_drifted_when_diverged(self) -> None:
        snaps = [
            _make_snapshot(refresh_id="r1"),
            _make_snapshot(refresh_id="r2", equivalent=False),
        ]
        c = build_projection_refresh_cycle(
            cycle_id="cid_001", cycle_index=0, snapshots=snaps
        )
        assert c["continuity_posture"] == "DRIFTED"
        assert c["drift_count"] == 1

    def test_cycle_hash_stable(self) -> None:
        snaps = self._two_snapshots()
        c1 = build_projection_refresh_cycle(
            cycle_id="cid_001", cycle_index=0, snapshots=snaps
        )
        c2 = build_projection_refresh_cycle(
            cycle_id="cid_001", cycle_index=0, snapshots=snaps
        )
        assert c1["cycle_hash"] == c2["cycle_hash"]

    def test_authority_invariants(self) -> None:
        c = build_projection_refresh_cycle(
            cycle_id="cid_001", cycle_index=0, snapshots=self._two_snapshots()
        )
        assert c["authority_granted"] is False
        assert c["mutation_allowed"] is False
        assert c["projection_only"] is True

    def test_total_duration_ns(self) -> None:
        snaps = [
            _make_snapshot(refresh_id="r1", refresh_duration_ns=100),
            _make_snapshot(refresh_id="r2", refresh_duration_ns=200),
        ]
        c = build_projection_refresh_cycle(
            cycle_id="cid_001", cycle_index=0, snapshots=snaps
        )
        assert c["total_duration_ns"] == 300

    def test_projection_lineage_chain(self) -> None:
        snap1 = _make_snapshot(refresh_id="r1")
        snap2 = _make_snapshot(refresh_id="r2")
        c = build_projection_refresh_cycle(
            cycle_id="cid_001", cycle_index=0, snapshots=[snap1, snap2]
        )
        assert isinstance(c["projection_lineage"], list)
        assert len(c["projection_lineage"]) >= 1


# ---------------------------------------------------------------------------
# ProjectionRefreshLedger tests
# ---------------------------------------------------------------------------


class TestProjectionRefreshLedger:
    def _make_cycle(self, cycle_index: int = 0) -> dict[str, Any]:
        snaps = [_make_snapshot(refresh_id=f"r_{cycle_index}")]
        return build_projection_refresh_cycle(
            cycle_id=f"cid_{cycle_index}",
            cycle_index=cycle_index,
            snapshots=snaps,
        )

    def test_schema(self) -> None:
        c = self._make_cycle()
        ledger = build_projection_refresh_ledger(
            ledger_id="ledger_001", cycles=[c]
        )
        assert ledger["schema"] == "ProjectionRefreshLedger.v1"

    def test_cycle_count(self) -> None:
        cycles = [self._make_cycle(i) for i in range(3)]
        ledger = build_projection_refresh_ledger(
            ledger_id="ledger_001", cycles=cycles
        )
        assert ledger["cycle_count"] == 3

    def test_overall_continuity_stable(self) -> None:
        c = self._make_cycle()
        ledger = build_projection_refresh_ledger(
            ledger_id="ledger_001", cycles=[c]
        )
        assert ledger["overall_continuity"] == "STABLE"

    def test_overall_continuity_drifted(self) -> None:
        snaps = [_make_snapshot(equivalent=False)]
        c = build_projection_refresh_cycle(
            cycle_id="cid_drifted", cycle_index=0, snapshots=snaps
        )
        ledger = build_projection_refresh_ledger(
            ledger_id="ledger_001", cycles=[c]
        )
        assert ledger["overall_continuity"] == "DRIFTED"

    def test_ledger_hash_stable(self) -> None:
        c = self._make_cycle()
        l1 = build_projection_refresh_ledger(ledger_id="ledger_001", cycles=[c])
        l2 = build_projection_refresh_ledger(ledger_id="ledger_001", cycles=[c])
        assert l1["ledger_hash"] == l2["ledger_hash"]

    def test_authority_invariants(self) -> None:
        ledger = build_projection_refresh_ledger(
            ledger_id="ledger_001", cycles=[self._make_cycle()]
        )
        assert ledger["authority_granted"] is False
        assert ledger["mutation_allowed"] is False
        assert ledger["projection_only"] is True
        assert ledger["advisory_only"] is True

    def test_drift_summary_keys(self) -> None:
        ledger = build_projection_refresh_ledger(
            ledger_id="ledger_001", cycles=[self._make_cycle()]
        )
        ds = ledger["drift_summary"]
        assert "total_drift_events" in ds
        assert "drift_rate" in ds
        assert "cycles_with_drift" in ds


# ---------------------------------------------------------------------------
# ProjectionContinuityReceipt tests
# ---------------------------------------------------------------------------


class TestProjectionContinuityReceipt:
    def _make_ledger(self, src: str, final: str) -> dict[str, Any]:
        snaps = [_make_snapshot(source_hash=src)]
        c = build_projection_refresh_cycle(
            cycle_id="cid_001", cycle_index=0, snapshots=snaps
        )
        raw = build_projection_refresh_ledger(ledger_id="ledger_001", cycles=[c])
        # Override lineage for predictable testing
        raw["projection_lineage"] = [src, final]
        raw["overall_continuity"] = "STABLE"
        return raw

    def test_schema(self) -> None:
        ledger = self._make_ledger("h_src", "h_final")
        r = build_projection_continuity_receipt(
            receipt_id="rcpt_001",
            ledger=ledger,
            source_packet_hash="h_src",
            final_packet_hash="h_final",
        )
        assert r["schema"] == "ProjectionContinuityReceipt.v1"

    def test_lineage_valid_when_matching(self) -> None:
        ledger = self._make_ledger("h_src", "h_final")
        r = build_projection_continuity_receipt(
            receipt_id="rcpt_001",
            ledger=ledger,
            source_packet_hash="h_src",
            final_packet_hash="h_final",
        )
        assert r["lineage_valid"] is True

    def test_lineage_invalid_when_mismatched(self) -> None:
        ledger = self._make_ledger("h_src", "h_final")
        r = build_projection_continuity_receipt(
            receipt_id="rcpt_001",
            ledger=ledger,
            source_packet_hash="h_WRONG",
            final_packet_hash="h_final",
        )
        assert r["lineage_valid"] is False

    def test_authority_invariants(self) -> None:
        ledger = self._make_ledger("h_src", "h_final")
        r = build_projection_continuity_receipt(
            receipt_id="rcpt_001",
            ledger=ledger,
            source_packet_hash="h_src",
            final_packet_hash="h_final",
        )
        assert r["authority_granted"] is False
        assert r["mutation_allowed"] is False
        assert r["projection_only"] is True

    def test_receipt_hash_stable(self) -> None:
        ledger = self._make_ledger("h_src", "h_final")
        r1 = build_projection_continuity_receipt(
            receipt_id="rcpt_001",
            ledger=ledger,
            source_packet_hash="h_src",
            final_packet_hash="h_final",
        )
        r2 = build_projection_continuity_receipt(
            receipt_id="rcpt_001",
            ledger=ledger,
            source_packet_hash="h_src",
            final_packet_hash="h_final",
        )
        assert r1["receipt_hash"] == r2["receipt_hash"]


# ---------------------------------------------------------------------------
# ProjectionRefreshScheduler tests
# ---------------------------------------------------------------------------


class TestProjectionRefreshScheduler:
    def test_plan_refresh_returns_cycle(self) -> None:
        sched = ProjectionRefreshScheduler(max_cycles=1)
        cycle = sched.plan_refresh(
            cycle_index=0,
            timestamps=["ts_0"],
            durations_ns=[0],
        )
        assert cycle["schema"] == "ProjectionRefreshCycle.v1"

    def test_run_refresh_loop_returns_ledger(self) -> None:
        sched = ProjectionRefreshScheduler(max_cycles=1)
        ledger = sched.run_refresh_loop(
            timestamps=["ts_0"],
            durations_ns=[0],
        )
        assert ledger["schema"] == "ProjectionRefreshLedger.v1"

    def test_refresh_ordering_stable(self) -> None:
        sched = ProjectionRefreshScheduler(max_cycles=2)
        sched.run_refresh_loop(
            timestamps=["ts_0"],
            durations_ns=[0],
        )
        cycles = sched._cycles
        assert cycles[0]["cycle_index"] == 0
        assert cycles[1]["cycle_index"] == 1

    def test_max_cycles_honored(self) -> None:
        sched = ProjectionRefreshScheduler(max_cycles=3)
        sched.run_refresh_loop(timestamps=["ts_0"], durations_ns=[0])
        assert len(sched._cycles) == 3

    def test_deterministic_across_runs(self) -> None:
        sched1 = ProjectionRefreshScheduler(max_cycles=1)
        l1 = sched1.run_refresh_loop(
            refresh_reasons=["manual"],
            timestamps=["ts_fixed"],
            durations_ns=[0],
        )
        sched2 = ProjectionRefreshScheduler(max_cycles=1)
        l2 = sched2.run_refresh_loop(
            refresh_reasons=["manual"],
            timestamps=["ts_fixed"],
            durations_ns=[0],
        )
        assert l1["ledger_hash"] == l2["ledger_hash"]

    def test_cycle_snapshots_have_authority_false(self) -> None:
        sched = ProjectionRefreshScheduler(max_cycles=1)
        sched.run_refresh_loop(timestamps=["ts_0"], durations_ns=[0])
        for cycle in sched._cycles:
            for snap in cycle.get("snapshots", []):
                assert snap["authority_granted"] is False
                assert snap["mutation_allowed"] is False
                assert snap["projection_only"] is True

    def test_missing_artifacts_produce_not_computable_gracefully(self) -> None:
        sched = ProjectionRefreshScheduler(
            max_cycles=1,
            source_artifact_paths={
                "runtime_performance_profile": "/nonexistent/path.json",
                "runtime_benchmark": "/nonexistent/path2.json",
                "incremental_replay": "/nonexistent/path3.json",
                "operator_console": "/nonexistent/path4.json",
            },
        )
        # Should not raise; missing artifacts produce NOT_COMPUTABLE internally
        ledger = sched.run_refresh_loop(timestamps=["ts_0"], durations_ns=[0])
        assert ledger["schema"] == "ProjectionRefreshLedger.v1"

    def test_no_runtime_mutation(self) -> None:
        """Scheduler never mutates runtime state — advisory only."""
        sched = ProjectionRefreshScheduler(max_cycles=1)
        ledger = sched.run_refresh_loop(timestamps=["ts_0"], durations_ns=[0])
        assert ledger["advisory_only"] is True
        assert ledger["authority_granted"] is False
        assert ledger["mutation_allowed"] is False
        assert ledger["promotion_allowed"] is False
        assert ledger["inference_authority"] is False


# ---------------------------------------------------------------------------
# Continuity verification tests
# ---------------------------------------------------------------------------


class TestVerifyProjectionContinuity:
    def _make_ledger(self, lineage: list[str], continuity: str) -> dict[str, Any]:
        return {
            "projection_lineage": lineage,
            "overall_continuity": continuity,
            "drift_summary": {"total_drift_events": 0, "drift_rate": 0.0},
        }

    def test_stable_lineage_verified(self) -> None:
        ledger = self._make_ledger(["h1", "h2"], "STABLE")
        v = verify_projection_continuity(ledger)
        assert v["continuity_verified"] is True
        assert v["overall_continuity"] == "STABLE"

    def test_drifted_lineage_still_verified(self) -> None:
        ledger = self._make_ledger(["h1", "h2"], "DRIFTED")
        v = verify_projection_continuity(ledger)
        assert v["continuity_verified"] is True
        assert v["overall_continuity"] == "DRIFTED"

    def test_empty_lineage_produces_blocker(self) -> None:
        ledger = self._make_ledger([], "STABLE")
        v = verify_projection_continuity(ledger)
        assert v["continuity_verified"] is False
        assert "continuity:empty_lineage" in v["continuity_blockers"]

    def test_not_computable_hash_produces_blocker(self) -> None:
        ledger = self._make_ledger([NOT_COMPUTABLE], "STABLE")
        v = verify_projection_continuity(ledger)
        assert v["continuity_verified"] is False

    def test_authority_invariants(self) -> None:
        ledger = self._make_ledger(["h1"], "STABLE")
        v = verify_projection_continuity(ledger)
        assert v["authority_granted"] is False
        assert v["projection_only"] is True


# ---------------------------------------------------------------------------
# Drift check tests
# ---------------------------------------------------------------------------


class TestCheckRefreshDrift:
    def test_no_drift_when_all_equivalent(self) -> None:
        snap = _make_snapshot()
        cycle = build_projection_refresh_cycle(
            cycle_id="cid", cycle_index=0, snapshots=[snap]
        )
        report = check_refresh_drift([cycle])
        assert report["drift_detected"] is False
        assert report["drift_event_count"] == 0

    def test_drift_detected_when_diverged(self) -> None:
        snap = _make_snapshot(equivalent=False)
        cycle = build_projection_refresh_cycle(
            cycle_id="cid", cycle_index=0, snapshots=[snap]
        )
        report = check_refresh_drift([cycle])
        assert report["drift_detected"] is True
        assert report["drift_event_count"] == 1

    def test_drift_rate_correct(self) -> None:
        s1 = _make_snapshot(refresh_id="r1")
        s2 = _make_snapshot(refresh_id="r2", equivalent=False)
        cycle = build_projection_refresh_cycle(
            cycle_id="cid", cycle_index=0, snapshots=[s1, s2]
        )
        report = check_refresh_drift([cycle])
        # 1 drift / 2 snapshots = 0.5
        assert report["drift_rate"] == 0.5

    def test_authority_invariants(self) -> None:
        report = check_refresh_drift([])
        assert report["authority_granted"] is False
        assert report["projection_only"] is True


# ---------------------------------------------------------------------------
# Snapshot lineage validation tests
# ---------------------------------------------------------------------------


class TestValidateSnapshotLineage:
    def test_valid_snapshots(self) -> None:
        snaps = [_make_snapshot(refresh_id="r1"), _make_snapshot(refresh_id="r2")]
        v = validate_snapshot_lineage(snaps)
        assert v["lineage_valid"] is True
        assert v["violations"] == []

    def test_wrong_schema_produces_violation(self) -> None:
        snap = _make_snapshot()
        snap["schema"] = "WrongSchema"
        v = validate_snapshot_lineage([snap])
        assert v["lineage_valid"] is False
        assert any("wrong_schema" in viol for viol in v["violations"])

    def test_empty_refresh_id_produces_violation(self) -> None:
        snap = _make_snapshot()
        snap["refresh_id"] = ""
        v = validate_snapshot_lineage([snap])
        assert v["lineage_valid"] is False

    def test_wrong_invariant_produces_violation(self) -> None:
        snap = _make_snapshot()
        snap["authority_granted"] = True  # violate invariant
        v = validate_snapshot_lineage([snap])
        assert v["lineage_valid"] is False
        assert any("authority_granted" in viol for viol in v["violations"])

    def test_authority_invariants_in_result(self) -> None:
        v = validate_snapshot_lineage([])
        assert v["authority_granted"] is False
        assert v["projection_only"] is True


# ---------------------------------------------------------------------------
# Top-level packet tests
# ---------------------------------------------------------------------------


class TestBuildLiveProjectionRefreshPacket:
    def _build(self, **kwargs: Any) -> dict[str, Any]:
        return build_live_projection_refresh_packet(
            packet_id="test_001",
            max_cycles=1,
            timestamps=["ts_fixed"],
            durations_ns=[0],
            **kwargs,
        )

    def test_schema(self) -> None:
        p = self._build()
        assert p["schema"] == "LiveProjectionRefreshPacket.v1"

    def test_patch_id(self) -> None:
        p = self._build()
        assert p["patch_id"] == PATCH_ID

    def test_authority_invariants(self) -> None:
        p = self._build()
        assert p["projection_only"] is True
        assert p["advisory_only"] is True
        assert p["authority_granted"] is False
        assert p["mutation_allowed"] is False
        assert p["promotion_allowed"] is False
        assert p["inference_authority"] is False

    def test_deterministic_across_runs(self) -> None:
        p1 = self._build()
        p2 = self._build()
        assert p1["packet_hash"] == p2["packet_hash"]

    def test_refresh_cycles_present(self) -> None:
        p = self._build()
        assert isinstance(p["refresh_cycles"], list)
        assert len(p["refresh_cycles"]) == 1

    def test_ledger_present(self) -> None:
        p = self._build()
        assert p["ledger"]["schema"] == "ProjectionRefreshLedger.v1"

    def test_continuity_receipt_present(self) -> None:
        p = self._build()
        assert p["continuity_receipt"]["schema"] == "ProjectionContinuityReceipt.v1"

    def test_drift_report_present(self) -> None:
        p = self._build()
        assert p["drift_report"]["schema"] == "ProjectionDriftReport.v1"

    def test_continuity_verification_present(self) -> None:
        p = self._build()
        assert p["continuity_verification"]["schema"] == "ProjectionContinuityVerification.v1"

    def test_lineage_validation_present(self) -> None:
        p = self._build()
        assert p["lineage_validation"]["schema"] == "SnapshotLineageValidation.v1"

    def test_refresh_cadence_summary_keys(self) -> None:
        p = self._build()
        cs = p["refresh_cadence_summary"]
        assert "refresh_cadence_status" in cs
        assert "snapshot_freshness" in cs
        assert "continuity_posture" in cs
        assert "projection_drift_posture" in cs
        assert "refresh_lineage_summary" in cs

    def test_missing_artifacts_handled_gracefully(self) -> None:
        p = build_live_projection_refresh_packet(
            packet_id="test_missing",
            max_cycles=1,
            source_artifact_paths={
                "runtime_performance_profile": "/nonexistent/a.json",
                "runtime_benchmark": "/nonexistent/b.json",
                "incremental_replay": "/nonexistent/c.json",
                "operator_console": "/nonexistent/d.json",
            },
            timestamps=["ts_0"],
            durations_ns=[0],
        )
        # Must not raise; must not fabricate state
        assert p["schema"] == "LiveProjectionRefreshPacket.v1"

    def test_projection_only_invariant_at_top_level(self) -> None:
        p = self._build()
        assert p["projection_only"] is True

    def test_final_status_is_advisory_or_blocked(self) -> None:
        p = self._build()
        assert p["final_status"] in ("ADVISORY_ONLY", "BLOCKED")

    def test_remaining_blockers_is_list(self) -> None:
        p = self._build()
        assert isinstance(p["remaining_blockers"], list)

    def test_no_promotion_allowed(self) -> None:
        p = self._build()
        assert p["promotion_allowed"] is False

    def test_no_inference_authority(self) -> None:
        p = self._build()
        assert p["inference_authority"] is False


# ---------------------------------------------------------------------------
# AAL-Viz refresh cadence extension tests
# ---------------------------------------------------------------------------


class TestAALVizRefreshCadenceExtension:
    def _make_ledger(self) -> dict[str, Any]:
        sched = ProjectionRefreshScheduler(max_cycles=1)
        return sched.run_refresh_loop(timestamps=["ts_0"], durations_ns=[0])

    def test_schema(self) -> None:
        ext = build_aal_viz_refresh_cadence_extension(self._make_ledger())
        assert ext["schema"] == "AALVizRefreshCadenceExtension.v1"

    def test_present_with_ledger(self) -> None:
        ext = build_aal_viz_refresh_cadence_extension(self._make_ledger())
        assert ext["status"] == "PRESENT"

    def test_not_computable_without_ledger(self) -> None:
        ext = build_aal_viz_refresh_cadence_extension(None)
        assert ext["status"] == NOT_COMPUTABLE

    def test_authority_invariants(self) -> None:
        ext = build_aal_viz_refresh_cadence_extension(self._make_ledger())
        assert ext["authority_granted"] is False
        assert ext["mutation_allowed"] is False
        assert ext["projection_only"] is True

    def test_refresh_cadence_status_present(self) -> None:
        ext = build_aal_viz_refresh_cadence_extension(self._make_ledger())
        assert "refresh_cadence_status" in ext

    def test_snapshot_freshness_fresh_when_snapshots_exist(self) -> None:
        ext = build_aal_viz_refresh_cadence_extension(self._make_ledger())
        assert ext["snapshot_freshness"] == "FRESH"

    def test_continuity_posture_present(self) -> None:
        ext = build_aal_viz_refresh_cadence_extension(self._make_ledger())
        assert ext["continuity_posture"] in ("STABLE", "DRIFTED")

    def test_refresh_lineage_summaries_keys(self) -> None:
        ext = build_aal_viz_refresh_cadence_extension(self._make_ledger())
        rls = ext["refresh_lineage_summaries"]
        assert "cycle_count" in rls
        assert "total_snapshots" in rls
        assert "lineage_length" in rls

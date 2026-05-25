"""Deterministic tests for PATCH-P13-AAL-VIZ-RUNTIME-PROJECTION-INTEGRATION-001.

Proves:
- packet shape stability
- deterministic node ordering
- stable replay topology projection
- stable benchmark aggregation
- projection_only invariants
- authority/mutation/promotion/inference_authority false
- missing artifact handling (NOT_COMPUTABLE, no fabrication)
- stable visualization hints
- no runtime/canon/replay mutation
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from core.aal_viz_runtime_projection import (
    NOT_COMPUTABLE,
    PATCH_ID,
    build_benchmark_trend_projection,
    build_projection_markdown,
    build_replay_topology_projection,
    build_runtime_health_projection,
    build_runtime_projection_packet,
    build_visualization_hints,
    write_runtime_projection_packet,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


def _make_replay_artifact() -> dict[str, Any]:
    return {
        "patch_id": "PATCH-P12-REPLAY-SCALING-AND-INCREMENTAL-EXECUTION-001",
        "plan_id": "plan_001",
        "graph_id": "graph_001",
        "replay_graph_hash": "abc123",
        "invalidated_nodes": ["node_b", "node_a", "node_c"],
        "skipped_surfaces": ["node_d", "node_e"],
        "replay_chunks": [
            {"chunk_id": "chunk_0000", "node_ids": ["node_a", "node_b", "node_c"]}
        ],
        "nodes": [
            {"node_id": "node_b", "dependencies": ["node_a"]},
            {"node_id": "node_a", "dependencies": []},
        ],
        "fail_closed": False,
        "replay_equivalence_verified": True,
        "final_status": "PASS",
        "remaining_blockers": [],
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


def _make_benchmark_artifact() -> dict[str, Any]:
    baseline = {
        "suite_id": "baseline",
        "surface": "registry",
        "run_count": 3,
        "duration_ns": {"mean": 2_000_000, "variance": 0, "min": 2_000_000, "max": 2_000_000},
        "cache": {"total_hits": 0, "total_misses": 0},
        "artifact_writes": 10,
        "replay_traversals": 20,
        "registry_loads": 1,
        "serialization_counts": 3,
        "output_hash_stable": True,
        "unique_output_hashes": ["h1"],
        "suite_hash": "sh_baseline",
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }
    optimized = {
        "suite_id": "optimized",
        "surface": "registry",
        "run_count": 3,
        "duration_ns": {"mean": 1_800_000, "variance": 0, "min": 1_800_000, "max": 1_800_000},
        "cache": {"total_hits": 5, "total_misses": 0},
        "artifact_writes": 4,
        "replay_traversals": 8,
        "registry_loads": 1,
        "serialization_counts": 3,
        "output_hash_stable": True,
        "unique_output_hashes": ["h1"],
        "suite_hash": "sh_optimized",
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }
    drift_report = {
        "schema": "RuntimeOptimizationDriftReport.v1",
        "report_id": "rpt_001",
        "surface": "registry",
        "baseline_suite_hash": "sh_baseline",
        "optimized_suite_hash": "sh_optimized",
        "performance_delta": {
            "delta_ns": -200_000,
            "delta_pct": -10.0,
            "baseline_mean_ns": 2_000_000,
            "optimized_mean_ns": 1_800_000,
        },
        "drift_detected": False,
        "detections": [],
        "advisory": {
            "output_hash_drift": False,
            "replay_divergence_detected": False,
            "cache_contamination_detected": False,
            "variance_spike_detected": False,
            "serialization_instability_detected": False,
            "artifact_ordering_drift_detected": False,
        },
        "report_hash": "rh_001",
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }
    return {
        "schema": "RuntimeBenchmarkArtifact.v1",
        "patch_id": "PATCH-P10-RUNTIME-BENCHMARK-AND-DRIFT-GUARD-001",
        "artifact_id": "runtime_benchmark_001",
        "baseline_suite": baseline,
        "optimized_suite": optimized,
        "drift_report": drift_report,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
    }


def _make_profile_artifact() -> dict[str, Any]:
    return {
        "patch_id": "PATCH-P8-RUNTIME-PERFORMANCE-PROFILING-001",
        "profile_enabled": True,
        "measured_surfaces": ["registry_generation"],
        "final_status": "PASS",
        "authority_granted": False,
        "mutation_allowed": False,
    }


def _make_console_artifact() -> dict[str, Any]:
    return {
        "patch_id": "PATCH-P11-OPERATOR-RUNTIME-CONSOLE-001",
        "packet_id": "operator_runtime_console_001",
        "final_status": "PASS",
        "remaining_blockers": [],
        "operator_next_actions": [
            "ADVISORY: No blocking issues found — console packet is projection-only"
        ],
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "projection_only": True,
        "advisory_only": True,
    }


def _make_operator_action_queue_artifact() -> dict[str, Any]:
    return {
        "operator_action_queue_status": "ADVISORY_ONLY",
        "operator_action_item_count": 4,
        "pending_approval_count": 4,
        "escalation_count": 2,
        "top_action_categories": ["drift_review", "render_blocker_review"],
        "queue_advisory_flags": ["advisory_only", "review_only"],
    }


def _make_read_only_transport_artifact() -> dict[str, Any]:
    return {
        "read_only_transport_status": "ADVISORY_ONLY",
        "transport_topic_count": 10,
        "transport_frame_count": 10,
        "transport_cursor_bounds": {"first": "cursor:a", "last": "cursor:b"},
        "transport_blocker_count": 1,
        "transport_advisory_flags": [
            "advisory_only",
            "deterministic_ordering",
            "read_only_transport",
            "transport_only",
        ],
        "final_status": "ADVISORY_ONLY",
    }


def _make_temporal_state_diff_artifact() -> dict[str, Any]:
    return {
        "temporal_state_diff_status": "ADVISORY_ONLY",
        "total_change_count": 12,
        "topology_change_count": 4,
        "lineage_shift_count": 2,
        "drift_acceleration_status": "DRIFT_ACCELERATING",
        "replay_equivalence_change_status": "SHIFT_DETECTED",
        "queue_delta_count": 3,
        "transport_delta_count": 5,
        "diff_advisory_flags": ["advisory_only", "diff_only", "detection_only"],
    }


def _make_temporal_topology_cartography_artifact() -> dict[str, Any]:
    return {
        "temporal_topology_cartography_status": "ADVISORY_ONLY",
        "atlas_region_count": 7,
        "atlas_corridor_count": 4,
        "stable_region_count": 2,
        "volatile_region_count": 1,
        "drift_zone_count": 2,
        "replay_corridor_count": 1,
        "continuity_corridor_count": 2,
        "topology_density_score": 0.55,
        "cartography_advisory_flags": [
            "advisory_only",
            "analytics_only",
            "cartography_only",
            "visualization_support_only",
        ],
    }


def _make_fusion_evidence_materialization_seal_artifact() -> dict[str, Any]:
    return {
        "schema_version": "FusionEvidenceMaterializationSealReceipt.v1",
        "seal_id": "fusion_evidence_materialization_seal_001",
        "status": "SEALED",
        "classification": "BLOCKER_FREE_ADVISORY_FUSION",
        "final_fusion_status": "ADVISORY_ONLY",
        "remaining_blockers": [],
        "drift_corridor_status": "ADVISORY_ONLY",
        "drift_evidence_count": 3,
        "lineage_corridor_status": "ADVISORY_ONLY",
        "lineage_evidence_count": 2,
        "receipt_hash": "seal_receipt_hash_001",
    }


# ---------------------------------------------------------------------------
# ReplayTopologyProjection tests
# ---------------------------------------------------------------------------


class TestReplayTopologyProjection:
    def test_schema(self) -> None:
        p = build_replay_topology_projection(_make_replay_artifact())
        assert p["schema"] == "ReplayTopologyProjection.v1"

    def test_nodes_sorted_deterministically(self) -> None:
        p = build_replay_topology_projection(_make_replay_artifact())
        assert p["nodes"] == sorted(p["nodes"])

    def test_skipped_surfaces_sorted(self) -> None:
        p = build_replay_topology_projection(_make_replay_artifact())
        assert p["skipped_surfaces"] == sorted(p["skipped_surfaces"])

    def test_edges_from_dependencies(self) -> None:
        p = build_replay_topology_projection(_make_replay_artifact())
        # node_b depends on node_a → edge source=node_a, target=node_b
        assert {"source": "node_a", "target": "node_b"} in p["edges"]

    def test_status_present(self) -> None:
        p = build_replay_topology_projection(_make_replay_artifact())
        assert p["status"] == "PRESENT"

    def test_missing_artifact_not_computable(self) -> None:
        p = build_replay_topology_projection(None)
        assert p["status"] == NOT_COMPUTABLE
        assert "reason" in p

    def test_authority_invariants(self) -> None:
        p = build_replay_topology_projection(_make_replay_artifact())
        assert p["projection_only"] is True
        assert p["advisory_only"] is True
        assert p["authority_granted"] is False
        assert p["mutation_allowed"] is False
        assert p["promotion_allowed"] is False
        assert p["inference_authority"] is False

    def test_missing_authority_invariants(self) -> None:
        p = build_replay_topology_projection(None)
        assert p["authority_granted"] is False
        assert p["mutation_allowed"] is False
        assert p["promotion_allowed"] is False

    def test_topology_hash_stable(self) -> None:
        a = _make_replay_artifact()
        p1 = build_replay_topology_projection(a)
        p2 = build_replay_topology_projection(a)
        assert p1["topology_hash"] == p2["topology_hash"]

    def test_equivalence_status_present(self) -> None:
        p = build_replay_topology_projection(_make_replay_artifact())
        eq = p["replay_equivalence_status"]
        assert eq["equivalence_verified"] is True
        assert eq["final_status"] == "PASS"

    def test_invalidation_lineage_present(self) -> None:
        p = build_replay_topology_projection(_make_replay_artifact())
        il = p["invalidation_lineage"]
        assert il["invalidated_count"] == 3
        assert il["fail_closed"] is False


# ---------------------------------------------------------------------------
# BenchmarkTrendProjection tests
# ---------------------------------------------------------------------------


class TestBenchmarkTrendProjection:
    def test_schema(self) -> None:
        p = build_benchmark_trend_projection(_make_benchmark_artifact())
        assert p["schema"] == "BenchmarkTrendProjection.v1"

    def test_status_present(self) -> None:
        p = build_benchmark_trend_projection(_make_benchmark_artifact())
        assert p["status"] == "PRESENT"

    def test_missing_artifact_not_computable(self) -> None:
        p = build_benchmark_trend_projection(None)
        assert p["status"] == NOT_COMPUTABLE
        assert "reason" in p

    def test_authority_invariants(self) -> None:
        p = build_benchmark_trend_projection(_make_benchmark_artifact())
        assert p["projection_only"] is True
        assert p["advisory_only"] is True
        assert p["authority_granted"] is False
        assert p["mutation_allowed"] is False
        assert p["promotion_allowed"] is False
        assert p["inference_authority"] is False

    def test_no_drift_detected(self) -> None:
        p = build_benchmark_trend_projection(_make_benchmark_artifact())
        assert p["drift_detected"] is False
        assert p["drift_detections"] == []

    def test_drift_detections_sorted(self) -> None:
        artifact = _make_benchmark_artifact()
        artifact["drift_report"]["drift_detected"] = True
        artifact["drift_report"]["detections"] = ["variance_spike", "cache_contamination"]
        p = build_benchmark_trend_projection(artifact)
        assert p["drift_detections"] == sorted(p["drift_detections"])

    def test_artifact_regeneration_reduction(self) -> None:
        p = build_benchmark_trend_projection(_make_benchmark_artifact())
        # baseline_writes=10, optimized_writes=4 → reduction = 1 - (4/10) = 0.6
        assert p["artifact_regeneration_reduction"] == 0.6

    def test_traversal_counts(self) -> None:
        p = build_benchmark_trend_projection(_make_benchmark_artifact())
        tc = p["traversal_counts"]
        assert tc["baseline_traversals"] == 20
        assert tc["optimized_traversals"] == 8
        assert tc["traversal_delta"] == -12

    def test_trend_hash_stable(self) -> None:
        a = _make_benchmark_artifact()
        p1 = build_benchmark_trend_projection(a)
        p2 = build_benchmark_trend_projection(a)
        assert p1["trend_hash"] == p2["trend_hash"]


# ---------------------------------------------------------------------------
# RuntimeHealthProjection tests
# ---------------------------------------------------------------------------


class TestRuntimeHealthProjection:
    def test_schema(self) -> None:
        p = build_runtime_health_projection(_make_profile_artifact(), _make_benchmark_artifact())
        assert p["schema"] == "RuntimeHealthProjection.v1"

    def test_health_healthy(self) -> None:
        p = build_runtime_health_projection(_make_profile_artifact(), _make_benchmark_artifact())
        assert p["health"] == "HEALTHY"

    def test_health_degraded_on_drift(self) -> None:
        bench = _make_benchmark_artifact()
        bench["drift_report"]["drift_detected"] = True
        p = build_runtime_health_projection(_make_profile_artifact(), bench)
        assert p["health"] == "DEGRADED"

    def test_health_degraded_on_profile_fail(self) -> None:
        profile = _make_profile_artifact()
        profile["final_status"] = "FAIL"
        p = build_runtime_health_projection(profile, _make_benchmark_artifact())
        assert p["health"] == "DEGRADED"

    def test_both_missing_not_computable(self) -> None:
        p = build_runtime_health_projection(None, None)
        assert p["health"] == NOT_COMPUTABLE

    def test_authority_invariants(self) -> None:
        p = build_runtime_health_projection(_make_profile_artifact(), _make_benchmark_artifact())
        assert p["projection_only"] is True
        assert p["advisory_only"] is True
        assert p["authority_granted"] is False
        assert p["mutation_allowed"] is False
        assert p["promotion_allowed"] is False
        assert p["inference_authority"] is False

    def test_health_hash_stable(self) -> None:
        p1 = build_runtime_health_projection(_make_profile_artifact(), _make_benchmark_artifact())
        p2 = build_runtime_health_projection(_make_profile_artifact(), _make_benchmark_artifact())
        assert p1["health_hash"] == p2["health_hash"]

    def test_profile_summary_present(self) -> None:
        p = build_runtime_health_projection(_make_profile_artifact(), None)
        assert p["profile_summary"]["status"] == "PRESENT"
        assert p["profile_summary"]["final_status"] == "PASS"

    def test_benchmark_summary_not_computable(self) -> None:
        p = build_runtime_health_projection(None, None)
        assert p["benchmark_summary"]["status"] == NOT_COMPUTABLE


# ---------------------------------------------------------------------------
# VisualizationHints tests
# ---------------------------------------------------------------------------


class TestVisualizationHints:
    def _make_topology(self) -> dict[str, Any]:
        return build_replay_topology_projection(_make_replay_artifact())

    def _make_bench(self) -> dict[str, Any]:
        return build_benchmark_trend_projection(_make_benchmark_artifact())

    def _make_health(self) -> dict[str, Any]:
        return build_runtime_health_projection(_make_profile_artifact(), _make_benchmark_artifact())

    def test_schema(self) -> None:
        h = build_visualization_hints(self._make_topology(), self._make_bench(), self._make_health())
        assert h["schema"] == "AALVizVisualizationHints.v1"

    def test_advisory_only(self) -> None:
        h = build_visualization_hints(self._make_topology(), self._make_bench(), self._make_health())
        assert h["advisory_only"] is True

    def test_hints_sorted(self) -> None:
        h = build_visualization_hints(self._make_topology(), self._make_bench(), self._make_health())
        assert h["hints"] == sorted(h["hints"])

    def test_hints_stable(self) -> None:
        h1 = build_visualization_hints(self._make_topology(), self._make_bench(), self._make_health())
        h2 = build_visualization_hints(self._make_topology(), self._make_bench(), self._make_health())
        assert h1["hints"] == h2["hints"]

    def test_healthy_hint_present(self) -> None:
        h = build_visualization_hints(self._make_topology(), self._make_bench(), self._make_health())
        assert any("runtime_healthy" in hint for hint in h["hints"])

    def test_not_computable_topology_hint(self) -> None:
        topo = build_replay_topology_projection(None)
        h = build_visualization_hints(topo, self._make_bench(), self._make_health())
        assert any("replay_topology_unavailable" in hint for hint in h["hints"])

    def test_drift_hint_present_on_drift(self) -> None:
        bench = _make_benchmark_artifact()
        bench["drift_report"]["drift_detected"] = True
        bench["drift_report"]["detections"] = ["variance_spike"]
        bt = build_benchmark_trend_projection(bench)
        h = build_visualization_hints(self._make_topology(), bt, self._make_health())
        assert any("variance_spike" in hint for hint in h["hints"])

    def test_equivalence_verified_hint(self) -> None:
        h = build_visualization_hints(self._make_topology(), self._make_bench(), self._make_health())
        assert any("replay_equivalence_verified" in hint for hint in h["hints"])

    def test_hint_count_matches(self) -> None:
        h = build_visualization_hints(self._make_topology(), self._make_bench(), self._make_health())
        assert h["hint_count"] == len(h["hints"])


# ---------------------------------------------------------------------------
# RuntimeProjectionPacket (top-level) tests
# ---------------------------------------------------------------------------


class TestRuntimeProjectionPacket:
    def _build_with_mocks(
        self,
        profile_data: dict[str, Any] | None = None,
        benchmark_data: dict[str, Any] | None = None,
        replay_data: dict[str, Any] | None = None,
        console_data: dict[str, Any] | None = None,
        operator_action_queue_data: dict[str, Any] | None = None,
        read_only_transport_data: dict[str, Any] | None = None,
        temporal_state_diff_data: dict[str, Any] | None = None,
        temporal_topology_cartography_data: dict[str, Any] | None = None,
        fusion_evidence_materialization_seal_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        side_effects = {
            "out/audit/runtime_performance_profile_001.latest.json": profile_data,
            "out/audit/runtime_benchmark_001.latest.json": benchmark_data,
            "out/audit/incremental_replay_001.latest.json": replay_data,
            "out/audit/operator_runtime_console_001.latest.json": console_data,
            "out/audit/operator_action_queue_001.latest.json": operator_action_queue_data,
            "out/projections/projection_chronoscope_001.latest.json": None,
            "out/projections/aal_viz_graph_render_packet_001.latest.json": None,
            "out/projections/read_only_transport_001.latest.json": read_only_transport_data,
            "out/projections/temporal_state_diff_001.latest.json": temporal_state_diff_data,
            "out/projections/temporal_topology_cartography_001.latest.json": temporal_topology_cartography_data,
            "out/audit/fusion_evidence_materialization_seal_001.latest.json": fusion_evidence_materialization_seal_data,
        }

        def mock_load(path: Any) -> dict[str, Any] | None:
            return side_effects.get(str(path))

        with patch(
            "core.aal_viz_runtime_projection._load_artifact", side_effect=mock_load
        ):
            return build_runtime_projection_packet()

    def test_schema(self) -> None:
        p = self._build_with_mocks()
        assert p["schema"] == "RuntimeProjectionPacket.v1"

    def test_patch_id(self) -> None:
        p = self._build_with_mocks()
        assert p["patch_id"] == PATCH_ID

    def test_projection_only_invariant(self) -> None:
        p = self._build_with_mocks()
        assert p["projection_only"] is True

    def test_advisory_only_invariant(self) -> None:
        p = self._build_with_mocks()
        assert p["advisory_only"] is True

    def test_authority_granted_false(self) -> None:
        p = self._build_with_mocks()
        assert p["authority_granted"] is False

    def test_mutation_allowed_false(self) -> None:
        p = self._build_with_mocks()
        assert p["mutation_allowed"] is False

    def test_promotion_allowed_false(self) -> None:
        p = self._build_with_mocks()
        assert p["promotion_allowed"] is False

    def test_inference_authority_false(self) -> None:
        p = self._build_with_mocks()
        assert p["inference_authority"] is False

    def test_all_missing_artifacts_blocked(self) -> None:
        p = self._build_with_mocks()
        # With all artifacts missing, final_status should be BLOCKED
        assert p["final_status"] == "BLOCKED"

    def test_remaining_blockers_listed(self) -> None:
        p = self._build_with_mocks()
        assert isinstance(p["remaining_blockers"], list)
        # With artifacts missing, blockers should mention them
        assert len(p["remaining_blockers"]) > 0

    def test_remaining_blockers_sorted(self) -> None:
        p = self._build_with_mocks()
        assert p["remaining_blockers"] == sorted(p["remaining_blockers"])

    def test_full_artifacts_pass(self) -> None:
        p = self._build_with_mocks(
            profile_data=_make_profile_artifact(),
            benchmark_data=_make_benchmark_artifact(),
            replay_data=_make_replay_artifact(),
            console_data=_make_console_artifact(),
        )
        assert p["final_status"] == "PASS"
        assert p["remaining_blockers"] == []

    def test_packet_deterministic(self) -> None:
        p1 = self._build_with_mocks(
            profile_data=_make_profile_artifact(),
            benchmark_data=_make_benchmark_artifact(),
            replay_data=_make_replay_artifact(),
            console_data=_make_console_artifact(),
        )
        p2 = self._build_with_mocks(
            profile_data=_make_profile_artifact(),
            benchmark_data=_make_benchmark_artifact(),
            replay_data=_make_replay_artifact(),
            console_data=_make_console_artifact(),
        )
        # projection_id and all derived fields must be equal
        assert p1["projection_id"] == p2["projection_id"]
        assert p1["replay_topology"]["topology_hash"] == p2["replay_topology"]["topology_hash"]
        assert p1["benchmark_trends"]["trend_hash"] == p2["benchmark_trends"]["trend_hash"]

    def test_sub_projection_schemas_present(self) -> None:
        p = self._build_with_mocks(
            profile_data=_make_profile_artifact(),
            benchmark_data=_make_benchmark_artifact(),
            replay_data=_make_replay_artifact(),
            console_data=_make_console_artifact(),
        )
        assert p["replay_topology"]["schema"] == "ReplayTopologyProjection.v1"
        assert p["benchmark_trends"]["schema"] == "BenchmarkTrendProjection.v1"
        assert p["runtime_health"]["schema"] == "RuntimeHealthProjection.v1"
        assert p["visualization_hints"]["schema"] == "AALVizVisualizationHints.v1"

    def test_authority_boundary_summary(self) -> None:
        p = self._build_with_mocks()
        ab = p["authority_boundary_summary"]
        assert ab["projection_only"] is True
        assert ab["authority_granted"] is False
        assert ab["mutation_allowed"] is False
        assert ab["promotion_allowed"] is False
        assert ab["inference_authority"] is False

    def test_source_artifacts_present(self) -> None:
        p = self._build_with_mocks()
        sa = p["source_artifacts"]
        assert "runtime_performance_profile" in sa
        assert "runtime_benchmark" in sa
        assert "incremental_replay" in sa
        assert "operator_console" in sa
        assert "operator_action_queue" in sa
        assert "projection_bus" in sa
        assert "temporal_snapshot_spine" in sa
        assert "projection_chronoscope" in sa
        assert "graph_render_packet" in sa
        assert "read_only_transport" in sa
        assert "temporal_state_diff" in sa
        assert "fusion_evidence_materialization_seal" in sa

    def test_sealed_fusion_evidence_summary_missing_non_breaking(self) -> None:
        p = self._build_with_mocks()
        summary = p["sealed_fusion_evidence_summary"]
        assert summary["status"] == NOT_COMPUTABLE
        assert summary["summary_blockers"] == [
            "missing_artifact:out/audit/fusion_evidence_materialization_seal_001.latest.json"
        ]
        assert summary["advisory_only"] is True
        assert summary["projection_only"] is True
        assert summary["authority_granted"] is False
        assert summary["forecast_authority"] is False
        assert summary["mutation_allowed"] is False

    def test_sealed_fusion_evidence_summary_present_deterministic(self) -> None:
        p1 = self._build_with_mocks(
            fusion_evidence_materialization_seal_data=_make_fusion_evidence_materialization_seal_artifact()
        )
        p2 = self._build_with_mocks(
            fusion_evidence_materialization_seal_data=_make_fusion_evidence_materialization_seal_artifact()
        )
        s1 = p1["sealed_fusion_evidence_summary"]
        s2 = p2["sealed_fusion_evidence_summary"]
        assert s1["status"] == "PRESENT"
        assert s1["seal_status"] == "SEALED"
        assert s1["classification"] == "BLOCKER_FREE_ADVISORY_FUSION"
        assert s1["fusion_final_status"] == "ADVISORY_ONLY"
        assert s1["remaining_blocker_count"] == 0
        assert s1["drift_corridor_status"] == "ADVISORY_ONLY"
        assert s1["drift_evidence_count"] == 3
        assert s1["lineage_corridor_status"] == "ADVISORY_ONLY"
        assert s1["lineage_evidence_count"] == 2
        assert s1["seal_receipt_hash"] == "seal_receipt_hash_001"
        assert s1["source_artifact_path"] == "out/audit/fusion_evidence_materialization_seal_001.latest.json"
        assert s1["summary_hash"] == s2["summary_hash"]
        assert s1["source_artifact_hash"] == s2["source_artifact_hash"]

    def test_projection_bus_summary_fields_present(self) -> None:
        p = self._build_with_mocks()
        assert p["projection_bus_status"] == NOT_COMPUTABLE
        assert p["snapshot_index_status"] == NOT_COMPUTABLE
        assert p["cursor_bounds"] == {"first": None, "last": None}
        assert p["temporal_window_count"] == 0
        assert p["lineage_gap_count"] == 0
        assert p["projection_bus_advisory_flags"] == []
        assert p["chronoscope_status"] == NOT_COMPUTABLE
        assert p["timeline_point_count"] == 0
        assert p["playback_cursor_bounds"] == {"first": None, "last": None}
        assert p["drift_timeline_status"] == NOT_COMPUTABLE
        assert p["lineage_evolution_status"] == NOT_COMPUTABLE
        assert p["chronoscope_advisory_flags"] == []
        assert p["graph_render_packet_status"] == NOT_COMPUTABLE
        assert p["render_node_count"] == 0
        assert p["render_edge_count"] == 0
        assert p["render_layer_count"] == 0
        assert p["render_overlay_count"] == 0
        assert p["render_blocker_count"] == 0
        assert p["render_advisory_flags"] == []
        assert p["operator_action_queue_status"] == NOT_COMPUTABLE
        assert p["operator_action_item_count"] == 0
        assert p["pending_approval_count"] == 0
        assert p["escalation_count"] == 0
        assert p["top_action_categories"] == []
        assert p["queue_advisory_flags"] == [
            "advisory_only",
            "deterministic_ordering",
            "fail_closed",
            "no_auto_approve",
            "no_auto_execute",
            "no_execution_authority",
            "no_mutation_authority",
            "review_only",
        ]
        assert p["read_only_transport_status"] == NOT_COMPUTABLE
        assert p["transport_topic_count"] == 0
        assert p["transport_frame_count"] == 0
        assert p["transport_cursor_bounds"] == {"first": None, "last": None}
        assert p["transport_blocker_count"] == 0
        assert p["transport_advisory_flags"] == []
        assert p["temporal_state_diff_status"] == NOT_COMPUTABLE
        assert p["total_change_count"] == 0
        assert p["topology_change_count"] == 0
        assert p["lineage_shift_count"] == 0
        assert p["drift_acceleration_status"] == NOT_COMPUTABLE
        assert p["replay_equivalence_change_status"] == NOT_COMPUTABLE
        assert p["queue_delta_count"] == 0
        assert p["transport_delta_count"] == 0
        assert p["diff_advisory_flags"] == []
        assert p["temporal_topology_cartography_status"] == NOT_COMPUTABLE
        assert p["atlas_region_count"] == 0
        assert p["atlas_corridor_count"] == 0
        assert p["stable_region_count"] == 0
        assert p["volatile_region_count"] == 0
        assert p["drift_zone_count"] == 0
        assert p["replay_corridor_count"] == 0
        assert p["continuity_corridor_count"] == 0
        assert p["topology_density_score"] == 0.0
        assert p["cartography_advisory_flags"] == []
        assert p["temporal_stability_pressure_status"] == NOT_COMPUTABLE
        assert p["aggregate_stress_score"] == 0.0
        assert p["pressure_zone_count"] == 0

    def test_operator_action_queue_summary_fields_present(self) -> None:
        p = self._build_with_mocks(
            profile_data=_make_profile_artifact(),
            benchmark_data=_make_benchmark_artifact(),
            replay_data=_make_replay_artifact(),
            console_data=_make_console_artifact(),
            operator_action_queue_data=_make_operator_action_queue_artifact(),
            read_only_transport_data=_make_read_only_transport_artifact(),
            temporal_state_diff_data=_make_temporal_state_diff_artifact(),
            temporal_topology_cartography_data=_make_temporal_topology_cartography_artifact(),
        )
        assert p["operator_action_queue_status"] == "ADVISORY_ONLY"
        assert p["operator_action_item_count"] == 4
        assert p["pending_approval_count"] == 4
        assert p["escalation_count"] == 2
        assert p["top_action_categories"] == [
            "drift_review",
            "render_blocker_review",
        ]
        assert p["read_only_transport_status"] == "ADVISORY_ONLY"
        assert p["transport_topic_count"] == 10
        assert p["transport_frame_count"] == 10
        assert p["transport_cursor_bounds"] == {"first": "cursor:a", "last": "cursor:b"}
        assert p["transport_blocker_count"] == 1
        assert p["transport_advisory_flags"] == [
            "advisory_only",
            "deterministic_ordering",
            "read_only_transport",
            "transport_only",
        ]
        assert p["temporal_state_diff_status"] == "ADVISORY_ONLY"
        assert p["total_change_count"] == 12
        assert p["topology_change_count"] == 4
        assert p["lineage_shift_count"] == 2
        assert p["drift_acceleration_status"] == "DRIFT_ACCELERATING"
        assert p["replay_equivalence_change_status"] == "SHIFT_DETECTED"
        assert p["queue_delta_count"] == 3
        assert p["transport_delta_count"] == 5
        assert p["diff_advisory_flags"] == [
            "advisory_only",
            "detection_only",
            "diff_only",
        ]
        assert p["temporal_topology_cartography_status"] == "ADVISORY_ONLY"
        assert p["atlas_region_count"] == 7
        assert p["atlas_corridor_count"] == 4
        assert p["stable_region_count"] == 2
        assert p["volatile_region_count"] == 1
        assert p["drift_zone_count"] == 2
        assert p["replay_corridor_count"] == 1
        assert p["continuity_corridor_count"] == 2
        assert p["topology_density_score"] == 0.55
        assert p["cartography_advisory_flags"] == [
            "advisory_only",
            "analytics_only",
            "cartography_only",
            "visualization_support_only",
        ]
        assert p["temporal_stability_pressure_status"] == NOT_COMPUTABLE
        assert p["aggregate_stress_score"] == 0.0
        assert p["pressure_zone_count"] == 0

    def test_optimization_drift_not_computable_when_missing(self) -> None:
        p = self._build_with_mocks()
        assert p["optimization_drift_summary"]["status"] == NOT_COMPUTABLE
        assert p["optimization_drift_summary"]["optimization_auto_apply"] is False

    def test_optimization_drift_present_with_benchmark(self) -> None:
        p = self._build_with_mocks(benchmark_data=_make_benchmark_artifact())
        od = p["optimization_drift_summary"]
        assert od["status"] == "PRESENT"
        assert od["optimization_auto_apply"] is False

    def test_final_posture_shape(self) -> None:
        p = self._build_with_mocks()
        fp = p["final_posture"]
        assert "final_status" in fp
        assert "remaining_blockers" in fp
        assert fp["authority_granted"] is False
        assert fp["mutation_allowed"] is False
        assert fp["promotion_allowed"] is False
        assert fp["projection_only"] is True
        assert fp["advisory_only"] is True


# ---------------------------------------------------------------------------
# write_runtime_projection_packet tests
# ---------------------------------------------------------------------------


class TestWriteRuntimeProjectionPacket:
    def test_writes_valid_json(self, tmp_path: Path) -> None:
        out = tmp_path / "test_projection.json"
        p = build_runtime_projection_packet()
        write_runtime_projection_packet(out, p)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["schema"] == "RuntimeProjectionPacket.v1"

    def test_trailing_newline(self, tmp_path: Path) -> None:
        out = tmp_path / "test_projection.json"
        p = build_runtime_projection_packet()
        write_runtime_projection_packet(out, p)
        raw = out.read_text(encoding="utf-8")
        assert raw.endswith("\n")

    def test_canonical_sorted_keys(self, tmp_path: Path) -> None:
        out = tmp_path / "test_projection.json"
        p = build_runtime_projection_packet()
        write_runtime_projection_packet(out, p)
        raw = out.read_text(encoding="utf-8")
        # Keys in the top-level object should be sorted lexicographically
        data = json.loads(raw)
        top_keys = list(data.keys())
        assert top_keys == sorted(top_keys)
        # File should end with a newline
        assert raw.endswith("\n")


# ---------------------------------------------------------------------------
# Markdown generation tests
# ---------------------------------------------------------------------------


class TestBuildProjectionMarkdown:
    def _packet(self) -> dict[str, Any]:
        def mock_load(path: Any) -> dict[str, Any] | None:
            mapping = {
                "out/audit/runtime_performance_profile_001.latest.json": _make_profile_artifact(),
                "out/audit/runtime_benchmark_001.latest.json": _make_benchmark_artifact(),
                "out/audit/incremental_replay_001.latest.json": _make_replay_artifact(),
                "out/audit/operator_runtime_console_001.latest.json": _make_console_artifact(),
                "out/audit/operator_action_queue_001.latest.json": _make_operator_action_queue_artifact(),
            }
            return mapping.get(str(path))

        with patch("core.aal_viz_runtime_projection._load_artifact", side_effect=mock_load):
            return build_runtime_projection_packet()

    def test_markdown_contains_patch_id(self) -> None:
        md = build_projection_markdown(self._packet())
        assert PATCH_ID in md

    def test_markdown_runtime_health_section(self) -> None:
        md = build_projection_markdown(self._packet())
        assert "## Runtime Health" in md

    def test_markdown_replay_topology_section(self) -> None:
        md = build_projection_markdown(self._packet())
        assert "## Replay Topology Health" in md

    def test_markdown_operator_next_actions(self) -> None:
        md = build_projection_markdown(self._packet())
        assert "## Operator Next Actions" in md

    def test_markdown_remaining_blockers(self) -> None:
        md = build_projection_markdown(self._packet())
        assert "## Remaining Blockers" in md

    def test_markdown_drift_posture(self) -> None:
        md = build_projection_markdown(self._packet())
        assert "## Optimization Drift Posture" in md

    def test_markdown_replay_equivalence(self) -> None:
        md = build_projection_markdown(self._packet())
        assert "## Replay Equivalence Posture" in md

    def test_markdown_graph_render_packet_section(self) -> None:
        md = build_projection_markdown(self._packet())
        assert "## Graph Render Packet" in md

    def test_markdown_operator_action_queue_section(self) -> None:
        md = build_projection_markdown(self._packet())
        assert "## Operator Action Queue" in md

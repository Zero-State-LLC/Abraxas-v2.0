"""AAL-Viz runtime projection integration for ABRAXAS v2.0.

PATCH-P13-AAL-VIZ-RUNTIME-PROJECTION-INTEGRATION-001

Deterministic projection packets integrating runtime/replay/benchmark/operator
data into AAL-Viz-compatible projection surfaces.

Hard invariants (always enforced):
    projection_only     = True
    advisory_only       = True
    authority_granted   = False
    mutation_allowed    = False
    promotion_allowed   = False
    inference_authority = False

No rendering engine.  No websocket/live-mutation channels.
No runtime/replay/canon/forecast/optimization/governance mutation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.diagnostics import stable_correlation_id

PATCH_ID = "PATCH-P13-AAL-VIZ-RUNTIME-PROJECTION-INTEGRATION-001"

NOT_COMPUTABLE = "NOT_COMPUTABLE"

# ---------------------------------------------------------------------------
# Hard authority boundary — never changes
# ---------------------------------------------------------------------------

_AUTHORITY_BOUNDARY: dict[str, Any] = {
    "projection_only": True,
    "advisory_only": True,
    "authority_granted": False,
    "mutation_allowed": False,
    "promotion_allowed": False,
    "inference_authority": False,
}


# ---------------------------------------------------------------------------
# Source artifact loading helpers
# ---------------------------------------------------------------------------


def _load_artifact(path: str | Path | None) -> dict[str, Any] | None:
    """Load a JSON artifact from disk; return None if absent or unreadable."""
    if path is None:
        return None
    try:
        text = Path(path).read_text(encoding="utf-8")
        return json.loads(text)  # type: ignore[no-any-return]
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# ReplayTopologyProjection.v1
# ---------------------------------------------------------------------------


def build_replay_topology_projection(
    replay_data: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a deterministic ReplayTopologyProjection.v1 packet.

    Extracts topology from an incremental replay artifact (IncrementalReplayPlan.v1
    or operator console replay data).  If the artifact is absent, surfaces are
    marked NOT_COMPUTABLE rather than fabricated.

    Ordering is deterministic: nodes sorted lexicographically.
    """
    if replay_data is None:
        return {
            "schema": "ReplayTopologyProjection.v1",
            "patch_id": PATCH_ID,
            "status": NOT_COMPUTABLE,
            "reason": "source replay artifact missing or unreadable",
            **_AUTHORITY_BOUNDARY,
        }

    nodes_raw: list[str] = sorted(replay_data.get("invalidated_nodes", []))
    skipped_raw: list[str] = sorted(replay_data.get("skipped_surfaces", []))
    chunks_raw: list[dict[str, Any]] = replay_data.get("replay_chunks", [])

    # Deterministic edges: extract from node dependency lists when available
    graph_nodes: list[dict[str, Any]] = replay_data.get("nodes", [])
    edges: list[dict[str, str]] = []
    for node in sorted(graph_nodes, key=lambda n: n.get("node_id", "")):
        nid = node.get("node_id", "")
        for dep in sorted(node.get("dependencies", [])):
            edges.append({"source": dep, "target": nid})

    # Invalidation lineage
    invalidation_lineage: dict[str, Any] = {
        "invalidated_count": len(nodes_raw),
        "skipped_count": len(skipped_raw),
        "fail_closed": replay_data.get("fail_closed", False),
        "lineage_hash": replay_data.get("lineage_hash", NOT_COMPUTABLE),
    }

    # Replay equivalence status
    equivalence_status: dict[str, Any] = {
        "equivalence_verified": replay_data.get("replay_equivalence_verified", NOT_COMPUTABLE),
        "final_status": replay_data.get("final_status", NOT_COMPUTABLE),
    }

    topology_hash = canonical_hash(
        {
            "patch_id": PATCH_ID,
            "nodes": nodes_raw,
            "edges": edges,
            "skipped": skipped_raw,
            "replay_graph_hash": replay_data.get("replay_graph_hash", ""),
        }
    )

    return {
        "schema": "ReplayTopologyProjection.v1",
        "patch_id": PATCH_ID,
        "status": "PRESENT",
        "replay_graph_hash": replay_data.get("replay_graph_hash", NOT_COMPUTABLE),
        "nodes": nodes_raw,
        "edges": edges,
        "skipped_surfaces": skipped_raw,
        "replay_chunks": chunks_raw,
        "invalidation_lineage": invalidation_lineage,
        "replay_equivalence_status": equivalence_status,
        "topology_hash": topology_hash,
        **_AUTHORITY_BOUNDARY,
    }


# ---------------------------------------------------------------------------
# BenchmarkTrendProjection.v1
# ---------------------------------------------------------------------------


def build_benchmark_trend_projection(
    benchmark_data: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a deterministic BenchmarkTrendProjection.v1 packet.

    Aggregates cost, cache, replay, and drift signals from a
    RuntimeBenchmarkArtifact.v1.  If absent, surfaces are NOT_COMPUTABLE.

    Trend aggregation is deterministic: all derived fields from input data only.
    """
    if benchmark_data is None:
        return {
            "schema": "BenchmarkTrendProjection.v1",
            "patch_id": PATCH_ID,
            "status": NOT_COMPUTABLE,
            "reason": "source benchmark artifact missing or unreadable",
            **_AUTHORITY_BOUNDARY,
        }

    drift_report: dict[str, Any] = benchmark_data.get("drift_report", {})
    baseline_suite: dict[str, Any] = benchmark_data.get("baseline_suite", {})
    optimized_suite: dict[str, Any] = benchmark_data.get("optimized_suite", {})

    # Runtime cost delta
    perf_delta: dict[str, Any] = drift_report.get("performance_delta", {})
    runtime_cost_delta = {
        "delta_ns": perf_delta.get("delta_ns", 0),
        "delta_pct": perf_delta.get("delta_pct", 0.0),
        "baseline_mean_ns": perf_delta.get("baseline_mean_ns", 0),
        "optimized_mean_ns": perf_delta.get("optimized_mean_ns", 0),
    }

    # Incremental replay reduction
    full_traversals = baseline_suite.get("replay_traversals", 0)
    inc_traversals = optimized_suite.get("replay_traversals", 0)
    traversal_delta = inc_traversals - full_traversals

    full_artifact_writes = baseline_suite.get("artifact_writes", 0)
    inc_artifact_writes = optimized_suite.get("artifact_writes", 0)
    artifact_reduction = (
        round(1.0 - (inc_artifact_writes / full_artifact_writes), 6)
        if full_artifact_writes > 0
        else 0.0
    )

    # Cache hit/miss trends
    baseline_cache: dict[str, Any] = baseline_suite.get("cache", {})
    optimized_cache: dict[str, Any] = optimized_suite.get("cache", {})
    cache_trend = {
        "baseline_hits": baseline_cache.get("total_hits", 0),
        "baseline_misses": baseline_cache.get("total_misses", 0),
        "optimized_hits": optimized_cache.get("total_hits", 0),
        "optimized_misses": optimized_cache.get("total_misses", 0),
        "miss_delta": optimized_cache.get("total_misses", 0)
        - baseline_cache.get("total_misses", 0),
    }

    # Drift detections
    drift_detections: list[str] = sorted(drift_report.get("detections", []))
    drift_detected: bool = bool(drift_report.get("drift_detected", False))

    trend_hash = canonical_hash(
        {
            "patch_id": PATCH_ID,
            "report_hash": drift_report.get("report_hash", ""),
            "baseline_suite_hash": baseline_suite.get("suite_hash", ""),
            "optimized_suite_hash": optimized_suite.get("suite_hash", ""),
            "drift_detected": drift_detected,
        }
    )

    return {
        "schema": "BenchmarkTrendProjection.v1",
        "patch_id": PATCH_ID,
        "status": "PRESENT",
        "runtime_cost_delta": runtime_cost_delta,
        "traversal_counts": {
            "baseline_traversals": full_traversals,
            "optimized_traversals": inc_traversals,
            "traversal_delta": traversal_delta,
        },
        "artifact_regeneration_reduction": artifact_reduction,
        "cache_hit_miss_trend": cache_trend,
        "drift_detections": drift_detections,
        "drift_detected": drift_detected,
        "output_hash_stable": optimized_suite.get("output_hash_stable", NOT_COMPUTABLE),
        "trend_hash": trend_hash,
        **_AUTHORITY_BOUNDARY,
    }


# ---------------------------------------------------------------------------
# RuntimeHealthProjection.v1
# ---------------------------------------------------------------------------


def build_runtime_health_projection(
    profile_data: dict[str, Any] | None,
    benchmark_data: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a deterministic RuntimeHealthProjection.v1 packet.

    Combines runtime profiling and benchmark data into a consolidated health
    surface.  Missing artifacts are marked NOT_COMPUTABLE.
    """
    profile_status = "PRESENT" if profile_data is not None else NOT_COMPUTABLE
    benchmark_status = "PRESENT" if benchmark_data is not None else NOT_COMPUTABLE

    # Profile summary
    if profile_data is not None:
        profile_summary: dict[str, Any] = {
            "status": "PRESENT",
            "profile_enabled": profile_data.get("profile_enabled", NOT_COMPUTABLE),
            "measured_surfaces": sorted(profile_data.get("measured_surfaces", [])),
            "final_status": profile_data.get("final_status", NOT_COMPUTABLE),
        }
    else:
        profile_summary = {
            "status": NOT_COMPUTABLE,
            "reason": "runtime profile artifact missing",
        }

    # Benchmark summary
    if benchmark_data is not None:
        drift_report = benchmark_data.get("drift_report", {})
        perf_delta = drift_report.get("performance_delta", {})
        benchmark_summary: dict[str, Any] = {
            "status": "PRESENT",
            "drift_detected": drift_report.get("drift_detected", NOT_COMPUTABLE),
            "variance_spike_detected": drift_report.get("advisory", {}).get(
                "variance_spike_detected", NOT_COMPUTABLE
            ),
            "baseline_mean_ns": perf_delta.get("baseline_mean_ns", NOT_COMPUTABLE),
            "optimized_mean_ns": perf_delta.get("optimized_mean_ns", NOT_COMPUTABLE),
        }
    else:
        benchmark_summary = {
            "status": NOT_COMPUTABLE,
            "reason": "benchmark artifact missing",
        }

    # Derive overall health signal
    if profile_data is None and benchmark_data is None:
        health = NOT_COMPUTABLE
    elif (
        benchmark_data is not None
        and benchmark_data.get("drift_report", {}).get("drift_detected", False)
    ):
        health = "DEGRADED"
    elif profile_data is not None and profile_data.get("final_status") != "PASS":
        health = "DEGRADED"
    else:
        health = "HEALTHY"

    health_hash = canonical_hash(
        {
            "patch_id": PATCH_ID,
            "profile_status": profile_status,
            "benchmark_status": benchmark_status,
            "health": health,
        }
    )

    return {
        "schema": "RuntimeHealthProjection.v1",
        "patch_id": PATCH_ID,
        "health": health,
        "profile_summary": profile_summary,
        "benchmark_summary": benchmark_summary,
        "health_hash": health_hash,
        **_AUTHORITY_BOUNDARY,
    }


# ---------------------------------------------------------------------------
# Operator summary extraction
# ---------------------------------------------------------------------------


def build_operator_summary_projection(
    console_data: dict[str, Any] | None,
    projection_bus_data: dict[str, Any] | None = None,
    snapshot_index_data: dict[str, Any] | None = None,
    chronoscope_data: dict[str, Any] | None = None,
    graph_render_packet_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Extract an operator summary from an existing console packet.

    If the console packet is absent, marks fields NOT_COMPUTABLE.
    """
    projection_bus_status = (
        projection_bus_data.get("final_status", NOT_COMPUTABLE)
        if projection_bus_data is not None
        else NOT_COMPUTABLE
    )
    snapshot_index_status = (
        snapshot_index_data.get("final_status", NOT_COMPUTABLE)
        if snapshot_index_data is not None
        else NOT_COMPUTABLE
    )
    cursor_bounds = (
        snapshot_index_data.get("cursor_bounds", {"first": None, "last": None})
        if snapshot_index_data is not None
        else {"first": None, "last": None}
    )
    temporal_window_count = (
        len(snapshot_index_data.get("temporal_windows", []))
        if snapshot_index_data is not None
        else 0
    )
    lineage_gap_count = (
        int(snapshot_index_data.get("lineage_gap_count", 0))
        if snapshot_index_data is not None
        else 0
    )
    projection_bus_advisory_flags = (
        sorted(projection_bus_data.get("advisory_flags", []))
        if projection_bus_data is not None
        else []
    )
    chronoscope_status = (
        chronoscope_data.get("final_status", NOT_COMPUTABLE)
        if chronoscope_data is not None
        else NOT_COMPUTABLE
    )
    timeline_point_count = (
        len(chronoscope_data.get("timeline_points", []))
        if chronoscope_data is not None
        else 0
    )
    playback_cursor_bounds = (
        chronoscope_data.get("playback_cursor_bounds", {"first": None, "last": None})
        if chronoscope_data is not None
        else {"first": None, "last": None}
    )
    drift_timeline_status = (
        chronoscope_data.get("drift_timeline", {}).get("drift_timeline_status", NOT_COMPUTABLE)
        if chronoscope_data is not None
        else NOT_COMPUTABLE
    )
    lineage_evolution_status = (
        chronoscope_data.get("lineage_evolution", {}).get("lineage_status", NOT_COMPUTABLE)
        if chronoscope_data is not None
        else NOT_COMPUTABLE
    )
    chronoscope_advisory_flags = (
        sorted(chronoscope_data.get("chronoscope_advisory_flags", []))
        if chronoscope_data is not None
        else []
    )
    graph_render_packet_status = (
        graph_render_packet_data.get("final_status", NOT_COMPUTABLE)
        if graph_render_packet_data is not None
        else NOT_COMPUTABLE
    )
    render_node_count = (
        int(graph_render_packet_data.get("render_node_count", 0))
        if graph_render_packet_data is not None
        else 0
    )
    render_edge_count = (
        int(graph_render_packet_data.get("render_edge_count", 0))
        if graph_render_packet_data is not None
        else 0
    )
    render_layer_count = (
        int(graph_render_packet_data.get("render_layer_count", 0))
        if graph_render_packet_data is not None
        else 0
    )
    render_overlay_count = (
        int(graph_render_packet_data.get("render_overlay_count", 0))
        if graph_render_packet_data is not None
        else 0
    )
    render_blocker_count = (
        int(graph_render_packet_data.get("render_blocker_count", 0))
        if graph_render_packet_data is not None
        else 0
    )
    render_advisory_flags = (
        sorted(graph_render_packet_data.get("render_advisory_flags", []))
        if graph_render_packet_data is not None
        else []
    )

    if console_data is None:
        return {
            "status": NOT_COMPUTABLE,
            "reason": "operator console artifact missing or unreadable",
            "next_actions": [],
            "projection_bus_status": projection_bus_status,
            "snapshot_index_status": snapshot_index_status,
            "cursor_bounds": cursor_bounds,
            "temporal_window_count": temporal_window_count,
            "lineage_gap_count": lineage_gap_count,
            "projection_bus_advisory_flags": projection_bus_advisory_flags,
            "chronoscope_status": chronoscope_status,
            "timeline_point_count": timeline_point_count,
            "playback_cursor_bounds": playback_cursor_bounds,
            "drift_timeline_status": drift_timeline_status,
            "lineage_evolution_status": lineage_evolution_status,
            "chronoscope_advisory_flags": chronoscope_advisory_flags,
            "graph_render_packet_status": graph_render_packet_status,
            "render_node_count": render_node_count,
            "render_edge_count": render_edge_count,
            "render_layer_count": render_layer_count,
            "render_overlay_count": render_overlay_count,
            "render_blocker_count": render_blocker_count,
            "render_advisory_flags": render_advisory_flags,
        }

    return {
        "status": "PRESENT",
        "packet_id": console_data.get("packet_id", NOT_COMPUTABLE),
        "final_status": console_data.get("final_status", NOT_COMPUTABLE),
        "remaining_blockers": sorted(console_data.get("remaining_blockers", [])),
        "next_actions": console_data.get("operator_next_actions", []),
        "projection_bus_status": projection_bus_status,
        "snapshot_index_status": snapshot_index_status,
        "cursor_bounds": cursor_bounds,
        "temporal_window_count": temporal_window_count,
        "lineage_gap_count": lineage_gap_count,
        "projection_bus_advisory_flags": projection_bus_advisory_flags,
        "chronoscope_status": chronoscope_status,
        "timeline_point_count": timeline_point_count,
        "playback_cursor_bounds": playback_cursor_bounds,
        "drift_timeline_status": drift_timeline_status,
        "lineage_evolution_status": lineage_evolution_status,
        "chronoscope_advisory_flags": chronoscope_advisory_flags,
        "graph_render_packet_status": graph_render_packet_status,
        "render_node_count": render_node_count,
        "render_edge_count": render_edge_count,
        "render_layer_count": render_layer_count,
        "render_overlay_count": render_overlay_count,
        "render_blocker_count": render_blocker_count,
        "render_advisory_flags": render_advisory_flags,
    }


# ---------------------------------------------------------------------------
# Visualization hints
# ---------------------------------------------------------------------------


def build_visualization_hints(
    replay_topology: dict[str, Any],
    benchmark_trends: dict[str, Any],
    runtime_health: dict[str, Any],
) -> dict[str, Any]:
    """Emit deterministic visualization hints for AAL-Viz rendering surfaces.

    Hints describe what to render; they do not drive rendering decisions.
    All hints are advisory_only and non-authoritative.
    """
    hints: list[str] = []

    # Replay topology hints
    topo_status = replay_topology.get("status")
    if topo_status == NOT_COMPUTABLE:
        hints.append("HINT:replay_topology_unavailable — render NOT_COMPUTABLE badge")
    else:
        node_count = len(replay_topology.get("nodes", []))
        if node_count > 0:
            hints.append(
                f"HINT:replay_topology_available — render {node_count} invalidated node(s)"
            )
        skipped = len(replay_topology.get("skipped_surfaces", []))
        if skipped > 0:
            hints.append(
                f"HINT:skipped_surfaces_present — render {skipped} skipped surface(s)"
            )
        if replay_topology.get("invalidation_lineage", {}).get("fail_closed", False):
            hints.append("HINT:fail_closed_invalidation — highlight conservative posture")
        eq = replay_topology.get("replay_equivalence_status", {}).get("equivalence_verified")
        if eq is True:
            hints.append("HINT:replay_equivalence_verified — render green equivalence badge")
        elif eq is False:
            hints.append("HINT:replay_equivalence_failed — render equivalence warning")

    # Benchmark trend hints
    bench_status = benchmark_trends.get("status")
    if bench_status == NOT_COMPUTABLE:
        hints.append("HINT:benchmark_trends_unavailable — render NOT_COMPUTABLE badge")
    else:
        if benchmark_trends.get("drift_detected"):
            for d in benchmark_trends.get("drift_detections", []):
                hints.append(f"HINT:drift_signal:{d} — render drift alert badge")
        else:
            hints.append("HINT:no_drift_detected — render clean benchmark badge")
        reduction = benchmark_trends.get("artifact_regeneration_reduction", 0.0)
        if isinstance(reduction, float) and reduction > 0:
            hints.append(
                f"HINT:artifact_reduction:{reduction:.4f} — render incremental efficiency gain"
            )

    # Runtime health hints
    health_val = runtime_health.get("health")
    if health_val == NOT_COMPUTABLE:
        hints.append("HINT:runtime_health_unavailable — render NOT_COMPUTABLE badge")
    elif health_val == "HEALTHY":
        hints.append("HINT:runtime_healthy — render green health badge")
    elif health_val == "DEGRADED":
        hints.append("HINT:runtime_degraded — render amber health badge")

    return {
        "schema": "AALVizVisualizationHints.v1",
        "patch_id": PATCH_ID,
        "hints": sorted(hints),
        "advisory_only": True,
        "hint_count": len(hints),
    }


# ---------------------------------------------------------------------------
# Final posture derivation
# ---------------------------------------------------------------------------


def _derive_final_posture(
    replay_topology: dict[str, Any],
    benchmark_trends: dict[str, Any],
    runtime_health: dict[str, Any],
    operator_summary: dict[str, Any],
) -> dict[str, Any]:
    blockers: list[str] = []

    # Propagate missing artifacts
    for label, surface in [
        ("replay_topology", replay_topology),
        ("benchmark_trends", benchmark_trends),
    ]:
        if surface.get("status") == NOT_COMPUTABLE:
            blockers.append(f"missing_artifact:{label}")

    # Runtime health degraded
    if runtime_health.get("health") == "DEGRADED":
        blockers.append("runtime_health:DEGRADED")

    # Operator-level remaining blockers
    for b in operator_summary.get("remaining_blockers", []):
        blockers.append(f"operator_blocker:{b}")

    final_status: str
    if blockers:
        # If all are missing-artifact blockers only, be precise about BLOCKED
        if all(b.startswith("missing_artifact:") for b in blockers):
            final_status = "BLOCKED"
        else:
            final_status = "ADVISORY_ONLY"
    else:
        final_status = "PASS"

    return {
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "projection_only": True,
        "advisory_only": True,
        "final_status": final_status,
        "remaining_blockers": sorted(blockers),
    }


# ---------------------------------------------------------------------------
# RuntimeProjectionPacket.v1 — top-level aggregate
# ---------------------------------------------------------------------------


def build_runtime_projection_packet(
    *,
    packet_id: str = "aal_viz_runtime_projection_001",
    source_artifact_paths: dict[str, str | Path] | None = None,
) -> dict[str, Any]:
    """Build a deterministic RuntimeProjectionPacket.v1.

    This is the top-level AAL-Viz runtime projection aggregate.  It integrates:
    - replay topology projection
    - benchmark trend projection
    - runtime health projection
    - operator summary
    - visualization hints

    If source artifacts are absent, affected surfaces are marked NOT_COMPUTABLE.
    No values are fabricated.  Final posture honestly reflects evidence availability.

    Hard invariants are always enforced at packet level:
        projection_only=True, advisory_only=True,
        authority_granted=False, mutation_allowed=False,
        promotion_allowed=False, inference_authority=False
    """
    defaults: dict[str, str | Path] = {
        "runtime_performance_profile": "out/audit/runtime_performance_profile_001.latest.json",
        "runtime_benchmark": "out/audit/runtime_benchmark_001.latest.json",
        "incremental_replay": "out/audit/incremental_replay_001.latest.json",
        "operator_console": "out/audit/operator_runtime_console_001.latest.json",
        "projection_bus": "out/projections/projection_bus_001.latest.json",
        "temporal_snapshot_spine": "out/projections/temporal_snapshot_spine_001.latest.json",
        "projection_chronoscope": "out/projections/projection_chronoscope_001.latest.json",
        "graph_render_packet": "out/projections/aal_viz_graph_render_packet_001.latest.json",
    }
    paths = {**defaults, **(source_artifact_paths or {})}

    # Load source artifacts
    profile_data = _load_artifact(paths.get("runtime_performance_profile"))
    benchmark_data = _load_artifact(paths.get("runtime_benchmark"))
    replay_data = _load_artifact(paths.get("incremental_replay"))
    console_data = _load_artifact(paths.get("operator_console"))
    projection_bus_data = _load_artifact(paths.get("projection_bus"))
    snapshot_index_data = _load_artifact(paths.get("temporal_snapshot_spine"))
    chronoscope_data = _load_artifact(paths.get("projection_chronoscope"))
    graph_render_packet_data = _load_artifact(paths.get("graph_render_packet"))

    # Build sub-projections
    replay_topology = build_replay_topology_projection(replay_data)
    benchmark_trends = build_benchmark_trend_projection(benchmark_data)
    runtime_health = build_runtime_health_projection(profile_data, benchmark_data)
    operator_summary = build_operator_summary_projection(
        console_data=console_data,
        projection_bus_data=projection_bus_data,
        snapshot_index_data=snapshot_index_data,
        chronoscope_data=chronoscope_data,
        graph_render_packet_data=graph_render_packet_data,
    )

    # Visualization hints (deterministic, advisory only)
    visualization_hints = build_visualization_hints(
        replay_topology, benchmark_trends, runtime_health
    )

    # Authority boundary summary
    authority_boundary_summary: dict[str, Any] = {
        **_AUTHORITY_BOUNDARY,
        "boundary_note": (
            "All authority flags permanently locked for P13 projection packet."
        ),
    }

    # Optimization drift summary (projection-only view of benchmark drift)
    if benchmark_data is not None:
        drift_report = benchmark_data.get("drift_report", {})
        optimization_drift_summary: dict[str, Any] = {
            "status": "PRESENT",
            "drift_detected": drift_report.get("drift_detected", NOT_COMPUTABLE),
            "detections": sorted(drift_report.get("detections", [])),
            "advisory": drift_report.get("advisory", {}),
            "performance_delta": drift_report.get("performance_delta", {}),
            "optimization_auto_apply": False,
        }
    else:
        optimization_drift_summary = {
            "status": NOT_COMPUTABLE,
            "reason": "benchmark artifact missing",
            "optimization_auto_apply": False,
        }

    # Source artifact tracking
    source_artifacts: dict[str, str] = {k: str(v) for k, v in paths.items()}

    # Final posture
    final_posture = _derive_final_posture(
        replay_topology=replay_topology,
        benchmark_trends=benchmark_trends,
        runtime_health=runtime_health,
        operator_summary=operator_summary,
    )

    # Deterministic packet hash
    projection_id = canonical_hash(
        {
            "packet_id": packet_id,
            "patch_id": PATCH_ID,
            "replay_topology_hash": replay_topology.get("topology_hash", ""),
            "benchmark_trend_hash": benchmark_trends.get("trend_hash", ""),
            "runtime_health_hash": runtime_health.get("health_hash", ""),
        }
    )

    projection_timestamp = stable_correlation_id(
        f"aal_viz_runtime_projection.{packet_id}",
        context={"packet_id": packet_id},
    )

    return {
        "schema": "RuntimeProjectionPacket.v1",
        "patch_id": PATCH_ID,
        "packet_id": packet_id,
        "projection_id": projection_id,
        "projection_timestamp": projection_timestamp,
        "source_artifacts": source_artifacts,
        "replay_topology": replay_topology,
        "benchmark_trends": benchmark_trends,
        "runtime_health": runtime_health,
        "optimization_drift_summary": optimization_drift_summary,
        "operator_summary": operator_summary,
        "projection_bus_status": operator_summary["projection_bus_status"],
        "snapshot_index_status": operator_summary["snapshot_index_status"],
        "cursor_bounds": operator_summary["cursor_bounds"],
        "temporal_window_count": operator_summary["temporal_window_count"],
        "lineage_gap_count": operator_summary["lineage_gap_count"],
        "projection_bus_advisory_flags": operator_summary["projection_bus_advisory_flags"],
        "chronoscope_status": operator_summary["chronoscope_status"],
        "timeline_point_count": operator_summary["timeline_point_count"],
        "playback_cursor_bounds": operator_summary["playback_cursor_bounds"],
        "drift_timeline_status": operator_summary["drift_timeline_status"],
        "lineage_evolution_status": operator_summary["lineage_evolution_status"],
        "chronoscope_advisory_flags": operator_summary["chronoscope_advisory_flags"],
        "graph_render_packet_status": operator_summary["graph_render_packet_status"],
        "render_node_count": operator_summary["render_node_count"],
        "render_edge_count": operator_summary["render_edge_count"],
        "render_layer_count": operator_summary["render_layer_count"],
        "render_overlay_count": operator_summary["render_overlay_count"],
        "render_blocker_count": operator_summary["render_blocker_count"],
        "render_advisory_flags": operator_summary["render_advisory_flags"],
        "authority_boundary_summary": authority_boundary_summary,
        "visualization_hints": visualization_hints,
        "final_posture": final_posture,
        # Hard invariants at top level for fast inspection
        "projection_only": True,
        "advisory_only": True,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "inference_authority": False,
        "final_status": final_posture["final_status"],
        "remaining_blockers": final_posture["remaining_blockers"],
    }


def write_runtime_projection_packet(
    path: str | Path,
    packet: dict[str, Any],
) -> Path:
    """Write a runtime projection packet to *path* as canonical JSON."""
    target = Path(path)
    write_canonical_json(target, packet)
    return target


def build_projection_markdown(packet: dict[str, Any]) -> str:
    """Build a concise operator-readable Markdown summary of the projection packet."""
    lines: list[str] = []
    lines.append(f"# AAL-Viz Runtime Projection — {packet.get('packet_id', '')}")
    lines.append("")
    lines.append(f"**Patch:** `{packet.get('patch_id', '')}`")
    lines.append(f"**Final Status:** `{packet.get('final_status', '')}`")
    lines.append(f"**Projection Only:** `{packet.get('projection_only', True)}`")
    lines.append(f"**Advisory Only:** `{packet.get('advisory_only', True)}`")
    lines.append("")

    # Authority boundary
    lines.append("## Authority Boundary")
    lines.append(
        "- authority_granted: `false`  mutation_allowed: `false`  "
        "promotion_allowed: `false`  inference_authority: `false`"
    )
    lines.append("")

    # Runtime health
    rh = packet.get("runtime_health", {})
    lines.append("## Runtime Health")
    lines.append(f"- Health: `{rh.get('health', '?')}`")
    ps = rh.get("profile_summary", {})
    lines.append(f"- Profile: `{ps.get('status', '?')}`")
    if ps.get("status") == "PRESENT":
        lines.append(f"  - Final status: `{ps.get('final_status', '?')}`")
    bms = rh.get("benchmark_summary", {})
    lines.append(f"- Benchmark: `{bms.get('status', '?')}`")
    if bms.get("status") == "PRESENT":
        lines.append(f"  - Drift detected: `{bms.get('drift_detected', '?')}`")
    lines.append("")

    # Replay topology health
    rt = packet.get("replay_topology", {})
    lines.append("## Replay Topology Health")
    lines.append(f"- Status: `{rt.get('status', '?')}`")
    if rt.get("status") == "PRESENT":
        lines.append(f"- Invalidated nodes: `{len(rt.get('nodes', []))}`")
        lines.append(f"- Skipped surfaces: `{len(rt.get('skipped_surfaces', []))}`")
        inv = rt.get("invalidation_lineage", {})
        lines.append(f"- Fail closed: `{inv.get('fail_closed', '?')}`")
        eq = rt.get("replay_equivalence_status", {})
        lines.append(f"- Equivalence verified: `{eq.get('equivalence_verified', '?')}`")
    lines.append("")

    # Optimization drift posture
    od = packet.get("optimization_drift_summary", {})
    lines.append("## Optimization Drift Posture")
    lines.append(f"- Status: `{od.get('status', '?')}`")
    if od.get("status") == "PRESENT":
        lines.append(f"- Drift detected: `{od.get('drift_detected', '?')}`")
        detections = od.get("detections", [])
        if detections:
            lines.append(f"- Detections: {', '.join(f'`{d}`' for d in detections)}")
    lines.append(f"- Optimization auto-apply: `{od.get('optimization_auto_apply', False)}`")
    lines.append("")

    # Graph render packet posture
    lines.append("## Graph Render Packet")
    lines.append(f"- Status: `{packet.get('graph_render_packet_status', NOT_COMPUTABLE)}`")
    lines.append(f"- Nodes: `{packet.get('render_node_count', 0)}`")
    lines.append(f"- Edges: `{packet.get('render_edge_count', 0)}`")
    lines.append(f"- Layers: `{packet.get('render_layer_count', 0)}`")
    lines.append(f"- Overlays: `{packet.get('render_overlay_count', 0)}`")
    lines.append(f"- Blockers: `{packet.get('render_blocker_count', 0)}`")
    lines.append("")

    # Replay equivalence posture
    lines.append("## Replay Equivalence Posture")
    if rt.get("status") == "PRESENT":
        eq = rt.get("replay_equivalence_status", {})
        lines.append(f"- Equivalence verified: `{eq.get('equivalence_verified', '?')}`")
        lines.append(f"- Final replay status: `{eq.get('final_status', '?')}`")
    else:
        lines.append("- Status: NOT_COMPUTABLE (replay artifact missing)")
    lines.append("")

    # Operator next actions
    op = packet.get("operator_summary", {})
    lines.append("## Operator Next Actions")
    actions = op.get("next_actions", [])
    if actions:
        for a in actions:
            lines.append(f"- {a}")
    else:
        lines.append("- No actions — projection-only, no blockers found")
    lines.append("")

    # Remaining blockers
    blockers = packet.get("remaining_blockers", [])
    lines.append("## Remaining Blockers")
    if blockers:
        for b in blockers:
            lines.append(f"- `{b}`")
    else:
        lines.append("- None")
    lines.append("")

    return "\n".join(lines)

from __future__ import annotations

# WP-D4-C3: pure builder — sole-writer scripts own out/ publication.
from core.observability.lineage import build_lineage_trace_packet
from core.observability.metrics import MetricPoint, build_metric_series
from core.observability.replay_metrics import build_replay_telemetry_packet
from core.observability.snapshots import build_projection_state_snapshot
from core.observability.stabilization import build_stabilization_telemetry
from core.observability.telemetry import build_execution_telemetry_packet
from core.observability.timelines import build_runtime_timeline_packet


def run_observability_pipeline(execution_run: dict, replay_packet: dict, graph_packet: dict) -> dict:
    telemetry = build_execution_telemetry_packet(graph_packet, replay_packet)
    lineage = build_lineage_trace_packet(graph_packet)
    timeline = build_runtime_timeline_packet(graph_packet)
    stabilization = build_stabilization_telemetry(graph_packet, replay_packet)
    replay_telemetry = build_replay_telemetry_packet(graph_packet, replay_packet)
    metric_series = build_metric_series(
        "runtime_core",
        [
            MetricPoint(timestamp_index=0, metric_name="executed_nodes", metric_value=float(telemetry.executed_node_count)),
            MetricPoint(timestamp_index=1, metric_name="failed_nodes", metric_value=float(telemetry.failed_node_count)),
        ],
    )
    snapshot = build_projection_state_snapshot(execution_run.get("projection", {}), execution_run.get("queue", {}), execution_run.get("validation", {}), telemetry.model_dump(mode="json"), graph_packet)
    return {
        "schema_version": "ObservabilityAggregation.v1",
        "telemetry": telemetry.model_dump(mode="json"),
        "lineage": lineage.model_dump(mode="json"),
        "timeline": timeline.model_dump(mode="json"),
        "stabilization": stabilization.model_dump(mode="json"),
        "replay_telemetry": replay_telemetry.model_dump(mode="json"),
        "metric_series": metric_series.model_dump(mode="json"),
        "projection_snapshot": snapshot.model_dump(mode="json"),
        "status": "valid",
    }

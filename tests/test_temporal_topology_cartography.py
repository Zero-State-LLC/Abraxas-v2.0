from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from core.temporal_topology_cartography import (
    BLOCKED,
    NOT_COMPUTABLE,
    _classify_corridor,
    _classify_region,
    build_temporal_topology_cartography_markdown,
    build_temporal_topology_cartography_packet,
    summarize_temporal_topology_cartography,
    write_temporal_topology_cartography_packet,
)
from scripts.temporal import run_temporal_topology_cartography


def _locked_flags() -> dict[str, bool]:
    return {
        "execution_authority": False,
        "authority_granted": False,
        "mutation_allowed": False,
        "promotion_allowed": False,
        "auto_execute": False,
        "auto_approve": False,
        "command_channel": False,
        "bidirectional_control": False,
        "inference_authority": False,
    }


def _payloads() -> dict[str, dict[str, object]]:
    return {
        "cross_run_topology_fusion": {
            "schema": "CrossRunTopologyFusionPacket.v1",
            "cross_run_topology_fusion_status": "ADVISORY_ONLY",
            "fusion_node_count": 3,
            "fusion_nodes": [
                {
                    "node_id": "n-2",
                    "source_runs": ["r1", "r2", "r3"],
                    "lineage_refs": ["l1"],
                    "persistence_ratio": 0.9,
                    "continuity_ratio": 0.9,
                    "volatility_score": 0.1,
                    "stability_score": 0.9,
                    "evidence_count": 5,
                    "recurrence_count": 5,
                    "advisory_flags": ["lineage_continuity"],
                    "final_status": "ADVISORY_ONLY",
                },
                {
                    "node_id": "n-1",
                    "source_runs": ["r1", "r2"],
                    "lineage_refs": ["l2"],
                    "persistence_ratio": 0.4,
                    "continuity_ratio": 0.3,
                    "volatility_score": 0.8,
                    "stability_score": 0.2,
                    "evidence_count": 3,
                    "recurrence_count": 3,
                    "advisory_flags": ["drift_corridor"],
                    "final_status": "ADVISORY_ONLY",
                },
            ],
            "topology_persistence_clusters": [
                {
                    "cluster_id": "c1",
                    "cluster_status": "ADVISORY_ONLY",
                    "source_runs": ["r1", "r2", "r3"],
                    "persistence_ratio": 0.8,
                    "continuity_ratio": 0.8,
                    "node_refs": ["n-2"],
                    "lineage_refs": ["l1"],
                    "evidence_count": 4,
                    "advisory_flags": ["lineage_continuity"],
                }
            ],
            "lineage_fusion_corridors": [
                {
                    "corridor_id": "lc1",
                    "node_refs": ["n-2"],
                    "source_runs": ["r1", "r2", "r3"],
                    "recurrence_count": 3,
                    "continuity_ratio": 0.9,
                    "drift_score": 0.1,
                    "replay_stability_status": "ADVISORY_ONLY",
                    "transport_stability_status": "ADVISORY_ONLY",
                    "advisory_flags": ["lineage_continuity"],
                    "final_status": "ADVISORY_ONLY",
                    "source_hashes": ["h1"],
                },
                {
                    "corridor_id": "rc1",
                    "node_refs": ["n-1"],
                    "source_runs": ["r1", "r2", "r3"],
                    "recurrence_count": 3,
                    "continuity_ratio": 0.8,
                    "drift_score": 0.2,
                    "replay_stability_status": "PASS",
                    "transport_stability_status": "ADVISORY_ONLY",
                    "advisory_flags": ["replay_continuity"],
                    "final_status": "ADVISORY_ONLY",
                    "source_hashes": ["h2"],
                },
            ],
            "replay_continuity_status": "ADVISORY_ONLY",
            "transport_continuity_status": "ADVISORY_ONLY",
            "topology_stability_score": 0.7,
            "fusion_advisory_flags": ["advisory_only", "analytics_only", "fusion_only"],
            **_locked_flags(),
        },
        "multi_run_convergence": {
            "schema": "MultiRunConvergencePacket.v1",
            "multi_run_convergence_status": "ADVISORY_ONLY",
            "run_observations": [
                {
                    "run_id": "r1",
                    "timestamp_or_sequence": "t:001",
                    "topology_change_count": 4,
                    "lineage_shift_count": 3,
                    "queue_delta_count": 1,
                    "transport_delta_count": 1,
                },
                {
                    "run_id": "r2",
                    "timestamp_or_sequence": "t:002",
                    "topology_change_count": 2,
                    "lineage_shift_count": 1,
                    "queue_delta_count": 1,
                    "transport_delta_count": 0,
                },
                {
                    "run_id": "r3",
                    "timestamp_or_sequence": "t:003",
                    "topology_change_count": 1,
                    "lineage_shift_count": 0,
                    "queue_delta_count": 0,
                    "transport_delta_count": 0,
                },
            ],
            **_locked_flags(),
        },
        "temporal_state_diff": {
            "schema": "TemporalStateDiff.v1",
            "temporal_state_diff_status": "ADVISORY_ONLY",
            "diff_advisory_flags": ["advisory_only", "diff_only", "detection_only"],
            "diff_entries": [
                {"entry_id": "d1", "source_surface": "projection_bus", "change_type": "MODIFIED"},
                {"entry_id": "d2", "source_surface": "projection_bus", "change_type": "TOPOLOGY_SHIFT"},
                {"entry_id": "d3", "source_surface": "projection_chronoscope", "change_type": "DRIFT_ACCELERATION"},
            ],
            **_locked_flags(),
        },
        "aal_viz_graph_render_packet": {
            "schema": "AALVizGraphRenderPacket.v1",
            "nodes": [{"node_id": "g1"}],
            "edges": [{"edge_id": "e1"}],
            "render_advisory_flags": ["advisory_only", "render_only"],
            **_locked_flags(),
        },
        "projection_chronoscope": {
            "schema": "ProjectionChronoscopePacket.v1",
            "final_status": "ADVISORY_ONLY",
            "timeline_points": [
                {"timeline_point_id": "tp1", "ordinal": 0, "link_status": "LINKED"},
                {"timeline_point_id": "tp2", "ordinal": 1, "link_status": "LINKED"},
            ],
            "chronoscope_advisory_flags": ["advisory_only", "deterministic_timeline"],
            "drift_timeline": {"drift_event_count": 2},
            **_locked_flags(),
        },
        "read_only_transport": {
            "schema": "ReadOnlyTransportFeedPacket.v1",
            "final_status": "ADVISORY_ONLY",
            "frames": [
                {"frame_id": "f1", "blocker_status": "PRESENT"},
                {"frame_id": "f2", "blocker_status": "PRESENT"},
            ],
            "transport_advisory_flags": ["advisory_only", "transport_only"],
            **_locked_flags(),
        },
        "operator_action_queue": {
            "schema": "OperatorReviewQueue.v1",
            "operator_action_items": [
                {"item_id": "q1", "category": "drift_review"},
                {"item_id": "q2", "category": "render_blocker_review"},
            ],
            "queue_advisory_flags": ["advisory_only", "review_only"],
            **_locked_flags(),
        },
        "projection_bus": {
            "schema": "ProjectionBusEnvelope.v1",
            "messages": [{"message_id": "m1"}],
            **_locked_flags(),
        },
        "temporal_snapshot_spine": {
            "schema": "TemporalSnapshotIndex.v1",
            "ordered_snapshots": [{"snapshot_id": "s1"}],
            **_locked_flags(),
        },
    }


def _write_sources(tmp_path: Path, mutate: dict[str, dict[str, object]] | None = None) -> dict[str, str]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    payloads = _payloads()
    if mutate:
        payloads.update(mutate)
    paths: dict[str, str] = {}
    for key, payload in payloads.items():
        path = tmp_path / f"{key}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        paths[key] = path.as_posix()
    return paths


def test_stable_region_corridor_ordering_hash_and_markdown(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    packet_a = build_temporal_topology_cartography_packet(source_artifact_paths=sources)
    packet_b = build_temporal_topology_cartography_packet(source_artifact_paths=sources)
    assert [region["region_id"] for region in packet_a["atlas_regions"]] == [
        region["region_id"] for region in packet_b["atlas_regions"]
    ]
    assert [corridor["corridor_id"] for corridor in packet_a["atlas_corridors"]] == [
        corridor["corridor_id"] for corridor in packet_b["atlas_corridors"]
    ]
    assert packet_a["packet_hash"] == packet_b["packet_hash"]
    assert build_temporal_topology_cartography_markdown(packet_a) == build_temporal_topology_cartography_markdown(packet_b)


def test_metrics_invariants_and_no_source_mutation(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    before = {path: Path(path).read_text(encoding="utf-8") for path in sources.values()}
    packet = build_temporal_topology_cartography_packet(source_artifact_paths=sources)
    after = {path: Path(path).read_text(encoding="utf-8") for path in sources.values()}
    assert before == after

    assert packet["atlas_region_count"] > 0
    assert packet["atlas_corridor_count"] > 0
    assert 0.0 <= packet["topology_density_score"] <= 1.0
    density = packet["topology_density_field"]
    assert 0.0 <= density["topology_density_score"] <= 1.0
    assert 0.0 <= density["continuity_density_score"] <= 1.0
    assert 0.0 <= density["drift_accumulation_score"] <= 1.0
    assert packet["regime_boundary_summary"]["schema"] == "RegimeBoundarySummary.v1"
    assert packet["regime_atlas_summary"]["schema"] == "RegimeAtlasSummary.v1"
    assert packet["temporal_topology_index"]["schema"] == "TemporalTopologyIndex.v1"

    for key, expected in (
        ("advisory_only", True),
        ("analytics_only", True),
        ("cartography_only", True),
        ("visualization_support_only", True),
        ("detection_only", True),
        ("execution_authority", False),
        ("authority_granted", False),
        ("mutation_allowed", False),
        ("promotion_allowed", False),
        ("auto_execute", False),
        ("auto_approve", False),
        ("command_channel", False),
        ("bidirectional_control", False),
        ("inference_authority", False),
    ):
        assert packet[key] is expected


def test_region_and_corridor_classification_rules() -> None:
    assert _classify_region(
        blocked=False,
        not_computable=False,
        persistence_ratio=0.9,
        continuity_ratio=0.9,
        volatility_score=0.1,
        drift_score=0.0,
        evidence_count=5,
        advisory_flags=[],
    )[0] == "CONVERGENCE_REGION"
    assert _classify_region(
        blocked=False,
        not_computable=False,
        persistence_ratio=0.2,
        continuity_ratio=0.2,
        volatility_score=0.3,
        drift_score=0.0,
        evidence_count=5,
        advisory_flags=[],
    )[0] == "DIVERGENCE_REGION"
    assert _classify_region(
        blocked=False,
        not_computable=False,
        persistence_ratio=0.6,
        continuity_ratio=0.6,
        volatility_score=0.8,
        drift_score=0.0,
        evidence_count=5,
        advisory_flags=[],
    )[0] == "VOLATILE_REGION"
    assert _classify_region(
        blocked=False,
        not_computable=False,
        persistence_ratio=0.6,
        continuity_ratio=0.6,
        volatility_score=0.2,
        drift_score=0.8,
        evidence_count=5,
        advisory_flags=[],
    )[0] == "DRIFT_ZONE"
    assert _classify_region(
        blocked=False,
        not_computable=True,
        persistence_ratio=0.6,
        continuity_ratio=0.6,
        volatility_score=0.2,
        drift_score=0.0,
        evidence_count=1,
        advisory_flags=[],
    )[0] == NOT_COMPUTABLE
    assert _classify_region(
        blocked=True,
        not_computable=False,
        persistence_ratio=0.6,
        continuity_ratio=0.6,
        volatility_score=0.2,
        drift_score=0.0,
        evidence_count=5,
        advisory_flags=[],
    )[0] == BLOCKED
    assert _classify_region(
        blocked=False,
        not_computable=False,
        persistence_ratio=0.6,
        continuity_ratio=0.6,
        volatility_score=0.2,
        drift_score=0.0,
        evidence_count=5,
        advisory_flags=["queue_blocker_structure"],
    )[0] == "DEGRADED_REGION"

    assert _classify_corridor(
        blocked=False,
        not_computable=False,
        corridor_hint="replay",
        persistence_ratio=0.8,
        continuity_ratio=0.8,
        volatility_score=0.1,
        drift_score=0.0,
        replay_stability=0.9,
        transport_stability=0.6,
        evidence_count=4,
        advisory_flags=[],
    )[0] == "REPLAY_CORRIDOR"
    assert _classify_corridor(
        blocked=False,
        not_computable=False,
        corridor_hint="continuity",
        persistence_ratio=0.7,
        continuity_ratio=0.7,
        volatility_score=0.2,
        drift_score=0.0,
        replay_stability=0.5,
        transport_stability=0.8,
        evidence_count=4,
        advisory_flags=[],
    )[0] == "CONTINUITY_CORRIDOR"


def test_insufficient_evidence_not_computable_behavior(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    only_one = {
        "cross_run_topology_fusion": sources["cross_run_topology_fusion"],
    }
    packet = build_temporal_topology_cartography_packet(source_artifact_paths=only_one)
    assert packet["final_status"] == NOT_COMPUTABLE
    assert any(blocker.startswith("missing_artifact:") for blocker in packet["remaining_blockers"])


def test_authority_boundary_violation_blocked_behavior(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    payload = json.loads(Path(sources["cross_run_topology_fusion"]).read_text(encoding="utf-8"))
    payload["authority_granted"] = True
    Path(sources["cross_run_topology_fusion"]).write_text(
        json.dumps(payload), encoding="utf-8"
    )
    packet = build_temporal_topology_cartography_packet(source_artifact_paths=sources)
    assert packet["final_status"] == BLOCKED
    assert any("authority_boundary_violation:" in blocker for blocker in packet["remaining_blockers"])


def test_hash_not_computable_blocks_when_source_present(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    with patch("core.temporal_topology_cartography._safe_hash", return_value=None):
        packet = build_temporal_topology_cartography_packet(source_artifact_paths=sources)
    assert packet["final_status"] == BLOCKED
    assert any(blocker.startswith("hash_not_computable:") for blocker in packet["remaining_blockers"])


def test_missing_and_corrupt_artifact_fail_closed(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    Path(sources["multi_run_convergence"]).unlink()
    corrupt_path = Path(sources["temporal_state_diff"])
    corrupt_path.write_text("{not json", encoding="utf-8")
    packet = build_temporal_topology_cartography_packet(source_artifact_paths=sources)
    assert packet["final_status"] == NOT_COMPUTABLE
    assert any(
        blocker.startswith("missing_artifact:") or blocker.startswith("corrupt_artifact:")
        for blocker in packet["remaining_blockers"]
    )


def test_writer_markdown_and_summary(tmp_path: Path) -> None:
    packet = build_temporal_topology_cartography_packet(
        source_artifact_paths=_write_sources(tmp_path)
    )
    out_path = tmp_path / "temporal_topology_cartography.json"
    write_temporal_topology_cartography_packet(out_path, packet)
    markdown = build_temporal_topology_cartography_markdown(packet)
    summary = summarize_temporal_topology_cartography(packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
    assert "Temporal Topology Cartography" in markdown
    assert "Operator Next Actions" in markdown
    assert summary["temporal_topology_cartography_status"] == packet["final_status"]
    assert summary["atlas_region_count"] == packet["atlas_region_count"]
    assert summarize_temporal_topology_cartography(None)["atlas_region_count"] == 0


def test_run_script_writes_artifacts(tmp_path: Path) -> None:
    runtime_paths = run_temporal_topology_cartography.RuntimePaths(
        contracts_dir=tmp_path / "contracts",
        out_dir=tmp_path / "out",
    )
    sources = _write_sources(tmp_path / "sources")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(sources, sort_keys=True), encoding="utf-8")

    with (
        patch.object(run_temporal_topology_cartography, "_PATHS", runtime_paths),
        patch.object(
            run_temporal_topology_cartography,
            "OUT_PATH",
            runtime_paths.temporal_topology_cartography_latest,
        ),
    ):
        run_temporal_topology_cartography.main(["--manifest", manifest.as_posix()])

    assert runtime_paths.temporal_topology_cartography_latest.exists()
    assert runtime_paths.temporal_topology_cartography_latest.with_suffix(".md").exists()


def test_no_runtime_replay_canon_projection_render_operator_transport_mutation(
    tmp_path: Path,
) -> None:
    payloads = _payloads()
    before = deepcopy(payloads)
    sources = _write_sources(tmp_path, mutate=payloads)
    build_temporal_topology_cartography_packet(source_artifact_paths=sources)
    assert payloads == before

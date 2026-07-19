from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from core.cross_run_topology_fusion import (
    BLOCKED,
    NOT_COMPUTABLE,
    _classify_motif,
    build_cross_run_topology_fusion_markdown,
    build_cross_run_topology_fusion_packet,
    write_cross_run_topology_fusion_packet,
)
from scripts.temporal import run_cross_run_topology_fusion


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
        "multi_run_convergence": {
            "schema": "MultiRunConvergencePacket.v1",
            "multi_run_convergence_status": "ADVISORY_ONLY",
            "run_observations": [
                {
                    "run_id": "run-a",
                    "packet_id": "pkt-a",
                    "timestamp_or_sequence": "t:001",
                    "source_hash": "h-a",
                    "source_artifact": "surface-a",
                    "final_status": "ADVISORY_ONLY",
                    "advisory_flags": ["advisory_only"],
                },
                {
                    "run_id": "run-b",
                    "packet_id": "pkt-b",
                    "timestamp_or_sequence": "t:002",
                    "source_hash": "h-b",
                    "source_artifact": "surface-b",
                    "final_status": "ADVISORY_ONLY",
                    "advisory_flags": ["advisory_only"],
                },
                {
                    "run_id": "run-c",
                    "packet_id": "pkt-c",
                    "timestamp_or_sequence": "t:003",
                    "source_hash": "h-c",
                    "source_artifact": "surface-c",
                    "final_status": "ADVISORY_ONLY",
                    "advisory_flags": ["advisory_only"],
                },
            ],
            **_locked_flags(),
        },
        "temporal_state_diff": {
            "schema": "TemporalStateDiff.v1",
            "temporal_state_diff_status": "ADVISORY_ONLY",
            "diff_advisory_flags": ["advisory_only", "diff_only", "detection_only"],
            "diff_entries": [
                {
                    "entry_id": "diff-1",
                    "source_surface": "projection_bus",
                    "change_type": "TOPOLOGY_SHIFT",
                },
                {
                    "entry_id": "diff-2",
                    "source_surface": "projection_bus",
                    "change_type": "LINEAGE_SHIFT",
                },
                {
                    "entry_id": "diff-3",
                    "source_surface": "projection_chronoscope",
                    "change_type": "QUEUE_DELTA",
                },
            ],
            **_locked_flags(),
        },
        "aal_viz_graph_render_packet": {
            "schema": "AALVizGraphRenderPacket.v1",
            "render_advisory_flags": ["advisory_only", "render_only"],
            "nodes": [
                {"node_id": "n2", "category": "replay_node", "status": "PRESENT"},
                {"node_id": "n1", "category": "replay_node", "status": "PRESENT"},
            ],
            "edges": [
                {
                    "edge_id": "e1",
                    "category": "message_edge",
                    "source_node_id": "n1",
                    "target_node_id": "n2",
                }
            ],
            **_locked_flags(),
        },
        "projection_chronoscope": {
            "schema": "ProjectionChronoscopePacket.v1",
            "chronoscope_advisory_flags": ["advisory_only", "deterministic_timeline"],
            "timeline_points": [
                {
                    "timeline_point_id": "tp1",
                    "ordinal": 0,
                    "snapshot_id": "s1",
                    "message_id": "m1",
                    "lineage_prev": None,
                    "link_status": "LINKED",
                },
                {
                    "timeline_point_id": "tp2",
                    "ordinal": 1,
                    "snapshot_id": "s2",
                    "message_id": "m2",
                    "lineage_prev": "s1",
                    "link_status": "LINKED",
                },
            ],
            "playback_cursors": [
                {"cursor": "c1", "next_cursor": "c2", "ordinal": 0},
                {"cursor": "c2", "next_cursor": None, "ordinal": 1},
            ],
            **_locked_flags(),
        },
        "read_only_transport": {
            "schema": "ReadOnlyTransportFeedPacket.v1",
            "transport_advisory_flags": ["advisory_only", "transport_only"],
            "topics": [
                {"topic_id": "t1", "topic_name": "projection.runtime"},
                {"topic_id": "t2", "topic_name": "projection.chronoscope"},
            ],
            "frames": [
                {
                    "frame_id": "f1",
                    "sequence_number": 1,
                    "topic_id": "t1",
                    "blocker_status": "PRESENT",
                    "advisory_flags": ["advisory_only"],
                },
                {
                    "frame_id": "f2",
                    "sequence_number": 2,
                    "topic_id": "t2",
                    "blocker_status": "PRESENT",
                    "advisory_flags": ["advisory_only"],
                },
            ],
            **_locked_flags(),
        },
        "operator_action_queue": {
            "schema": "OperatorReviewQueue.v1",
            "queue_advisory_flags": ["advisory_only", "review_only"],
            "operator_action_items": [
                {
                    "item_id": "q1",
                    "category": "missing_artifact_review",
                    "severity": "HIGH",
                    "source_artifact": "a.json",
                },
                {
                    "item_id": "q2",
                    "category": "render_blocker_review",
                    "severity": "LOW",
                    "source_artifact": "b.json",
                },
            ],
            "escalation_paths": [
                {
                    "escalation_id": "esc-1",
                    "related_action_item_ids": ["q1", "q2"],
                }
            ],
            **_locked_flags(),
        },
        "projection_bus": {
            "schema": "ProjectionBusEnvelope.v1",
            "messages": [
                {
                    "message_id": "m1",
                    "topic": "projection.runtime",
                    "snapshot_id": "s1",
                    "advisory_flags": ["advisory_only"],
                }
            ],
            **_locked_flags(),
        },
        "temporal_snapshot_spine": {
            "schema": "TemporalSnapshotIndex.v1",
            "ordered_snapshots": [
                {
                    "snapshot_id": "s1",
                    "ordinal": 0,
                    "status": "PRESENT",
                    "projection_id": "p1",
                    "projection_hash": "ph1",
                    "lineage_prev": None,
                },
                {
                    "snapshot_id": "s2",
                    "ordinal": 1,
                    "status": "PRESENT",
                    "projection_id": "p2",
                    "projection_hash": "ph2",
                    "lineage_prev": "s1",
                },
            ],
            **_locked_flags(),
        },
        "temporal_state_diff_pulse_ledger": {
            "schema_version": "TemporalStateDiffPulseLedger.v1",
            "entries": [
                {"pulse_ordinal": 1, "entry_hash": "pulse-1", "temporal_state_diff_hash": "h1"},
                {"pulse_ordinal": 2, "entry_hash": "pulse-2", "temporal_state_diff_hash": "h2"},
            ],
            **_locked_flags(),
        },
        "temporal_lineage_pulse_ledger": {
            "schema_version": "TemporalLineagePulseLedger.v1",
            "entries": [
                {"pulse_ordinal": 1, "entry_hash": "lineage-pulse-1", "lineage_hash": "lh1"},
                {"pulse_ordinal": 2, "entry_hash": "lineage-pulse-2", "lineage_hash": "lh2"},
            ],
            **_locked_flags(),
        },
    }


def _write_sources(tmp_path: Path, *, mutate: dict[str, dict[str, object]] | None = None) -> dict[str, str]:
    payloads = _payloads()
    if mutate:
        payloads.update(mutate)
    paths: dict[str, str] = {}
    for key, payload in payloads.items():
        path = tmp_path / f"{key}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        paths[key] = path.as_posix()
    return paths


def test_stable_node_edge_ordering_packet_hash_and_markdown(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    packet_a = build_cross_run_topology_fusion_packet(source_artifact_paths=sources)
    packet_b = build_cross_run_topology_fusion_packet(source_artifact_paths=sources)
    assert [node["node_id"] for node in packet_a["fusion_nodes"]] == [
        node["node_id"] for node in packet_b["fusion_nodes"]
    ]
    assert [edge["edge_id"] for edge in packet_a["fusion_edges"]] == [
        edge["edge_id"] for edge in packet_b["fusion_edges"]
    ]
    assert packet_a["packet_hash"] == packet_b["packet_hash"]
    assert build_cross_run_topology_fusion_markdown(packet_a) == build_cross_run_topology_fusion_markdown(packet_b)


def test_metrics_and_invariants_and_no_source_mutation(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    before = {path: Path(path).read_text(encoding="utf-8") for path in sources.values()}
    packet = build_cross_run_topology_fusion_packet(source_artifact_paths=sources)
    after = {path: Path(path).read_text(encoding="utf-8") for path in sources.values()}
    assert before == after

    assert packet["fusion_node_count"] > 0
    assert packet["fusion_edge_count"] > 0
    assert packet["lineage_corridor_count"] >= 1
    assert any(edge.get("edge_kind") == "lineage_pulse_lineage_edge" for edge in packet["fusion_edges"])
    assert packet["replay_continuity_status"] in {"ADVISORY_ONLY", NOT_COMPUTABLE}
    assert packet["transport_continuity_status"] in {"ADVISORY_ONLY", NOT_COMPUTABLE}
    assert packet["drift_corridor_summary"]["schema"] == "DriftCorridorSummary.v1"
    assert packet["topology_stability_score"] >= 0.0

    for key, expected in (
        ("advisory_only", True),
        ("analytics_only", True),
        ("fusion_only", True),
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


def test_motif_classifications() -> None:
    assert _classify_motif(
        recurrence_count=4,
        persistence_ratio=0.9,
        continuity_ratio=0.9,
        volatility_score=0.1,
        evidence_count=4,
        blocked=False,
        degraded=False,
    )[0] == "PERSISTENT"
    assert _classify_motif(
        recurrence_count=2,
        persistence_ratio=0.6,
        continuity_ratio=0.6,
        volatility_score=0.4,
        evidence_count=4,
        blocked=False,
        degraded=False,
    )[0] == "RECURRING"
    assert _classify_motif(
        recurrence_count=1,
        persistence_ratio=0.3,
        continuity_ratio=0.2,
        volatility_score=0.3,
        evidence_count=4,
        blocked=False,
        degraded=False,
    )[0] == "TRANSIENT"
    assert _classify_motif(
        recurrence_count=3,
        persistence_ratio=0.5,
        continuity_ratio=0.3,
        volatility_score=0.8,
        evidence_count=4,
        blocked=False,
        degraded=False,
    )[0] == "VOLATILE"
    assert _classify_motif(
        recurrence_count=2,
        persistence_ratio=0.6,
        continuity_ratio=0.6,
        volatility_score=0.5,
        evidence_count=4,
        blocked=False,
        degraded=True,
    )[0] == "DEGRADED"
    classification, blockers = _classify_motif(
        recurrence_count=1,
        persistence_ratio=0.1,
        continuity_ratio=0.1,
        volatility_score=0.9,
        evidence_count=1,
        blocked=False,
        degraded=False,
    )
    assert classification == NOT_COMPUTABLE
    assert "insufficient_fusion_evidence" in blockers
    classification, blockers = _classify_motif(
        recurrence_count=3,
        persistence_ratio=0.8,
        continuity_ratio=0.8,
        volatility_score=0.2,
        evidence_count=3,
        blocked=True,
        degraded=False,
    )
    assert classification == BLOCKED
    assert "authority_boundary_violation" in blockers


def test_missing_and_corrupt_sources_fail_closed(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    missing = dict(sources)
    missing["temporal_state_diff"] = (tmp_path / "missing.json").as_posix()
    packet_missing = build_cross_run_topology_fusion_packet(source_artifact_paths=missing)
    assert packet_missing["final_status"] == NOT_COMPUTABLE
    assert any(
        str(blocker).startswith("missing_artifact:")
        for blocker in packet_missing["remaining_blockers"]
    )

    corrupt = dict(sources)
    corrupt_path = tmp_path / "corrupt.json"
    corrupt_path.write_text("{", encoding="utf-8")
    corrupt["temporal_state_diff"] = corrupt_path.as_posix()
    packet_corrupt = build_cross_run_topology_fusion_packet(source_artifact_paths=corrupt)
    assert packet_corrupt["final_status"] == NOT_COMPUTABLE
    assert any(
        str(blocker).startswith("corrupt_artifact:")
        for blocker in packet_corrupt["remaining_blockers"]
    )


def test_authority_violation_and_hash_not_computable_blocked(tmp_path: Path) -> None:
    sources = _write_sources(
        tmp_path,
        mutate={"read_only_transport": {**_payloads()["read_only_transport"], "authority_granted": True}},
    )
    packet = build_cross_run_topology_fusion_packet(source_artifact_paths=sources)
    assert packet["final_status"] == BLOCKED
    assert any(
        str(blocker).startswith("authority_boundary_violation:")
        for blocker in packet["remaining_blockers"]
    )

    with patch("core.cross_run_topology_fusion._safe_hash", return_value=None):
        blocked_packet = build_cross_run_topology_fusion_packet(source_artifact_paths=sources)
    assert blocked_packet["final_status"] == BLOCKED
    assert any(
        str(blocker).startswith("hash_not_computable:")
        for blocker in blocked_packet["remaining_blockers"]
    )
    assert all(entry["source_hash"] is None for entry in blocked_packet["source_entries"])
    assert all(node["source_hashes"] == [] for node in blocked_packet["fusion_nodes"])


def test_writer_and_run_script(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    packet = build_cross_run_topology_fusion_packet(source_artifact_paths=sources)
    out_path = tmp_path / "cross_run_topology_fusion.json"
    write_cross_run_topology_fusion_packet(out_path, packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")

    runtime_paths = run_cross_run_topology_fusion.RuntimePaths(
        contracts_dir=tmp_path / "contracts", out_dir=tmp_path / "out"
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(sources), encoding="utf-8")

    with (
        patch.object(run_cross_run_topology_fusion, "_PATHS", runtime_paths),
        patch.object(
            run_cross_run_topology_fusion,
            "OUT_PATH",
            runtime_paths.cross_run_topology_fusion_latest,
        ),
    ):
        run_cross_run_topology_fusion.main(["--manifest", manifest.as_posix()])

    assert runtime_paths.cross_run_topology_fusion_latest.exists()
    assert runtime_paths.cross_run_topology_fusion_latest.with_suffix(".md").exists()

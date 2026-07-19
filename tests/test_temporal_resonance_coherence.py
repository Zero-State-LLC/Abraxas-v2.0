from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from core.generated_artifact_registry import (
    build_generated_artifact_registry,
    list_ci_drift_artifact_paths,
)
from core.temporal_resonance_coherence import (
    BLOCKED,
    NOT_COMPUTABLE,
    build_temporal_resonance_coherence_markdown,
    build_temporal_resonance_coherence_packet,
    summarize_temporal_resonance_coherence,
    write_temporal_resonance_coherence_packet,
)
from scripts.temporal import run_temporal_resonance_coherence


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


def _payloads() -> dict[str, dict[str, Any]]:
    return {
        "temporal_persistence_memory": {
            "schema": "TemporalPersistenceMemoryPacket.v1",
            "aggregate_memory_score": 0.68,
            "decay_score": 0.32,
            "memory_zones": [{"zone_id": "m1"}],
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "temporal_stability_pressure": {
            "schema": "TemporalStabilityPressurePacket.v1",
            "aggregate_stress_score": 0.22,
            "transition_pressure_gradient_score": 0.31,
            "pressure_zones": [{"zone_id": "p1"}],
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "temporal_regime_transition": {
            "schema": "TemporalRegimeTransitionPacket.v1",
            "phase_boundary_count": 4,
            "phase_shift_count": 3,
            "drift_escalation_boundary_count": 1,
            "transition_density_metrics": {"transition_density_score": 0.72},
            "replay_collapse_status": "ADVISORY_ONLY",
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "temporal_topology_cartography": {
            "schema": "TemporalTopologyAtlas.v1",
            "topology_density_score": 0.73,
            "atlas_corridor_count": 4,
            "atlas_regions": [{"region_id": "r1"}],
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "cross_run_topology_fusion": {
            "schema": "CrossRunTopologyFusionPacket.v1",
            "topology_stability_score": 0.76,
            "lineage_corridor_count": 3,
            "replay_continuity_status": "ADVISORY_ONLY",
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "multi_run_convergence": {
            "schema": "MultiRunConvergencePacket.v1",
            "topology_persistence_ratio": 0.74,
            "lineage_persistence_ratio": 0.69,
            "replay_stability_status": "ADVISORY_ONLY",
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "temporal_state_diff": {
            "schema": "TemporalStateDiff.v1",
            "drift_acceleration_status": "ADVISORY_ONLY",
            "drift_acceleration_ratio": 0.15,
            "replay_equivalence_change_status": "NO_CHANGE",
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "aal_viz_graph_render_packet": {
            "schema": "AALVizGraphRenderPacket.v1",
            "render_blocker_count": 0,
            "render_layer_count": 5,
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "projection_chronoscope": {
            "schema": "ProjectionChronoscopePacket.v1",
            "timeline_point_count": 5,
            "lineage_evolution": {"lineage_status": "PRESENT"},
            "drift_timeline": {"drift_event_count": 0},
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "read_only_transport": {
            "schema": "ReadOnlyTransportFeedPacket.v1",
            "read_only_transport_status": "ADVISORY_ONLY",
            "final_status": "ADVISORY_ONLY",
            "transport_frame_count": 8,
            "transport_blocker_count": 0,
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "operator_action_queue": {
            "schema": "OperatorReviewQueue.v1",
            "final_status": "ADVISORY_ONLY",
            "remaining_blockers": [],
            **_locked_flags(),
        },
    }


def _write_sources(
    tmp_path: Path, mutate: dict[str, dict[str, Any]] | None = None
) -> dict[str, str]:
    payloads = _payloads()
    if mutate:
        payloads.update(mutate)
    tmp_path.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}
    for key, payload in payloads.items():
        path = tmp_path / f"{key}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        paths[key] = path.as_posix()
    return paths


def test_deterministic_ordering_hashes_markdown_and_bounded_metrics(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    packet_a = build_temporal_resonance_coherence_packet(source_artifact_paths=sources)
    packet_b = build_temporal_resonance_coherence_packet(source_artifact_paths=sources)
    assert packet_a["packet_hash"] == packet_b["packet_hash"]
    assert [zone["zone_id"] for zone in packet_a["coherence_zones"]] == [
        zone["zone_id"] for zone in packet_b["coherence_zones"]
    ]
    assert build_temporal_resonance_coherence_markdown(
        packet_a
    ) == build_temporal_resonance_coherence_markdown(packet_b)
    for key in (
        "aggregate_coherence_score",
        "resonance_score",
        "dissonance_score",
    ):
        assert 0.0 <= packet_a[key] <= 1.0
    for zone in packet_a["coherence_zones"]:
        assert 0.0 <= zone["coherence_score"] <= 1.0
        assert 0.0 <= zone["resonance_score"] <= 1.0
        assert 0.0 <= zone["dissonance_score"] <= 1.0


def test_classification_and_invariants(tmp_path: Path) -> None:
    packet = build_temporal_resonance_coherence_packet(
        source_artifact_paths=_write_sources(tmp_path)
    )
    assert packet["phase_alignment_bucket"] in {
        "LOW",
        "MODERATE",
        "HIGH",
        "LOCKED",
        NOT_COMPUTABLE,
        BLOCKED,
    }
    assert packet["coherence_zone_count"] == len(packet["coherence_zones"])
    assert packet["dominant_coherence_component"] in {
        "topology_alignment",
        "lineage_alignment",
        "replay_resonance",
        "transition_alignment",
        "pressure_memory_alignment",
        "drift_alignment",
        "transport_alignment",
        NOT_COMPUTABLE,
    }
    assert packet["advisory_only"] is True
    assert packet["analytics_only"] is True
    assert packet["resonance_only"] is True
    assert packet["coherence_field_only"] is True
    assert packet["detection_only"] is True
    assert packet["visualization_support_only"] is True
    assert packet["execution_authority"] is False
    assert packet["authority_granted"] is False
    assert packet["mutation_allowed"] is False
    assert packet["promotion_allowed"] is False
    assert packet["auto_execute"] is False
    assert packet["auto_approve"] is False
    assert packet["command_channel"] is False
    assert packet["bidirectional_control"] is False
    assert packet["inference_authority"] is False


def test_missing_and_corrupt_sources_fail_closed(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    Path(sources["multi_run_convergence"]).unlink()
    Path(sources["temporal_state_diff"]).write_text("{bad json", encoding="utf-8")
    packet = build_temporal_resonance_coherence_packet(source_artifact_paths=sources)
    assert packet["final_status"] == NOT_COMPUTABLE
    assert any(
        blocker.startswith("missing_artifact:") or blocker.startswith("corrupt_artifact:")
        for blocker in packet["remaining_blockers"]
    )


def test_authority_boundary_violation_blocks(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    payload = json.loads(Path(sources["read_only_transport"]).read_text(encoding="utf-8"))
    payload["authority_granted"] = True
    Path(sources["read_only_transport"]).write_text(json.dumps(payload), encoding="utf-8")
    packet = build_temporal_resonance_coherence_packet(source_artifact_paths=sources)
    assert packet["final_status"] == BLOCKED
    assert "authority_boundary_violation" in packet["coherence_advisory_flags"]
    assert any("authority_boundary_violation:" in b for b in packet["remaining_blockers"])


def test_insufficient_evidence_not_computable(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    packet = build_temporal_resonance_coherence_packet(
        source_artifact_paths={"temporal_regime_transition": sources["temporal_regime_transition"]}
    )
    assert packet["final_status"] == NOT_COMPUTABLE
    assert "remaining_blocker: insufficient_coherence_evidence" in packet["remaining_blockers"]
    assert any(zone["zone_kind"] == NOT_COMPUTABLE for zone in packet["coherence_zones"])


def test_build_does_not_mutate_sources_writer_and_summary(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    before = {path: Path(path).read_text(encoding="utf-8") for path in sources.values()}
    packet = build_temporal_resonance_coherence_packet(source_artifact_paths=sources)
    after = {path: Path(path).read_text(encoding="utf-8") for path in sources.values()}
    assert before == after

    out_path = tmp_path / "temporal_resonance_coherence.json"
    write_temporal_resonance_coherence_packet(out_path, packet)
    markdown = build_temporal_resonance_coherence_markdown(packet)
    summary = summarize_temporal_resonance_coherence(packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
    assert "Temporal Resonance Coherence" in markdown
    assert "Operator Next Actions" in markdown
    assert summary["temporal_resonance_coherence_status"] == packet["final_status"]
    assert summarize_temporal_resonance_coherence(None)["coherence_zone_count"] == 0


def test_run_script_writes_artifacts(tmp_path: Path) -> None:
    runtime_paths = run_temporal_resonance_coherence.RuntimePaths(
        contracts_dir=tmp_path / "contracts",
        out_dir=tmp_path / "out",
    )
    sources = _write_sources(tmp_path / "sources")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(sources, sort_keys=True), encoding="utf-8")
    with (
        patch.object(run_temporal_resonance_coherence, "_PATHS", runtime_paths),
        patch.object(
            run_temporal_resonance_coherence,
            "OUT_PATH",
            runtime_paths.temporal_resonance_coherence_latest,
        ),
    ):
        run_temporal_resonance_coherence.main(["--manifest", manifest.as_posix()])
    assert runtime_paths.temporal_resonance_coherence_latest.exists()
    assert runtime_paths.temporal_resonance_coherence_latest.with_suffix(".md").exists()


def test_artifact_registry_classification_and_ci_drift_scope() -> None:
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path
        == "out/projections/temporal_resonance_coherence_001.latest.json"
    )
    assert entry.canonical_generator == "scripts/temporal/run_temporal_resonance_coherence.py"
    assert entry.determinism_class == "DERIVED_OPTIONAL"
    assert (
        "out/projections/temporal_resonance_coherence_001.latest.json"
        not in list_ci_drift_artifact_paths(registry)
    )

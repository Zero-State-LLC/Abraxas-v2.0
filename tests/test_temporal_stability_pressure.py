from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from core.generated_artifact_registry import build_generated_artifact_registry
from core.temporal_stability_pressure import (
    BLOCKED,
    NOT_COMPUTABLE,
    build_temporal_stability_pressure_markdown,
    build_temporal_stability_pressure_packet,
    summarize_temporal_stability_pressure,
    write_temporal_stability_pressure_packet,
)
from scripts.temporal import run_temporal_stability_pressure


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
        "temporal_regime_transition": {
            "schema": "TemporalRegimeTransitionPacket.v1",
            "phase_boundary_count": 3,
            "phase_shift_count": 2,
            "drift_escalation_boundary_count": 2,
            "phase_boundaries": [
                {"boundary_id": "b1", "velocity_score": 0.8},
                {"boundary_id": "b2", "velocity_score": 0.6},
            ],
            "transition_density_metrics": {"transition_density_score": 0.7},
            "continuity_fracture_report": {"fracture_count": 4, "fracture_status": "ADVISORY_ONLY"},
            "replay_collapse_report": {"signal_count": 3, "collapse_status": "COLLAPSE_WATCH"},
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "temporal_topology_cartography": {
            "schema": "TemporalTopologyAtlas.v1",
            "atlas_region_count": 4,
            "atlas_corridor_count": 3,
            "volatile_region_count": 2,
            "topology_density_score": 0.45,
            "atlas_regions": [
                {"region_id": "r1", "drift_score": 0.1, "volatility_score": 0.2, "continuity_ratio": 0.9},
                {"region_id": "r2", "drift_score": 0.7, "volatility_score": 0.8, "continuity_ratio": 0.3},
            ],
            "atlas_corridors": [
                {"corridor_id": "c1", "drift_score": 0.6, "volatility_score": 0.5, "continuity_ratio": 0.4}
            ],
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "cross_run_topology_fusion": {
            "schema": "CrossRunTopologyFusionPacket.v1",
            "topology_stability_score": 0.4,
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "multi_run_convergence": {
            "schema": "MultiRunConvergencePacket.v1",
            "topology_persistence_ratio": 0.35,
            "lineage_persistence_ratio": 0.25,
            "drift_persistence_ratio": 0.3,
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "temporal_state_diff": {
            "schema": "TemporalStateDiff.v1",
            "drift_acceleration_status": "DRIFT_ACCELERATING",
            "replay_equivalence_change_status": "SHIFT_DETECTED",
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "aal_viz_graph_render_packet": {
            "schema": "AALVizGraphRenderPacket.v1",
            "final_status": "ADVISORY_ONLY",
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "projection_chronoscope": {
            "schema": "ProjectionChronoscopePacket.v1",
            "drift_timeline": {"drift_event_count": 2},
            "remaining_blockers": [],
            **_locked_flags(),
        },
        "read_only_transport": {
            "schema": "ReadOnlyTransportFeedPacket.v1",
            "transport_frame_count": 10,
            "transport_stability_status": "ADVISORY_ONLY",
            "ledger": {
                "not_computable_summary": {"not_computable_frame_count": 1},
                "blocker_summary": {"blocked_frame_count": 2},
            },
            "final_status": "ADVISORY_ONLY",
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


def _write_sources(tmp_path: Path, mutate: dict[str, dict[str, Any]] | None = None) -> dict[str, str]:
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


def test_deterministic_ordering_hashes_and_markdown(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    packet_a = build_temporal_stability_pressure_packet(source_artifact_paths=sources)
    packet_b = build_temporal_stability_pressure_packet(source_artifact_paths=sources)
    assert packet_a["packet_hash"] == packet_b["packet_hash"]
    assert [zone["zone_id"] for zone in packet_a["pressure_zones"]] == [
        zone["zone_id"] for zone in packet_b["pressure_zones"]
    ]
    assert build_temporal_stability_pressure_markdown(packet_a) == build_temporal_stability_pressure_markdown(packet_b)


def test_bounded_metrics_resilience_and_invariants(tmp_path: Path) -> None:
    packet = build_temporal_stability_pressure_packet(
        source_artifact_paths=_write_sources(tmp_path)
    )
    assert 0.0 <= packet["aggregate_stress_score"] <= 1.0
    assert 0.0 <= packet["resilience_score"] <= 1.0
    assert packet["resilience_score"] == round(1.0 - packet["aggregate_stress_score"], 6)
    assert 0.0 <= packet["transition_pressure_gradient_score"] <= 1.0
    assert packet["advisory_only"] is True
    assert packet["analytics_only"] is True
    assert packet["pressure_only"] is True
    assert packet["stress_tensor_only"] is True
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


def test_classification_correctness_for_continuity_strain(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    packet = build_temporal_stability_pressure_packet(source_artifact_paths=sources)
    assert packet["dominant_pressure_component"] in {
        "topology_stress",
        "continuity_stress",
        "replay_stress",
        "drift_stress",
        "transport_stress",
        "blocker_stress",
        "volatility_stress",
    }
    assert packet["pressure_zone_count"] >= 1
    assert packet["critical_pressure_count"] >= 0
    assert packet["strain_zone_count"] >= 0
    assert packet["collapse_pressure_zone_count"] >= 0
    assert packet["drift_load_zone_count"] >= 0


def test_missing_and_corrupt_sources_fail_closed(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    Path(sources["multi_run_convergence"]).unlink()
    Path(sources["temporal_state_diff"]).write_text("{not json", encoding="utf-8")
    packet = build_temporal_stability_pressure_packet(source_artifact_paths=sources)
    assert packet["final_status"] == NOT_COMPUTABLE
    assert any(
        blocker.startswith("missing_artifact:") or blocker.startswith("corrupt_artifact:")
        for blocker in packet["remaining_blockers"]
    )


def test_authority_boundary_violation_blocks(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    payload = json.loads(Path(sources["cross_run_topology_fusion"]).read_text(encoding="utf-8"))
    payload["authority_granted"] = True
    Path(sources["cross_run_topology_fusion"]).write_text(json.dumps(payload), encoding="utf-8")
    packet = build_temporal_stability_pressure_packet(source_artifact_paths=sources)
    assert packet["final_status"] == BLOCKED
    assert "authority_boundary_violation" in packet["pressure_advisory_flags"]
    assert any("authority_boundary_violation:" in blocker for blocker in packet["remaining_blockers"])


def test_insufficient_evidence_not_computable(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    packet = build_temporal_stability_pressure_packet(
        source_artifact_paths={"temporal_regime_transition": sources["temporal_regime_transition"]}
    )
    assert packet["final_status"] == NOT_COMPUTABLE
    assert "remaining_blocker: insufficient_pressure_evidence" in packet["remaining_blockers"]
    assert any(zone["zone_kind"] == NOT_COMPUTABLE for zone in packet["pressure_zones"])


def test_build_does_not_mutate_sources_and_writer_summary(tmp_path: Path) -> None:
    sources = _write_sources(tmp_path)
    before = {path: Path(path).read_text(encoding="utf-8") for path in sources.values()}
    packet = build_temporal_stability_pressure_packet(source_artifact_paths=sources)
    after = {path: Path(path).read_text(encoding="utf-8") for path in sources.values()}
    assert before == after

    out_path = tmp_path / "temporal_stability_pressure.json"
    write_temporal_stability_pressure_packet(out_path, packet)
    markdown = build_temporal_stability_pressure_markdown(packet)
    summary = summarize_temporal_stability_pressure(packet)
    assert out_path.read_text(encoding="utf-8").endswith("\n")
    assert "Temporal Stability Pressure" in markdown
    assert "Operator Next Actions" in markdown
    assert summary["temporal_stability_pressure_status"] == packet["final_status"]
    assert summarize_temporal_stability_pressure(None)["pressure_zone_count"] == 0


def test_run_script_writes_artifacts(tmp_path: Path) -> None:
    runtime_paths = run_temporal_stability_pressure.RuntimePaths(
        contracts_dir=tmp_path / "contracts",
        out_dir=tmp_path / "out",
    )
    sources = _write_sources(tmp_path / "sources")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(sources, sort_keys=True), encoding="utf-8")
    with (
        patch.object(run_temporal_stability_pressure, "_PATHS", runtime_paths),
        patch.object(
            run_temporal_stability_pressure,
            "OUT_PATH",
            runtime_paths.temporal_stability_pressure_latest,
        ),
    ):
        run_temporal_stability_pressure.main(["--manifest", manifest.as_posix()])
    assert runtime_paths.temporal_stability_pressure_latest.exists()
    assert runtime_paths.temporal_stability_pressure_latest.with_suffix(".md").exists()


def test_artifact_registry_classification_and_ci_drift_scope() -> None:
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    entry = next(
        item
        for item in registry.entries
        if item.artifact_path
        == "out/projections/temporal_stability_pressure_001.latest.json"
    )
    assert entry.canonical_generator == "scripts/temporal/run_temporal_stability_pressure.py"
    assert entry.determinism_class == "DERIVED_OPTIONAL"

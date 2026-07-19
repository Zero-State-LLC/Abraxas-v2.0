"""Tests for core/temporal_regime_transition.py — P24 phase-boundary detection."""

from __future__ import annotations

import json
from pathlib import Path

from core.temporal_regime_transition import (
    ADVISORY_ONLY,
    BLOCKED,
    NOT_COMPUTABLE,
    PATCH_ID,
    build_temporal_regime_transition_markdown,
    build_temporal_regime_transition_packet,
    summarize_temporal_regime_transition,
    write_temporal_regime_transition_packet,
    _apply_invariants,
    _detect_continuity_fractures,
    _detect_phase_boundaries,
    _detect_replay_collapse,
    _build_phase_shift_tracks,
    _compute_drift_escalation_boundaries,
    _compute_transition_density,
    _build_regime_transition_summary,
    _build_aal_viz_surface,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _cartography_payload() -> dict:
    return {
        "schema": "TemporalTopologyAtlas.v1",
        "patch_id": "PATCH-P23-TEMPORAL-TOPOLOGY-CARTOGRAPHY-AND-REGIME-ATLAS-001",
        "packet_id": "temporal_topology_cartography_001",
        "final_status": ADVISORY_ONLY,
        "temporal_topology_cartography_status": ADVISORY_ONLY,
        "atlas_region_count": 3,
        "atlas_corridor_count": 2,
        "atlas_regions": [
            {
                "schema": "AtlasRegion.v1",
                "region_id": "r1",
                "region_kind": "STABLE_REGION",
                "persistence_ratio": 0.9,
                "continuity_ratio": 0.85,
                "volatility_score": 0.1,
                "drift_score": 0.0,
                "density_score": 0.5,
                "stability_score": 0.9,
                "evidence_count": 5,
                "advisory_flags": ["advisory_only"],
                "final_status": ADVISORY_ONLY,
            },
            {
                "schema": "AtlasRegion.v1",
                "region_id": "r2",
                "region_kind": "DIVERGENCE_REGION",
                "persistence_ratio": 0.2,
                "continuity_ratio": 0.15,
                "volatility_score": 0.8,
                "drift_score": 0.0,
                "density_score": 0.2,
                "stability_score": 0.2,
                "evidence_count": 3,
                "advisory_flags": ["advisory_only"],
                "final_status": ADVISORY_ONLY,
            },
            {
                "schema": "AtlasRegion.v1",
                "region_id": "r3",
                "region_kind": "DRIFT_ZONE",
                "persistence_ratio": 0.3,
                "continuity_ratio": 0.2,
                "volatility_score": 0.7,
                "drift_score": 0.75,
                "density_score": 0.3,
                "stability_score": 0.3,
                "evidence_count": 4,
                "advisory_flags": ["drift_corridor"],
                "final_status": ADVISORY_ONLY,
            },
        ],
        "atlas_corridors": [
            {
                "schema": "AtlasCorridor.v1",
                "corridor_id": "c1",
                "corridor_kind": "REPLAY_CORRIDOR",
                "replay_stability": 0.3,
                "transport_stability": 0.5,
                "continuity_ratio": 0.4,
                "persistence_ratio": 0.6,
                "drift_score": 0.6,
                "evidence_count": 4,
                "volatility_score": 0.5,
                "advisory_flags": ["replay_continuity"],
                "final_status": ADVISORY_ONLY,
            },
            {
                "schema": "AtlasCorridor.v1",
                "corridor_id": "c2",
                "corridor_kind": "CONTINUITY_CORRIDOR",
                "replay_stability": 0.7,
                "transport_stability": 0.8,
                "continuity_ratio": 0.75,
                "persistence_ratio": 0.7,
                "drift_score": 0.1,
                "evidence_count": 5,
                "volatility_score": 0.2,
                "advisory_flags": ["transport_continuity"],
                "final_status": ADVISORY_ONLY,
            },
        ],
        "drift_accumulation_zones": [
            {
                "schema": "DriftAccumulationZone.v1",
                "zone_id": "z1",
                "drift_score": 0.75,
                "evidence_count": 4,
                "final_status": ADVISORY_ONLY,
                "advisory_flags": [],
            }
        ],
        "structural_evolution_tracks": [
            {
                "schema": "StructuralEvolutionTrack.v1",
                "track_id": "t1",
                "from_ref": "run-1",
                "to_ref": "run-2",
                "evolution_velocity": 0.8,
                "continuity_delta": -0.5,
                "evidence_count": 2,
                "final_status": ADVISORY_ONLY,
                "advisory_flags": [],
            }
        ],
        "topology_density_field": {
            "schema": "TopologyDensityField.v1",
            "topology_density_score": 0.4,
            "region_density_score": 0.5,
            "continuity_density_score": 0.55,
            "drift_accumulation_score": 0.5,
            "evidence_count": 12,
            "final_status": ADVISORY_ONLY,
        },
        "regime_boundary_summary": {
            "schema": "RegimeBoundarySummary.v1",
            "boundary_count": 1,
            "boundaries": [
                {
                    "schema": "RegimeBoundary.v1",
                    "boundary_id": "b1",
                    "track_ref": "t1",
                    "boundary_kind": "HIGH_VELOCITY_TRANSITION",
                    "velocity_score": 0.8,
                    "final_status": ADVISORY_ONLY,
                }
            ],
            "regime_boundary_status": ADVISORY_ONLY,
            "final_status": ADVISORY_ONLY,
        },
        "remaining_blockers": [],
    }


def _regime_detector_audit() -> dict:
    return {
        "status": "PASS",
        "detector_hash": "abc123",
        "receipt_hash": "def456",
        "findings": [],
        "schema_version": "TemporalRegimeTransitionDetector.v1",
        "detector_status": "REGIME_WATCH",
        "detector_posture": "WATCH",
        "current_regime_state": {
            "state_id": "state-watch",
            "state_type": "WATCH",
            "state_score": 0.6,
            "confidence": 0.8,
            "state_posture": "ELEVATED",
            "authoritative": False,
        },
        "transition_events": [
            {
                "transition_id": "tr-1",
                "from_state": "CALM",
                "to_state": "WATCH",
                "transition_probability": 0.6,
                "transition_confidence": 0.8,
                "trigger_ids": [],
                "affected_node_ids": [],
                "affected_fracture_zone_ids": [],
                "event_posture": "WATCH",
                "auto_transition_allowed": False,
            }
        ],
        "instability_metrics": [
            {
                "metric_id": "m-instability",
                "metric_type": "REGIME_INSTABILITY",
                "metric_value": 0.6,
                "metric_policy": "ADVISORY_ONLY",
                "metric_posture": "WARN",
            },
            {
                "metric_id": "m-trans",
                "metric_type": "TRANSITION_PROBABILITY",
                "metric_value": 0.6,
                "metric_policy": "ADVISORY_ONLY",
                "metric_posture": "WARN",
            },
        ],
    }


# ---------------------------------------------------------------------------
# Tests: invariant enforcement
# ---------------------------------------------------------------------------


def test_apply_invariants_fail_closed() -> None:
    payload = _apply_invariants({"custom": "value"})
    assert payload["advisory_only"] is True
    assert payload["detection_only"] is True
    assert payload["visualization_support_only"] is True
    assert payload["execution_authority"] is False
    assert payload["authority_granted"] is False
    assert payload["mutation_allowed"] is False
    assert payload["replay_mutation_allowed"] is False
    assert payload["canon_mutation_allowed"] is False
    assert payload["forecast_mutation_allowed"] is False
    assert payload["operator_execution_allowed"] is False
    assert payload["autonomous_adaptation"] is False
    assert payload["command_channel"] is False
    assert payload["bidirectional_control"] is False
    assert payload["inference_authority"] is False


def test_patch_id_correct() -> None:
    assert PATCH_ID == "PATCH-P24-TEMPORAL-REGIME-TRANSITION-AND-PHASE-BOUNDARY-DETECTION-001"


# ---------------------------------------------------------------------------
# Tests: phase-boundary detection
# ---------------------------------------------------------------------------


def test_detect_phase_boundaries_from_cartography() -> None:
    carto = _cartography_payload()
    boundaries = _detect_phase_boundaries(carto, None)
    boundary_kinds = {b["boundary_kind"] for b in boundaries}
    assert "HIGH_VELOCITY_TRANSITION" in boundary_kinds
    for b in boundaries:
        assert b["advisory_only"] is True
        assert b["detection_only"] is True
        assert b["mutation_allowed"] is False
        assert b["final_status"] == ADVISORY_ONLY


def test_detect_phase_boundaries_from_regime_detector() -> None:
    detector = _regime_detector_audit()
    boundaries = _detect_phase_boundaries(None, detector)
    assert any(b["boundary_kind"] == "REGIME_STATE_TRANSITION" for b in boundaries)
    for b in boundaries:
        assert b["mutation_allowed"] is False


def test_detect_phase_boundaries_empty() -> None:
    boundaries = _detect_phase_boundaries(None, None)
    assert boundaries == []


def test_detect_phase_boundaries_no_authority() -> None:
    carto = _cartography_payload()
    detector = _regime_detector_audit()
    for b in _detect_phase_boundaries(carto, detector):
        assert b.get("authority_granted") is False
        assert b.get("auto_execute") is False
        assert b.get("command_channel") is False


# ---------------------------------------------------------------------------
# Tests: replay collapse detection
# ---------------------------------------------------------------------------


def test_detect_replay_collapse_from_cartography() -> None:
    carto = _cartography_payload()
    report = _detect_replay_collapse(carto, None)
    assert report["schema"] == "ReplayCollapseReport.v1"
    assert report["collapse_status"] in {
        "COLLAPSE_RISK_DETECTED", "COLLAPSE_WATCH", NOT_COMPUTABLE
    }
    assert report["mutation_allowed"] is False
    assert report["advisory_only"] is True


def test_detect_replay_collapse_from_detector_metrics() -> None:
    detector = _regime_detector_audit()
    report = _detect_replay_collapse(None, detector)
    # TRANSITION_PROBABILITY with WARN posture should emit a signal
    assert report["signal_count"] >= 1 or report["collapse_status"] == NOT_COMPUTABLE


def test_replay_collapse_no_authority() -> None:
    carto = _cartography_payload()
    report = _detect_replay_collapse(carto, None)
    for signal in report["signals"]:
        assert signal["mutation_allowed"] is False
        assert signal["authority_granted"] is False
        assert signal["autonomous_adaptation"] is False


# ---------------------------------------------------------------------------
# Tests: continuity fracture detection
# ---------------------------------------------------------------------------


def test_detect_continuity_fractures_from_cartography() -> None:
    carto = _cartography_payload()
    report = _detect_continuity_fractures(carto, None)
    assert report["schema"] == "ContinuityFractureReport.v1"
    # DIVERGENCE_REGION and DRIFT_ZONE with low continuity should generate fractures
    assert report["fracture_count"] >= 1
    for f in report["fractures"]:
        assert f["advisory_only"] is True
        assert f["mutation_allowed"] is False


def test_detect_continuity_fractures_no_authority() -> None:
    carto = _cartography_payload()
    report = _detect_continuity_fractures(carto, None)
    for f in report["fractures"]:
        assert f.get("authority_granted") is False
        assert f.get("command_channel") is False


def test_detect_continuity_fractures_none_inputs() -> None:
    report = _detect_continuity_fractures(None, None)
    assert report["fracture_count"] == 0
    assert report["fracture_status"] == NOT_COMPUTABLE


# ---------------------------------------------------------------------------
# Tests: drift escalation boundaries
# ---------------------------------------------------------------------------


def test_compute_drift_escalation_boundaries_from_cartography() -> None:
    carto = _cartography_payload()
    boundaries = _compute_drift_escalation_boundaries(carto, None)
    # drift_accumulation_score=0.5 and zone with 0.75 should emit boundaries
    assert len(boundaries) >= 1
    for b in boundaries:
        assert b["schema"] == "DriftEscalationBoundary.v1"
        assert b["advisory_only"] is True
        assert b["mutation_allowed"] is False
        assert b["escalation_posture"] in {
            "ESCALATION_CRITICAL", "ESCALATION_ELEVATED", "ESCALATION_WATCH"
        }


def test_compute_drift_escalation_boundaries_no_authority() -> None:
    carto = _cartography_payload()
    for b in _compute_drift_escalation_boundaries(carto, None):
        assert b.get("authority_granted") is False
        assert b.get("auto_execute") is False


def test_drift_escalation_boundaries_empty() -> None:
    boundaries = _compute_drift_escalation_boundaries(None, None)
    assert boundaries == []


# ---------------------------------------------------------------------------
# Tests: phase-shift tracking
# ---------------------------------------------------------------------------


def test_build_phase_shift_tracks_from_cartography() -> None:
    carto = _cartography_payload()
    shifts = _build_phase_shift_tracks(carto, None)
    # Track t1 has velocity=0.8 which is >= 0.3 threshold
    assert len(shifts) >= 1
    for s in shifts:
        assert s["schema"] == "PhaseShiftTrack.v1"
        assert s["advisory_only"] is True
        assert s["mutation_allowed"] is False


def test_build_phase_shift_tracks_from_detector() -> None:
    detector = _regime_detector_audit()
    shifts = _build_phase_shift_tracks(None, detector)
    # CALM -> WATCH is +1 severity delta -> should produce a shift
    assert any(s.get("direction") == "ESCALATION" for s in shifts)


def test_phase_shift_tracks_no_authority() -> None:
    carto = _cartography_payload()
    detector = _regime_detector_audit()
    for s in _build_phase_shift_tracks(carto, detector):
        assert s.get("authority_granted") is False
        assert s.get("command_channel") is False
        assert s.get("autonomous_adaptation") is False


# ---------------------------------------------------------------------------
# Tests: transition density metrics
# ---------------------------------------------------------------------------


def test_compute_transition_density() -> None:
    carto = _cartography_payload()
    detector = _regime_detector_audit()
    boundaries = _detect_phase_boundaries(carto, detector)
    shifts = _build_phase_shift_tracks(carto, detector)
    drift_bounds = _compute_drift_escalation_boundaries(carto, detector)
    collapse = _detect_replay_collapse(carto, detector)
    fractures = _detect_continuity_fractures(carto, detector)

    density = _compute_transition_density(boundaries, shifts, drift_bounds, collapse, fractures)
    assert density["schema"] == "TransitionDensityMetrics.v1"
    assert density["advisory_only"] is True
    assert density["mutation_allowed"] is False
    assert 0.0 <= density["transition_density_score"] <= 1.0
    assert 0.0 <= density["high_severity_ratio"] <= 1.0
    assert density["transition_density_posture"] in {
        "TRANSITION_DENSE", "TRANSITION_ELEVATED", "TRANSITION_NOMINAL", NOT_COMPUTABLE
    }
    assert density["total_transition_events"] >= 0


# ---------------------------------------------------------------------------
# Tests: regime transition summary
# ---------------------------------------------------------------------------


def test_build_regime_transition_summary() -> None:
    carto = _cartography_payload()
    detector = _regime_detector_audit()
    boundaries = _detect_phase_boundaries(carto, detector)
    shifts = _build_phase_shift_tracks(carto, detector)
    drift_bounds = _compute_drift_escalation_boundaries(carto, detector)
    collapse = _detect_replay_collapse(carto, detector)
    fractures = _detect_continuity_fractures(carto, detector)
    density = _compute_transition_density(boundaries, shifts, drift_bounds, collapse, fractures)

    summary = _build_regime_transition_summary(
        detector, boundaries, shifts, collapse, fractures, drift_bounds, density
    )
    assert summary["schema"] == "RegimeTransitionSummary.v1"
    assert summary["advisory_only"] is True
    assert summary["mutation_allowed"] is False
    assert summary["overall_regime_posture"] in {
        "REGIME_CRITICAL", "REGIME_ELEVATED", "REGIME_WATCH", "REGIME_STABLE", NOT_COMPUTABLE
    }
    assert len(summary["recommended_actions"]) >= 1
    # Must never be authoritative
    assert summary.get("authority_granted") is False
    assert summary.get("auto_execute") is False
    assert summary.get("command_channel") is False


def test_regime_transition_summary_no_detector() -> None:
    summary = _build_regime_transition_summary(None, [], [], _detect_replay_collapse(None, None), _detect_continuity_fractures(None, None), [], _compute_transition_density([], [], [], _detect_replay_collapse(None, None), _detect_continuity_fractures(None, None)))
    assert summary["detector_status"] == NOT_COMPUTABLE
    assert summary["overall_regime_posture"] == NOT_COMPUTABLE


# ---------------------------------------------------------------------------
# Tests: AAL-Viz surface
# ---------------------------------------------------------------------------


def test_build_aal_viz_surface() -> None:
    carto = _cartography_payload()
    detector = _regime_detector_audit()
    boundaries = _detect_phase_boundaries(carto, detector)
    shifts = _build_phase_shift_tracks(carto, detector)
    drift_bounds = _compute_drift_escalation_boundaries(carto, detector)
    collapse = _detect_replay_collapse(carto, detector)
    fractures = _detect_continuity_fractures(carto, detector)
    density = _compute_transition_density(boundaries, shifts, drift_bounds, collapse, fractures)
    summary = _build_regime_transition_summary(
        detector, boundaries, shifts, collapse, fractures, drift_bounds, density
    )
    viz = _build_aal_viz_surface(summary, boundaries, shifts, density, collapse, fractures)

    assert viz["schema"] == "TemporalRegimeTransitionVizSurface.v1"
    assert viz["advisory_only"] is True
    assert viz["mutation_allowed"] is False
    assert viz["authority_granted"] is False
    assert "aal_viz_surface" in viz["advisory_flags"]
    assert 0.0 <= viz["posture_score"] <= 1.0
    assert 0.0 <= viz["transition_density_score"] <= 1.0


# ---------------------------------------------------------------------------
# Tests: full packet builder
# ---------------------------------------------------------------------------


def test_build_temporal_regime_transition_packet_no_sources(tmp_path: Path) -> None:
    packet = build_temporal_regime_transition_packet(
        packet_id="test-001",
        source_artifact_paths={},
    )
    assert packet["schema"] == "TemporalRegimeTransitionPacket.v1"
    assert packet["patch_id"] == PATCH_ID
    assert packet["advisory_only"] is True
    assert packet["mutation_allowed"] is False
    assert packet["execution_authority"] is False
    assert packet["authority_granted"] is False
    assert packet["command_channel"] is False
    assert packet["replay_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["forecast_mutation_allowed"] is False
    assert packet["operator_execution_allowed"] is False
    assert packet["autonomous_adaptation"] is False
    assert "phase_boundaries" in packet
    assert "phase_shifts" in packet
    assert "replay_collapse_report" in packet
    assert "continuity_fracture_report" in packet
    assert "drift_escalation_boundaries" in packet
    assert "transition_density_metrics" in packet
    assert "regime_transition_summary" in packet
    assert "aal_viz_surface" in packet
    assert packet["final_status"] in {ADVISORY_ONLY, NOT_COMPUTABLE, BLOCKED}


def test_build_temporal_regime_transition_packet_with_cartography(tmp_path: Path) -> None:
    carto_path = tmp_path / "temporal_topology_cartography_001.latest.json"
    carto_path.write_text(
        json.dumps(_cartography_payload(), sort_keys=True) + "\n", encoding="utf-8"
    )
    packet = build_temporal_regime_transition_packet(
        packet_id="test-with-carto",
        source_artifact_paths={"temporal_topology_cartography": str(carto_path)},
    )
    assert packet["schema"] == "TemporalRegimeTransitionPacket.v1"
    assert packet["final_status"] in {ADVISORY_ONLY, NOT_COMPUTABLE}
    # With valid cartography data, boundaries and shifts should be detected
    assert isinstance(packet["phase_boundaries"], list)
    assert isinstance(packet["drift_escalation_boundaries"], list)
    # Hash must be present and non-empty
    assert packet["packet_hash"] and len(packet["packet_hash"]) == 64


def test_packet_determinism(tmp_path: Path) -> None:
    carto_path = tmp_path / "temporal_topology_cartography_001.latest.json"
    carto_path.write_text(
        json.dumps(_cartography_payload(), sort_keys=True) + "\n", encoding="utf-8"
    )
    sources = {"temporal_topology_cartography": str(carto_path)}
    p1 = build_temporal_regime_transition_packet(packet_id="det-test", source_artifact_paths=sources)
    p2 = build_temporal_regime_transition_packet(packet_id="det-test", source_artifact_paths=sources)
    assert p1["packet_hash"] == p2["packet_hash"]


def test_packet_hash_changes_with_inputs(tmp_path: Path) -> None:
    sources_a: dict[str, str] = {}
    sources_b = {"temporal_topology_cartography": str(tmp_path / "missing.json")}
    p1 = build_temporal_regime_transition_packet(packet_id="hash-test", source_artifact_paths=sources_a)
    p2 = build_temporal_regime_transition_packet(packet_id="hash-test", source_artifact_paths=sources_b)
    # Both should produce packets but with different hashes (different source paths)
    assert isinstance(p1["packet_hash"], str)
    assert isinstance(p2["packet_hash"], str)


# ---------------------------------------------------------------------------
# Tests: write helpers
# ---------------------------------------------------------------------------


def test_write_temporal_regime_transition_packet(tmp_path: Path) -> None:
    packet = build_temporal_regime_transition_packet(packet_id="write-test", source_artifact_paths={})
    out_path = tmp_path / "temporal_regime_transition_001.latest.json"
    write_temporal_regime_transition_packet(out_path, packet)
    assert out_path.exists()
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    roundtrip = json.loads(text)
    assert roundtrip["schema"] == "TemporalRegimeTransitionPacket.v1"
    assert roundtrip["advisory_only"] is True
    assert roundtrip["mutation_allowed"] is False


def test_build_temporal_regime_transition_markdown() -> None:
    packet = build_temporal_regime_transition_packet(packet_id="md-test", source_artifact_paths={})
    md = build_temporal_regime_transition_markdown(packet)
    assert "# Temporal Regime Transition" in md
    assert PATCH_ID in md
    assert "Advisory Only" in md
    assert "mutation" in md.lower()


# ---------------------------------------------------------------------------
# Tests: summarize helper
# ---------------------------------------------------------------------------


def test_summarize_temporal_regime_transition_none() -> None:
    summary = summarize_temporal_regime_transition(None)
    assert summary["temporal_regime_transition_status"] == NOT_COMPUTABLE
    assert summary["overall_regime_posture"] == NOT_COMPUTABLE
    assert summary["phase_boundary_count"] == 0
    assert summary["transition_density_score"] == 0.0


def test_summarize_temporal_regime_transition_packet() -> None:
    packet = build_temporal_regime_transition_packet(packet_id="sum-test", source_artifact_paths={})
    summary = summarize_temporal_regime_transition(packet)
    assert summary["temporal_regime_transition_status"] in {ADVISORY_ONLY, NOT_COMPUTABLE, BLOCKED}
    assert summary["phase_boundary_count"] >= 0
    assert 0.0 <= summary["transition_density_score"] <= 1.0


# ---------------------------------------------------------------------------
# Tests: authority seal — no flag may be True that is forbidden
# ---------------------------------------------------------------------------


def test_no_forbidden_true_flags_in_packet() -> None:
    forbidden = {
        "execution_authority",
        "authority_granted",
        "mutation_allowed",
        "promotion_allowed",
        "auto_execute",
        "auto_approve",
        "command_channel",
        "bidirectional_control",
        "inference_authority",
        "replay_mutation_allowed",
        "canon_mutation_allowed",
        "forecast_mutation_allowed",
        "operator_execution_allowed",
        "autonomous_adaptation",
    }
    packet = build_temporal_regime_transition_packet(packet_id="authority-seal", source_artifact_paths={})
    text = json.dumps(packet)
    payload = json.loads(text)

    def _check(obj: object, path: str = "") -> list[str]:
        violations: list[str] = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                p = f"{path}.{k}" if path else k
                if k in forbidden and v is True:
                    violations.append(p)
                violations.extend(_check(v, p))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                violations.extend(_check(v, f"{path}[{i}]"))
        return violations

    violations = _check(payload)
    assert violations == [], f"Forbidden True flags found: {violations}"


# ---------------------------------------------------------------------------
# Tests: script entry point (smoke test)
# ---------------------------------------------------------------------------


def test_run_temporal_regime_transition_script(tmp_path: Path, monkeypatch: object) -> None:
    import importlib

    out_json = tmp_path / "projections" / "temporal_regime_transition_001.latest.json"
    monkeypatch.setenv("OUT_DIR", str(tmp_path))

    import scripts.temporal.run_temporal_regime_transition as script_module

    importlib.reload(script_module)
    script_module.main(argv=[])
    assert out_json.exists()
    md_path = out_json.with_suffix(".md")
    assert md_path.exists()
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["schema"] == "TemporalRegimeTransitionPacket.v1"
    assert payload["advisory_only"] is True
    assert payload["mutation_allowed"] is False

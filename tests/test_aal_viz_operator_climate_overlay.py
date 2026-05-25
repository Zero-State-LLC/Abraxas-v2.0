from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.aal_viz_operator_climate_overlay import NOT_COMPUTABLE, build_aal_viz_operator_climate_overlay_packet, write_aal_viz_operator_climate_overlay_packet
from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _sources(tmp_path: Path, *, missing: str | None = None, corrupt: str | None = None) -> dict[str, str]:
    src = {
        "operator_attention_weather": tmp_path / "weather.json",
        "operator_review_routing_enhancer": tmp_path / "routing.json",
        "operator_attention_ledger": tmp_path / "ledger.json",
        "operator_fatigue_corridor": tmp_path / "corridor.json",
        "continuity_degradation_explainer": tmp_path / "explainer.json",
        "operator_climatology_summary": tmp_path / "climatology.json",
    }
    payloads = {
        "operator_attention_weather": {"weather_posture": "CLEAR", "attention_urgency": "LOW", "blocker_summary": [], "weather_hash": "wh", "final_status": "ADVISORY_ONLY"},
        "operator_review_routing_enhancer": {"routing_posture": "NORMAL", "review_priority_posture": "LOW", "blocker_summary": [], "enhancer_hash": "rh", "final_status": "ADVISORY_ONLY"},
        "operator_attention_ledger": {"ledger_posture": "STABLE", "final_status": "ADVISORY_ONLY", "blocker_summary": [], "ledger_hash": "lh", "entries": []},
        "operator_fatigue_corridor": {"corridor_status": "CLEAR", "final_status": "ADVISORY_ONLY", "pressure_persistence_detected": False, "blocker_summary": [], "corridor_hash": "ch"},
        "continuity_degradation_explainer": {"final_status": "ADVISORY_ONLY", "explanation_posture": "CLEAR", "dominant_degradation_vectors": ["UPSTREAM_BLOCKER_RECURRENCE"], "blocker_summary": [], "explainer_hash": "eh"},
        "operator_climatology_summary": {"final_status": "ADVISORY_ONLY", "climatology_posture": "CLEAR", "weather_posture_counts": {"CLEAR": 1}, "attention_urgency_counts": {"LOW": 1}, "routing_posture_counts": {"NORMAL": 1}, "review_priority_posture_counts": {"LOW": 1}, "ledger_posture_counts": {"STABLE": 1}, "corridor_status_counts": {"CLEAR": 1}, "degradation_vector_counts": {"UPSTREAM_BLOCKER_RECURRENCE": 1}, "blocker_class_counts": {}, "source_hash_lineage": {"weather_hash": "wh"}, "blocker_summary": []},
    }
    for key, path in src.items():
        if key == missing:
            continue
        if key == corrupt:
            path.write_text("{bad", encoding="utf-8")
            continue
        _write(path, payloads[key])
    return {k: v.as_posix() for k, v in src.items()}


def test_healthy_overlay(tmp_path: Path) -> None:
    p = build_aal_viz_operator_climate_overlay_packet(source_artifact_paths=_sources(tmp_path))
    assert p["final_status"] == "PROJECTION_ONLY"
    assert p["overlay_posture"] in {"CLEAR", "WATCH"}


def test_pressure_persistence_degraded(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["operator_fatigue_corridor"]), {"corridor_status": "PRESSURE_PERSISTENCE", "final_status": "ADVISORY_DEGRADED", "pressure_persistence_detected": True, "blocker_summary": ["x"], "corridor_hash": "ch"})
    p = build_aal_viz_operator_climate_overlay_packet(source_artifact_paths=src)
    assert p["final_status"] == "PROJECTION_DEGRADED"
    assert p["overlay_posture"] in {"PRESSURE_PERSISTENCE", "DEGRADED"}


def test_blocked_state(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["operator_climatology_summary"]), {"final_status": "BLOCKED", "climatology_posture": "BLOCKED", "blocker_summary": ["x"]})
    p = build_aal_viz_operator_climate_overlay_packet(source_artifact_paths=src)
    assert p["final_status"] == "BLOCKED"
    assert p["overlay_posture"] == "BLOCKED"


def test_missing_fails_closed(tmp_path: Path) -> None:
    p = build_aal_viz_operator_climate_overlay_packet(source_artifact_paths=_sources(tmp_path, missing="operator_attention_weather"))
    assert p["final_status"] == NOT_COMPUTABLE


def test_corrupt_fails_closed(tmp_path: Path) -> None:
    p = build_aal_viz_operator_climate_overlay_packet(source_artifact_paths=_sources(tmp_path, corrupt="operator_attention_ledger"))
    assert p["final_status"] == NOT_COMPUTABLE


def test_sorted_and_stable_ids(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    a = build_aal_viz_operator_climate_overlay_packet(source_artifact_paths=src)
    b = build_aal_viz_operator_climate_overlay_packet(source_artifact_paths=src)
    assert [x["layer_id"] for x in a["render_layers"]] == sorted(x["layer_id"] for x in a["render_layers"])
    assert [x["node_id"] for x in a["overlay_nodes"]] == sorted(x["node_id"] for x in a["overlay_nodes"])
    assert [x["card_id"] for x in a["overlay_cards"]] == sorted(x["card_id"] for x in a["overlay_cards"])
    assert [x["badge_id"] for x in a["overlay_badges"]] == sorted(x["badge_id"] for x in a["overlay_badges"])
    assert [x["edge_id"] for x in a["overlay_edges"]] == sorted(x["edge_id"] for x in a["overlay_edges"])
    assert a["overlay_hash"] == b["overlay_hash"]


def test_input_not_mutated() -> None:
    packets = {
        "operator_attention_weather": {"weather_posture": "WATCH", "attention_urgency": "MEDIUM", "blocker_summary": []},
        "operator_review_routing_enhancer": {"routing_posture": "WATCH", "review_priority_posture": "MEDIUM", "blocker_summary": []},
        "operator_attention_ledger": {"ledger_posture": "WATCH", "blocker_summary": []},
        "operator_fatigue_corridor": {"corridor_status": "WATCH", "final_status": "ADVISORY_ONLY", "pressure_persistence_detected": False, "blocker_summary": []},
        "continuity_degradation_explainer": {"final_status": "ADVISORY_ONLY", "explanation_posture": "WATCH", "dominant_degradation_vectors": [], "blocker_summary": []},
        "operator_climatology_summary": {"final_status": "ADVISORY_ONLY", "climatology_posture": "WATCH", "blocker_summary": []},
    }
    before = deepcopy(packets)
    build_aal_viz_operator_climate_overlay_packet(source_packets=packets, source_artifact_paths={})
    assert packets == before


def test_writer_schema_governance_registry(tmp_path: Path) -> None:
    packet = build_aal_viz_operator_climate_overlay_packet(source_artifact_paths=_sources(tmp_path))
    out = tmp_path / "p35.json"
    write_aal_viz_operator_climate_overlay_packet(out, packet)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    schema = json.loads(Path("contracts/operator_attention/aal_viz_operator_climate_overlay.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "AALVizOperatorClimateOverlay.v1"
    g = packet["governance_flags"]
    assert g["advisory_only"] is True and g["projection_only"] is True and g["render_consumer_only"] is True
    assert all(g[k] is False for k in ["inference_authority", "mutation_allowed", "authority_granted", "execution_authority", "forecast_authority", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed", "runtime_mutation_allowed", "ui_command_authority", "adaptive_behavior_allowed", "psychological_claims_allowed", "speculative_causation_allowed", "trend_prediction_allowed", "readiness_claims_allowed", "auto_execute", "auto_approve", "command_channel", "bidirectional_control"])

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    j = next(e for e in registry.entries if e.artifact_path == "out/projections/aal_viz_operator_climate_overlay_001.latest.json")
    m = next(e for e in registry.entries if e.artifact_path == "out/projections/aal_viz_operator_climate_overlay_001.latest.md")
    assert j.determinism_class == "DERIVED_OPTIONAL"
    assert m.determinism_class == "DERIVED_OPTIONAL"
    assert j.artifact_path not in list_ci_drift_artifact_paths(registry)

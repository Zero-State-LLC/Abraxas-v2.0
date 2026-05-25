from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths
from core.operator_climatology_summary import NOT_COMPUTABLE, build_operator_climatology_summary_packet, write_operator_climatology_summary_packet


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
    }
    payloads = {
        "operator_attention_weather": {"weather_posture": "CLEAR", "attention_urgency": "LOW", "blocker_summary": [], "weather_hash": "wh", "final_status": "ADVISORY_ONLY"},
        "operator_review_routing_enhancer": {"routing_posture": "NORMAL", "review_priority_posture": "LOW", "blocker_summary": [], "enhancer_hash": "rh", "final_status": "ADVISORY_ONLY"},
        "operator_attention_ledger": {"ledger_posture": "STABLE", "final_status": "ADVISORY_ONLY", "blocker_summary": [], "ledger_hash": "lh", "entries": [{"entry_hash": "e1"}]},
        "operator_fatigue_corridor": {"corridor_status": "CLEAR", "final_status": "ADVISORY_ONLY", "pressure_persistence_detected": False, "blocker_summary": [], "recurring_blocker_classes": [], "corridor_hash": "ch", "evidence_refs": []},
        "continuity_degradation_explainer": {"final_status": "ADVISORY_ONLY", "explanation_posture": "CLEAR", "dominant_degradation_vectors": ["UPSTREAM_BLOCKER_RECURRENCE"], "blocker_summary": [], "explainer_hash": "eh"},
    }
    for key, path in src.items():
        if key == missing:
            continue
        if key == corrupt:
            path.write_text("{bad", encoding="utf-8")
            continue
        _write(path, payloads[key])
    return {k: v.as_posix() for k, v in src.items()}


def test_healthy_summary(tmp_path: Path) -> None:
    p = build_operator_climatology_summary_packet(source_artifact_paths=_sources(tmp_path))
    assert p["final_status"] == "ADVISORY_ONLY"
    assert p["climatology_posture"] in {"CLEAR", "WATCH"}


def test_pressure_persistence_degraded(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["operator_fatigue_corridor"]), {"corridor_status": "PRESSURE_PERSISTENCE", "final_status": "ADVISORY_DEGRADED", "pressure_persistence_detected": True, "blocker_summary": ["X"], "recurring_blocker_classes": ["X"], "corridor_hash": "ch", "evidence_refs": []})
    p = build_operator_climatology_summary_packet(source_artifact_paths=src)
    assert p["final_status"] == "ADVISORY_DEGRADED"
    assert p["climatology_posture"] in {"PRESSURE_PERSISTENCE", "DEGRADED"}


def test_blocked_propagates(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["continuity_degradation_explainer"]), {"final_status": "BLOCKED", "explanation_posture": "BLOCKED", "dominant_degradation_vectors": ["SOURCE_NOT_COMPUTABLE_PROPAGATION"], "blocker_summary": ["x"], "explainer_hash": "eh"})
    p = build_operator_climatology_summary_packet(source_artifact_paths=src)
    assert p["final_status"] == "BLOCKED"
    assert p["climatology_posture"] == "BLOCKED"


def test_missing_fails_closed(tmp_path: Path) -> None:
    p = build_operator_climatology_summary_packet(source_artifact_paths=_sources(tmp_path, missing="operator_attention_weather"))
    assert p["final_status"] == NOT_COMPUTABLE


def test_corrupt_fails_closed(tmp_path: Path) -> None:
    p = build_operator_climatology_summary_packet(source_artifact_paths=_sources(tmp_path, corrupt="operator_attention_ledger"))
    assert p["final_status"] == NOT_COMPUTABLE


def test_sorted_and_deterministic_counts(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["continuity_degradation_explainer"]), {"final_status": "ADVISORY_ONLY", "explanation_posture": "CLEAR", "dominant_degradation_vectors": ["B", "A", "B"], "blocker_summary": ["z"], "explainer_hash": "eh"})
    a = build_operator_climatology_summary_packet(source_artifact_paths=src)
    b = build_operator_climatology_summary_packet(source_artifact_paths=src)
    assert list(a["degradation_vector_counts"].keys()) == sorted(a["degradation_vector_counts"].keys())
    assert a["summary_hash"] == b["summary_hash"]


def test_blocker_count_normalization(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["operator_attention_weather"]), {"weather_posture": "CLEAR", "attention_urgency": "LOW", "blocker_summary": [" A ", "a", "B"], "weather_hash": "wh", "final_status": "ADVISORY_ONLY"})
    p = build_operator_climatology_summary_packet(source_artifact_paths=src)
    assert p["blocker_class_counts"]["a"] >= 1
    assert "b" in p["blocker_class_counts"]


def test_input_not_mutated() -> None:
    packets = {
        "operator_attention_weather": {"weather_posture": "WATCH", "attention_urgency": "MEDIUM", "weather_hash": "wh", "blocker_summary": []},
        "operator_review_routing_enhancer": {"routing_posture": "WATCH", "review_priority_posture": "MEDIUM", "enhancer_hash": "rh", "blocker_summary": []},
        "operator_attention_ledger": {"ledger_posture": "WATCH", "ledger_hash": "lh", "blocker_summary": [], "entries": [{"entry_hash": "e1"}]},
        "operator_fatigue_corridor": {"corridor_status": "WATCH", "pressure_persistence_detected": False, "corridor_hash": "ch", "blocker_summary": [], "recurring_blocker_classes": []},
        "continuity_degradation_explainer": {"final_status": "ADVISORY_ONLY", "explanation_posture": "WATCH", "dominant_degradation_vectors": [], "blocker_summary": [], "explainer_hash": "eh"},
    }
    before = deepcopy(packets)
    build_operator_climatology_summary_packet(source_packets=packets, source_artifact_paths={})
    assert packets == before


def test_writer_schema_governance_registry(tmp_path: Path) -> None:
    packet = build_operator_climatology_summary_packet(source_artifact_paths=_sources(tmp_path))
    out = tmp_path / "p34.json"
    write_operator_climatology_summary_packet(out, packet)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    schema = json.loads(Path("contracts/operator_attention/operator_climatology_summary.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "OperatorClimatologySummary.v1"
    g = packet["governance_flags"]
    assert g["advisory_only"] is True and g["projection_only"] is True and g["climatology_only"] is True and g["observation_only"] is True
    assert all(g[k] is False for k in ["mutation_allowed", "authority_granted", "execution_authority", "forecast_authority", "trend_prediction_allowed", "readiness_claims_allowed", "adaptive_behavior_allowed", "psychological_claims_allowed", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed", "runtime_mutation_allowed", "auto_execute", "auto_approve", "command_channel", "bidirectional_control"])

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    j = next(e for e in registry.entries if e.artifact_path == "out/projections/operator_climatology_summary_001.latest.json")
    m = next(e for e in registry.entries if e.artifact_path == "out/projections/operator_climatology_summary_001.latest.md")
    assert j.determinism_class == "DERIVED_OPTIONAL"
    assert m.determinism_class == "DERIVED_OPTIONAL"
    assert j.artifact_path not in list_ci_drift_artifact_paths(registry)

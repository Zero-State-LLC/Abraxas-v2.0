from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.continuity_degradation_explainer import (
    NOT_COMPUTABLE,
    build_continuity_degradation_explainer_packet,
    write_continuity_degradation_explainer_packet,
)
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
    }
    payloads = {
        "operator_attention_weather": {"weather_posture": "CLEAR", "attention_urgency": "LOW", "blocker_summary": [], "weather_hash": "wh", "final_status": "ADVISORY_ONLY"},
        "operator_review_routing_enhancer": {"routing_posture": "NORMAL", "review_priority_posture": "LOW", "blocker_summary": [], "enhancer_hash": "rh", "final_status": "ADVISORY_ONLY"},
        "operator_attention_ledger": {"ledger_posture": "STABLE", "final_status": "ADVISORY_ONLY", "blocker_summary": [], "ledger_hash": "lh", "entries": [{"entry_hash": "e1"}]},
        "operator_fatigue_corridor": {"corridor_status": "CLEAR", "final_status": "ADVISORY_ONLY", "pressure_persistence_detected": False, "blocker_summary": [], "recurring_blocker_classes": [], "corridor_hash": "ch", "evidence_refs": []},
    }
    for key, path in src.items():
        if key == missing:
            continue
        if key == corrupt:
            path.write_text("{bad", encoding="utf-8")
            continue
        _write(path, payloads[key])
    return {k: v.as_posix() for k, v in src.items()}


def test_healthy_clear_or_watch(tmp_path: Path) -> None:
    p = build_continuity_degradation_explainer_packet(source_artifact_paths=_sources(tmp_path))
    assert p["final_status"] == "ADVISORY_ONLY"
    assert p["explanation_posture"] in {"CLEAR", "WATCH"}


def test_pressure_persistence_degraded(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["operator_fatigue_corridor"]), {"corridor_status": "PRESSURE_PERSISTENCE", "final_status": "ADVISORY_DEGRADED", "pressure_persistence_detected": True, "blocker_summary": ["x"], "recurring_blocker_classes": ["x"], "corridor_hash": "ch", "evidence_refs": []})
    p = build_continuity_degradation_explainer_packet(source_artifact_paths=src)
    assert p["final_status"] == "ADVISORY_DEGRADED"
    assert p["explanation_posture"] == "PRESSURE_PERSISTENCE"


def test_corridor_blocked_propagates(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["operator_fatigue_corridor"]), {"corridor_status": "BLOCKED_PERSISTENCE", "final_status": "BLOCKED", "pressure_persistence_detected": True, "blocker_summary": ["x"], "recurring_blocker_classes": ["x"], "corridor_hash": "ch", "evidence_refs": []})
    p = build_continuity_degradation_explainer_packet(source_artifact_paths=src)
    assert p["final_status"] == "BLOCKED"
    assert p["explanation_posture"] == "BLOCKED"


def test_missing_fails_closed(tmp_path: Path) -> None:
    p = build_continuity_degradation_explainer_packet(source_artifact_paths=_sources(tmp_path, missing="operator_attention_weather"))
    assert p["final_status"] == NOT_COMPUTABLE


def test_corrupt_fails_closed(tmp_path: Path) -> None:
    p = build_continuity_degradation_explainer_packet(source_artifact_paths=_sources(tmp_path, corrupt="operator_attention_ledger"))
    assert p["final_status"] == NOT_COMPUTABLE


def test_recurring_blockers_sorted(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["operator_attention_ledger"]), {"ledger_posture": "DEGRADED", "final_status": "ADVISORY_DEGRADED", "blocker_summary": ["z", "a"], "ledger_hash": "lh", "entries": [{"entry_hash": "e1"}]})
    _write(Path(src["operator_fatigue_corridor"]), {"corridor_status": "PRESSURE_PERSISTENCE", "final_status": "ADVISORY_DEGRADED", "pressure_persistence_detected": True, "blocker_summary": [], "recurring_blocker_classes": ["b", "a"], "corridor_hash": "ch", "evidence_refs": []})
    p = build_continuity_degradation_explainer_packet(source_artifact_paths=src)
    assert p["recurring_blocker_classes"] == ["a", "b", "z"]


def test_deterministic_vectors_and_reason_chain(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    a = build_continuity_degradation_explainer_packet(source_artifact_paths=src)
    b = build_continuity_degradation_explainer_packet(source_artifact_paths=src)
    assert a["dominant_degradation_vectors"] == b["dominant_degradation_vectors"]
    assert a["reason_chain"] == b["reason_chain"]
    assert a["explainer_hash"] == b["explainer_hash"]


def test_input_not_mutated() -> None:
    source_packets = {
        "operator_attention_weather": {"weather_posture": "WATCH", "attention_urgency": "MEDIUM", "weather_hash": "wh", "blocker_summary": []},
        "operator_review_routing_enhancer": {"routing_posture": "WATCH", "review_priority_posture": "MEDIUM", "enhancer_hash": "rh", "blocker_summary": []},
        "operator_attention_ledger": {"ledger_posture": "WATCH", "ledger_hash": "lh", "blocker_summary": [], "entries": [{"entry_hash": "e1"}]},
        "operator_fatigue_corridor": {"corridor_status": "WATCH", "pressure_persistence_detected": False, "corridor_hash": "ch", "blocker_summary": [], "recurring_blocker_classes": []},
    }
    before = deepcopy(source_packets)
    build_continuity_degradation_explainer_packet(source_packets=source_packets, source_artifact_paths={})
    assert source_packets == before


def test_writer_emits_final_newline(tmp_path: Path) -> None:
    packet = build_continuity_degradation_explainer_packet(source_artifact_paths=_sources(tmp_path))
    out = tmp_path / "p33.json"
    write_continuity_degradation_explainer_packet(out, packet)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")


def test_schema_and_governance_and_registry() -> None:
    schema = json.loads(Path("contracts/operator_attention/continuity_degradation_explainer.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "ContinuityDegradationExplainer.v1"
    p = build_continuity_degradation_explainer_packet(source_packets={
        "operator_attention_weather": {"weather_posture": "CLEAR", "attention_urgency": "LOW", "weather_hash": "wh", "blocker_summary": []},
        "operator_review_routing_enhancer": {"routing_posture": "NORMAL", "review_priority_posture": "LOW", "enhancer_hash": "rh", "blocker_summary": []},
        "operator_attention_ledger": {"ledger_posture": "STABLE", "ledger_hash": "lh", "blocker_summary": [], "entries": []},
        "operator_fatigue_corridor": {"corridor_status": "CLEAR", "pressure_persistence_detected": False, "corridor_hash": "ch", "blocker_summary": [], "recurring_blocker_classes": []},
    }, source_artifact_paths={})
    g = p["governance_flags"]
    assert g["advisory_only"] is True and g["projection_only"] is True and g["explainer_only"] is True and g["evidence_linked"] is True
    assert all(g[k] is False for k in ["mutation_allowed","authority_granted","execution_authority","forecast_authority","routing_change_allowed","queue_mutation_allowed","canon_mutation_allowed","runtime_mutation_allowed","adaptive_behavior_allowed","speculative_causation_allowed","psychological_claims_allowed","auto_execute","auto_approve","command_channel","bidirectional_control"])
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    j = next(e for e in registry.entries if e.artifact_path == "out/projections/continuity_degradation_explainer_001.latest.json")
    m = next(e for e in registry.entries if e.artifact_path == "out/projections/continuity_degradation_explainer_001.latest.md")
    assert j.determinism_class == "DERIVED_OPTIONAL"
    assert m.determinism_class == "DERIVED_OPTIONAL"
    assert j.artifact_path not in list_ci_drift_artifact_paths(registry)

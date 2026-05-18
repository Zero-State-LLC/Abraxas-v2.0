from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths
from core.operator_review_routing_enhancer import (
    NOT_COMPUTABLE,
    build_operator_review_routing_enhancer_packet,
    write_operator_review_routing_enhancer_packet,
)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _sources(tmp_path: Path, *, missing: str | None = None, corrupt: str | None = None) -> dict[str, str]:
    paths = {
        "operator_attention_weather": tmp_path / "weather.json",
        "coherence_field_operator_surface": tmp_path / "p28.json",
        "operator_review_queue": tmp_path / "queue.json",
    }
    payloads = {
        "operator_attention_weather": {"weather_posture": "WATCH", "attention_urgency": "MEDIUM"},
        "coherence_field_operator_surface": {"remaining_blockers": []},
        "operator_review_queue": {"items": [{"priority": "P2"}]},
    }
    for k, p in payloads.items():
        if missing == k:
            continue
        if corrupt == k:
            paths[k].write_text("{bad", encoding="utf-8")
        else:
            _write(paths[k], p)
    return {k: v.as_posix() for k, v in paths.items()}


def test_builds_advisory_packet_healthy(tmp_path: Path) -> None:
    p = build_operator_review_routing_enhancer_packet(source_artifact_paths=_sources(tmp_path))
    assert p["final_status"] == "ADVISORY_ONLY"
    assert p["routing_posture"] in {"NORMAL", "WATCH"}


def test_missing_weather_fails_closed(tmp_path: Path) -> None:
    p = build_operator_review_routing_enhancer_packet(source_artifact_paths=_sources(tmp_path, missing="operator_attention_weather"))
    assert p["final_status"] == NOT_COMPUTABLE
    assert p["routing_posture"] == "BLOCKED"


def test_corrupt_source_fails_closed(tmp_path: Path) -> None:
    p = build_operator_review_routing_enhancer_packet(source_artifact_paths=_sources(tmp_path, corrupt="operator_review_queue"))
    assert p["final_status"] == NOT_COMPUTABLE


def test_blocked_critical_propagates(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["operator_attention_weather"]), {"weather_posture": "BLOCKED", "attention_urgency": "CRITICAL"})
    p = build_operator_review_routing_enhancer_packet(source_artifact_paths=src)
    assert p["routing_posture"] == "BLOCKED"
    assert p["review_priority_posture"] == "CRITICAL"


def test_queue_pressure_in_suggestions(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["operator_review_queue"]), {"items": [{"priority": "P0"}, {"priority": "P1"}]})
    p = build_operator_review_routing_enhancer_packet(source_artifact_paths=src)
    assert any("P0/P1" in s for s in p["advisory_routing_suggestions"])


def test_governance_flags_locked(tmp_path: Path) -> None:
    g = build_operator_review_routing_enhancer_packet(source_artifact_paths=_sources(tmp_path))["governance_flags"]
    assert g["advisory_only"] is True and g["projection_only"] is True and g["non_authoritative"] is True
    assert all(g[k] is False for k in ["routing_change_allowed","mutation_allowed","authority_granted","execution_authority","forecast_authority","command_channel","bidirectional_control","auto_execute","auto_approve","allow_autonomous_approval","queue_mutation_allowed","canon_mutation_allowed","runtime_mutation_allowed"])


def test_inputs_not_mutated() -> None:
    src_packets = {"operator_attention_weather": {"weather_posture": "WATCH", "attention_urgency": "MEDIUM"}, "coherence_field_operator_surface": {"remaining_blockers": []}, "operator_review_queue": {"items": []}}
    before = deepcopy(src_packets)
    build_operator_review_routing_enhancer_packet(source_packets=src_packets, source_artifact_paths={})
    assert src_packets == before


def test_deterministic_hashes_and_repeat(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    a = build_operator_review_routing_enhancer_packet(source_artifact_paths=src)
    b = build_operator_review_routing_enhancer_packet(source_artifact_paths=src)
    assert a["enhancer_hash"] == b["enhancer_hash"]
    assert a["source_hashes"] == b["source_hashes"]


def test_writer_emits_final_newline(tmp_path: Path) -> None:
    p = build_operator_review_routing_enhancer_packet(source_artifact_paths=_sources(tmp_path))
    out = tmp_path / "p30.json"
    write_operator_review_routing_enhancer_packet(out, p)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")


def test_registry_classification_derived_optional() -> None:
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    j = next(e for e in registry.entries if e.artifact_path == "out/projections/operator_review_routing_enhancer_001.latest.json")
    m = next(e for e in registry.entries if e.artifact_path == "out/projections/operator_review_routing_enhancer_001.latest.md")
    assert j.determinism_class == "DERIVED_OPTIONAL"
    assert m.determinism_class == "DERIVED_OPTIONAL"
    assert j.artifact_path not in list_ci_drift_artifact_paths(registry)


def test_schema_shape_present() -> None:
    schema = json.loads(Path("contracts/operator_review/operator_review_routing_enhancer.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "OperatorReviewRoutingEnhancer.v1"

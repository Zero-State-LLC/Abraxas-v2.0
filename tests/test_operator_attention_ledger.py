from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths
from core.operator_attention_ledger import (
    NOT_COMPUTABLE,
    build_operator_attention_ledger_packet,
    write_operator_attention_ledger_packet,
)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _sources(tmp_path: Path, *, missing: str | None = None, corrupt: str | None = None) -> dict[str, str]:
    paths = {
        "operator_attention_weather": tmp_path / "weather.json",
        "operator_review_routing_enhancer": tmp_path / "routing.json",
    }
    payloads = {
        "operator_attention_weather": {
            "final_status": "ADVISORY_ONLY",
            "weather_posture": "WATCH",
            "attention_urgency": "MEDIUM",
            "blocker_summary": [],
            "weather_hash": "wh-1",
        },
        "operator_review_routing_enhancer": {
            "final_status": "ADVISORY_ONLY",
            "routing_posture": "WATCH",
            "review_priority_posture": "MEDIUM",
            "blocker_summary": [],
            "enhancer_hash": "rh-1",
        },
    }
    for key, payload in payloads.items():
        if key == missing:
            continue
        if key == corrupt:
            paths[key].write_text("{bad", encoding="utf-8")
        else:
            _write(paths[key], payload)
    return {k: v.as_posix() for k, v in paths.items()}


def test_healthy_builds_advisory_entry(tmp_path: Path) -> None:
    packet = build_operator_attention_ledger_packet(source_artifact_paths=_sources(tmp_path))
    assert packet["final_status"] == "ADVISORY_ONLY"
    assert packet["ledger_posture"] in {"STABLE", "WATCH"}
    assert packet["entry_count"] == 1


def test_blocked_propagates(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["operator_attention_weather"]), {"final_status": "BLOCKED", "weather_posture": "BLOCKED", "attention_urgency": "CRITICAL", "blocker_summary": ["x"], "weather_hash": "wh-b"})
    packet = build_operator_attention_ledger_packet(source_artifact_paths=src)
    assert packet["final_status"] == "BLOCKED"
    assert packet["ledger_posture"] == "BLOCKED"


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_operator_attention_ledger_packet(source_artifact_paths=_sources(tmp_path, missing="operator_attention_weather"))
    assert packet["final_status"] == NOT_COMPUTABLE
    assert packet["ledger_posture"] == "BLOCKED"


def test_corrupt_source_fails_closed(tmp_path: Path) -> None:
    packet = build_operator_attention_ledger_packet(source_artifact_paths=_sources(tmp_path, corrupt="operator_review_routing_enhancer"))
    assert packet["final_status"] == NOT_COMPUTABLE


def test_deterministic_entry_id_and_hash(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    a = build_operator_attention_ledger_packet(source_artifact_paths=src)
    b = build_operator_attention_ledger_packet(source_artifact_paths=src)
    assert a["latest_entry"]["entry_id"] == b["latest_entry"]["entry_id"]
    assert a["ledger_hash"] == b["ledger_hash"]


def test_entries_sorted_deterministically() -> None:
    packet = build_operator_attention_ledger_packet(
        source_packets={
            "operator_attention_weather": {"final_status": "ADVISORY_ONLY", "weather_posture": "WATCH", "attention_urgency": "MEDIUM", "blocker_summary": [], "weather_hash": "B"},
            "operator_review_routing_enhancer": {"final_status": "ADVISORY_ONLY", "routing_posture": "WATCH", "review_priority_posture": "MEDIUM", "blocker_summary": [], "enhancer_hash": "A"},
        },
        source_artifact_paths={},
    )
    ids = [e["entry_id"] for e in packet["entries"]]
    assert ids == sorted(ids)


def test_governance_flags_locked(tmp_path: Path) -> None:
    flags = build_operator_attention_ledger_packet(source_artifact_paths=_sources(tmp_path))["governance_flags"]
    assert flags["advisory_only"] is True and flags["projection_only"] is True and flags["ledger_only"] is True
    assert all(flags[k] is False for k in ["mutation_allowed", "authority_granted", "execution_authority", "forecast_authority", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed", "runtime_mutation_allowed", "adaptive_behavior_allowed", "auto_learning_allowed", "auto_execute", "auto_approve", "command_channel", "bidirectional_control"])


def test_inputs_not_mutated() -> None:
    src_packets = {
        "operator_attention_weather": {"final_status": "ADVISORY_ONLY", "weather_posture": "WATCH", "attention_urgency": "MEDIUM", "blocker_summary": [], "weather_hash": "wh"},
        "operator_review_routing_enhancer": {"final_status": "ADVISORY_ONLY", "routing_posture": "WATCH", "review_priority_posture": "MEDIUM", "blocker_summary": [], "enhancer_hash": "rh"},
    }
    before = deepcopy(src_packets)
    build_operator_attention_ledger_packet(source_packets=src_packets, source_artifact_paths={})
    assert before == src_packets


def test_writer_emits_final_newline(tmp_path: Path) -> None:
    packet = build_operator_attention_ledger_packet(source_artifact_paths=_sources(tmp_path))
    out = tmp_path / "p31.json"
    write_operator_attention_ledger_packet(out, packet)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")


def test_schema_shape_present() -> None:
    schema = json.loads(Path("contracts/operator_attention/operator_attention_ledger.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "OperatorAttentionLedger.v1"


def test_registry_classification_derived_optional() -> None:
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    j = next(e for e in registry.entries if e.artifact_path == "out/projections/operator_attention_ledger_001.latest.json")
    m = next(e for e in registry.entries if e.artifact_path == "out/projections/operator_attention_ledger_001.latest.md")
    assert j.determinism_class == "DERIVED_OPTIONAL"
    assert m.determinism_class == "DERIVED_OPTIONAL"
    assert j.artifact_path not in list_ci_drift_artifact_paths(registry)

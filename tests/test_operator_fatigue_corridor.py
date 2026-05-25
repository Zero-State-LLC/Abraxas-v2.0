from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths
from core.operator_fatigue_corridor import (
    NOT_COMPUTABLE,
    build_operator_fatigue_corridor_packet,
    write_operator_fatigue_corridor_packet,
)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _ledger(entries: list[dict] | None = None, *, final_status: str = "ADVISORY_ONLY", ledger_posture: str = "STABLE", blockers: list[str] | None = None) -> dict:
    return {
        "final_status": final_status,
        "ledger_posture": ledger_posture,
        "entries": entries or [],
        "blocker_summary": blockers or [],
        "ledger_hash": "lh-1",
    }


def _entry(*, urgency: str = "LOW", routing_posture: str = "NORMAL", weather_posture: str = "CLEAR", blockers: list[str] | None = None, entry_hash: str = "eh-1") -> dict:
    return {
        "attention_urgency": urgency,
        "routing_posture": routing_posture,
        "weather_posture": weather_posture,
        "blocker_summary": blockers or [],
        "entry_hash": entry_hash,
    }


def test_healthy_ledger_clear_or_watch() -> None:
    p = build_operator_fatigue_corridor_packet(source_packets={"operator_attention_ledger": _ledger(entries=[_entry()])}, source_artifact_paths={})
    assert p["corridor_status"] in {"CLEAR", "WATCH"}


def test_blocked_ledger_produces_blocked_persistence() -> None:
    p = build_operator_fatigue_corridor_packet(source_packets={"operator_attention_ledger": _ledger(entries=[_entry(urgency="CRITICAL", routing_posture="BLOCKED")], final_status="BLOCKED", ledger_posture="BLOCKED")}, source_artifact_paths={})
    assert p["final_status"] == "BLOCKED"
    assert p["corridor_status"] == "BLOCKED_PERSISTENCE"


def test_repeated_critical_detects_pressure_persistence() -> None:
    p = build_operator_fatigue_corridor_packet(source_packets={"operator_attention_ledger": _ledger(entries=[_entry(urgency="CRITICAL", entry_hash="eh-1"), _entry(urgency="CRITICAL", entry_hash="eh-2")])}, source_artifact_paths={})
    assert p["corridor_status"] == "PRESSURE_PERSISTENCE"


def test_recurring_blockers_normalized_sorted() -> None:
    p = build_operator_fatigue_corridor_packet(source_packets={"operator_attention_ledger": _ledger(entries=[_entry(blockers=["Z-Block", "a-block"]), _entry(blockers=["a-block"], entry_hash="eh-2")])}, source_artifact_paths={})
    assert p["recurring_blocker_classes"] == ["a-block", "z-block"]


def test_missing_fails_closed(tmp_path: Path) -> None:
    p = build_operator_fatigue_corridor_packet(source_artifact_paths={"operator_attention_ledger": (tmp_path / "missing.json").as_posix()})
    assert p["final_status"] == NOT_COMPUTABLE
    assert p["corridor_status"] == NOT_COMPUTABLE


def test_corrupt_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{bad", encoding="utf-8")
    p = build_operator_fatigue_corridor_packet(source_artifact_paths={"operator_attention_ledger": path.as_posix()})
    assert p["final_status"] == NOT_COMPUTABLE


def test_deterministic_corridor_hash() -> None:
    src = {"operator_attention_ledger": _ledger(entries=[_entry()])}
    a = build_operator_fatigue_corridor_packet(source_packets=src, source_artifact_paths={})
    b = build_operator_fatigue_corridor_packet(source_packets=src, source_artifact_paths={})
    assert a["corridor_hash"] == b["corridor_hash"]


def test_evidence_refs_hash_only() -> None:
    p = build_operator_fatigue_corridor_packet(source_packets={"operator_attention_ledger": _ledger(entries=[_entry(entry_hash="eh-1")], blockers=["x"])} , source_artifact_paths={})
    assert all(ref.startswith("ledger_hash:") or ref.startswith("entry_hash:") for ref in p["evidence_refs"])


def test_governance_flags_locked_and_no_psych_claims() -> None:
    g = build_operator_fatigue_corridor_packet(source_packets={"operator_attention_ledger": _ledger(entries=[_entry()])}, source_artifact_paths={})["governance_flags"]
    assert g["psychological_claims_allowed"] is False
    assert g["advisory_only"] is True and g["projection_only"] is True and g["detector_only"] is True
    assert all(g[k] is False for k in ["adaptive_behavior_allowed", "threshold_self_modification_allowed", "mutation_allowed", "authority_granted", "execution_authority", "forecast_authority", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed", "runtime_mutation_allowed", "auto_execute", "auto_approve", "command_channel", "bidirectional_control"])


def test_input_not_mutated() -> None:
    src_packets = {"operator_attention_ledger": _ledger(entries=[_entry()])}
    before = deepcopy(src_packets)
    build_operator_fatigue_corridor_packet(source_packets=src_packets, source_artifact_paths={})
    assert src_packets == before


def test_writer_emits_final_newline(tmp_path: Path) -> None:
    packet = build_operator_fatigue_corridor_packet(source_packets={"operator_attention_ledger": _ledger(entries=[_entry()])}, source_artifact_paths={})
    out = tmp_path / "p32.json"
    write_operator_fatigue_corridor_packet(out, packet)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")


def test_schema_shape_present() -> None:
    schema = json.loads(Path("contracts/operator_attention/operator_fatigue_corridor.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "OperatorFatigueCorridor.v1"


def test_registry_classification_derived_optional() -> None:
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    j = next(e for e in registry.entries if e.artifact_path == "out/projections/operator_fatigue_corridor_001.latest.json")
    m = next(e for e in registry.entries if e.artifact_path == "out/projections/operator_fatigue_corridor_001.latest.md")
    assert j.determinism_class == "DERIVED_OPTIONAL"
    assert m.determinism_class == "DERIVED_OPTIONAL"
    assert j.artifact_path not in list_ci_drift_artifact_paths(registry)

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths
from core.pressure_motif_registry import build_pressure_motif_registry_packet, write_pressure_motif_registry_packet


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _sources(tmp_path: Path, *, missing: str | None = None, corrupt: str | None = None) -> dict[str, str]:
    src = {
        "operator_fatigue_corridor": tmp_path / "p32.json",
        "continuity_degradation_explainer": tmp_path / "p33.json",
        "operator_climatology_summary": tmp_path / "p34.json",
        "aal_viz_operator_climate_overlay": tmp_path / "p35.json",
    }
    packets = {
        "operator_fatigue_corridor": {"final_status": "ADVISORY_DEGRADED", "corridor_status": "PRESSURE_PERSISTENCE", "recurring_blocker_classes": ["Queue Lag"], "evidence_refs": ["corridor_hash:a"], "blocker_summary": [], "pressure_persistence_detected": True},
        "continuity_degradation_explainer": {"final_status": "ADVISORY_ONLY", "dominant_degradation_vectors": ["CORRIDOR_PRESSURE_PERSISTENCE"], "recurring_blocker_classes": ["queue lag"], "evidence_refs": ["explainer_hash:b"], "blocker_summary": []},
        "operator_climatology_summary": {"final_status": "ADVISORY_ONLY", "blocker_class_counts": {"queue lag": 2}, "degradation_vector_counts": {"CORRIDOR_PRESSURE_PERSISTENCE": 3}, "weather_posture_counts": {"WATCH": 1}, "attention_urgency_counts": {"HIGH": 1}, "routing_posture_counts": {"WATCH": 1}, "review_priority_posture_counts": {"MEDIUM": 1}, "ledger_posture_counts": {"WATCH": 1}, "corridor_status_counts": {"PRESSURE_PERSISTENCE": 1}, "blocker_summary": []},
        "aal_viz_operator_climate_overlay": {"final_status": "PROJECTION_DEGRADED", "climate_summary": {"source_hash_lineage": {"operator_fatigue_corridor": "h1"}}, "blocker_summary": []},
    }
    for k, p in packets.items():
        if k == missing:
            continue
        if k == corrupt:
            src[k].parent.mkdir(parents=True, exist_ok=True)
            src[k].write_text("{", encoding="utf-8")
            continue
        _write(src[k], p)
    return {k: v.as_posix() for k, v in src.items()}


def test_healthy_sources_and_determinism(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    a = build_pressure_motif_registry_packet(source_artifact_paths=src)
    b = build_pressure_motif_registry_packet(source_artifact_paths=src)
    assert a["final_status"] == "ADVISORY_DEGRADED"
    assert a["registry_posture"] == "PRESSURE_PERSISTENCE"
    assert a["motif_count"] > 0
    assert a["registry_hash"] == b["registry_hash"]
    assert [m["motif_id"] for m in a["motif_catalog"]] == sorted(m["motif_id"] for m in a["motif_catalog"])


def test_blocked_propagates(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["operator_climatology_summary"]), {"final_status": "BLOCKED"})
    p = build_pressure_motif_registry_packet(source_artifact_paths=src)
    assert p["final_status"] == "BLOCKED"
    assert p["registry_posture"] == "BLOCKED"


def test_missing_corrupt_fail_closed(tmp_path: Path) -> None:
    p1 = build_pressure_motif_registry_packet(source_artifact_paths=_sources(tmp_path / "m", missing="operator_fatigue_corridor"))
    p2 = build_pressure_motif_registry_packet(source_artifact_paths=_sources(tmp_path / "c", corrupt="operator_fatigue_corridor"))
    assert p1["final_status"] == "NOT_COMPUTABLE"
    assert p2["final_status"] == "NOT_COMPUTABLE"


def test_hash_evidence_lineage_and_write(tmp_path: Path) -> None:
    p = build_pressure_motif_registry_packet(source_artifact_paths=_sources(tmp_path))
    assert p["motif_evidence_refs"] == sorted(set(p["motif_evidence_refs"]))
    for m in p["motif_catalog"]:
        clone = {k: v for k, v in m.items() if k != "motif_hash"}
        assert m["motif_hash"]
        assert "motif_hash" not in clone
    out = tmp_path / "p36.json"
    write_pressure_motif_registry_packet(out, p)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")


def test_input_not_mutated_and_governance_and_registry_class() -> None:
    packets = {
        "operator_fatigue_corridor": {"final_status": "ADVISORY_ONLY", "corridor_status": "WATCH", "recurring_blocker_classes": [], "evidence_refs": [], "blocker_summary": []},
        "continuity_degradation_explainer": {"final_status": "ADVISORY_ONLY", "dominant_degradation_vectors": [], "recurring_blocker_classes": [], "evidence_refs": [], "blocker_summary": []},
        "operator_climatology_summary": {"final_status": "ADVISORY_ONLY", "blocker_class_counts": {}, "degradation_vector_counts": {}, "blocker_summary": []},
        "aal_viz_operator_climate_overlay": {"final_status": "PROJECTION_ONLY", "climate_summary": {"source_hash_lineage": {}}, "blocker_summary": []},
    }
    before = deepcopy(packets)
    p = build_pressure_motif_registry_packet(source_packets=packets, source_artifact_paths={})
    assert packets == before
    g = p["governance_flags"]
    assert g["advisory_only"] is True and g["projection_only"] is True and g["registry_only"] is True and g["observed_only"] is True
    assert all(g[k] is False for k in ["prediction_allowed", "forecast_authority", "readiness_claims_allowed", "motif_learning_authority", "adaptive_ontology_mutation_allowed", "psychological_claims_allowed", "speculative_causation_allowed", "mutation_allowed", "authority_granted", "execution_authority", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed", "runtime_mutation_allowed", "auto_execute", "auto_approve", "command_channel", "bidirectional_control"])

    schema = json.loads(Path("contracts/operator_attention/pressure_motif_registry.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "PressureMotifRegistry.v1"
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    j = next(e for e in registry.entries if e.artifact_path == "out/projections/pressure_motif_registry_001.latest.json")
    m = next(e for e in registry.entries if e.artifact_path == "out/projections/pressure_motif_registry_001.latest.md")
    assert j.determinism_class == "DERIVED_OPTIONAL"
    assert m.determinism_class == "DERIVED_OPTIONAL"
    assert j.artifact_path not in list_ci_drift_artifact_paths(registry)

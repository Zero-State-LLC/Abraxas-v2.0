from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths
from core.operator_load_seasonality_surface import build_operator_load_seasonality_surface_packet, write_operator_load_seasonality_surface_packet


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _sources(tmp_path: Path, *, missing: str | None = None, corrupt: str | None = None, p38: str = "PASS", pressure: bool = False) -> dict[str, str]:
    src = {k: tmp_path / f"{k}.json" for k in ["operator_attention_ledger", "operator_fatigue_corridor", "continuity_degradation_explainer", "operator_climatology_summary", "pressure_motif_registry", "motif_governance_audit"]}
    packets = {
        "operator_attention_ledger": {"final_status": "ADVISORY_ONLY", "ledger_posture": "WATCH", "ledger_hash": "h31", "blocker_summary": []},
        "operator_fatigue_corridor": {"final_status": "ADVISORY_DEGRADED" if pressure else "ADVISORY_ONLY", "corridor_status": "PRESSURE_PERSISTENCE" if pressure else "WATCH", "pressure_persistence_detected": pressure, "corridor_hash": "h32", "blocker_summary": []},
        "continuity_degradation_explainer": {"final_status": "ADVISORY_ONLY", "explanation_posture": "WATCH", "dominant_degradation_vectors": ["A", "A"], "explainer_hash": "h33", "blocker_summary": []},
        "operator_climatology_summary": {"final_status": "ADVISORY_ONLY", "climatology_posture": "WATCH", "degradation_vector_counts": {"A": 2}, "corridor_status_counts": {"WATCH": 1}, "summary_hash": "h34", "blocker_summary": []},
        "pressure_motif_registry": {"final_status": "ADVISORY_ONLY", "registry_posture": "PRESSURE_PERSISTENCE" if pressure else "WATCH", "motif_class_counts": {"BLOCKER_CLASS": 2}, "motif_catalog": [{"motif_class": "DEGRADATION_VECTOR", "motif_label": "A"}], "registry_hash": "h36", "blocker_summary": []},
        "motif_governance_audit": {"final_status": p38, "audit_posture": p38, "audit_hash": "h38", "blocker_summary": []},
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


def test_recurrence_and_sorted_maps(tmp_path: Path) -> None:
    p = build_operator_load_seasonality_surface_packet(source_artifact_paths=_sources(tmp_path))
    assert p["final_status"] == "ADVISORY_ONLY"
    assert p["seasonality_posture"] == "RECURRENCE_OBSERVED"
    assert p["observed_recurrence_classes"] == sorted(p["observed_recurrence_classes"])
    for key in ["load_posture_counts", "pressure_motif_class_counts", "degradation_vector_counts", "corridor_status_counts", "audit_status_counts"]:
        assert list(p[key].keys()) == sorted(p[key].keys())


def test_pressure_persistence_and_warn_fail_blocked(tmp_path: Path) -> None:
    assert build_operator_load_seasonality_surface_packet(source_artifact_paths=_sources(tmp_path / "a", pressure=True))["seasonality_posture"] == "PRESSURE_PERSISTENCE"
    warn = build_operator_load_seasonality_surface_packet(source_artifact_paths=_sources(tmp_path / "b", p38="WARN"))
    assert warn["final_status"] == "ADVISORY_DEGRADED"
    fail = build_operator_load_seasonality_surface_packet(source_artifact_paths=_sources(tmp_path / "c", p38="FAIL"))
    assert fail["final_status"] == "BLOCKED"


def test_missing_corrupt_hash_lineage_and_immutability_and_writer(tmp_path: Path) -> None:
    assert build_operator_load_seasonality_surface_packet(source_artifact_paths=_sources(tmp_path / "m", missing="operator_attention_ledger"))["final_status"] == "NOT_COMPUTABLE"
    assert build_operator_load_seasonality_surface_packet(source_artifact_paths=_sources(tmp_path / "c", corrupt="operator_attention_ledger"))["final_status"] == "NOT_COMPUTABLE"

    p = build_operator_load_seasonality_surface_packet(source_artifact_paths=_sources(tmp_path / "h"))
    assert set(p["source_hash_lineage"].keys()) == {"ledger_hash", "corridor_hash", "explainer_hash", "summary_hash", "registry_hash", "audit_hash"}
    out = tmp_path / "p39.json"
    write_operator_load_seasonality_surface_packet(out, p)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    packets = {"operator_attention_ledger": {}, "operator_fatigue_corridor": {}, "continuity_degradation_explainer": {}, "operator_climatology_summary": {}, "pressure_motif_registry": {}, "motif_governance_audit": {}}
    before = deepcopy(packets)
    build_operator_load_seasonality_surface_packet(source_packets=packets, source_artifact_paths={})
    assert packets == before


def test_schema_governance_and_registry_classification() -> None:
    schema = json.loads(Path("contracts/operator_attention/operator_load_seasonality_surface.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "OperatorLoadSeasonalitySurface.v1"
    packet = build_operator_load_seasonality_surface_packet(source_packets={"operator_attention_ledger": {}, "operator_fatigue_corridor": {}, "continuity_degradation_explainer": {}, "operator_climatology_summary": {}, "pressure_motif_registry": {}, "motif_governance_audit": {}}, source_artifact_paths={})
    g = packet["governance_flags"]
    deny = ["prediction_allowed","forecast_authority","trend_prediction_allowed","readiness_claims_allowed","adaptive_thresholds_allowed","psychological_claims_allowed","speculative_causation_allowed","mutation_allowed","authority_granted","execution_authority","routing_change_allowed","queue_mutation_allowed","canon_mutation_allowed","runtime_mutation_allowed","auto_execute","auto_approve","command_channel","bidirectional_control"]
    assert g["advisory_only"] and g["projection_only"] and g["seasonality_only"] and g["observation_only"] and g["non_authoritative"]
    assert all(g[k] is False for k in deny)

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    j = next(e for e in registry.entries if e.artifact_path == "out/projections/operator_load_seasonality_001.latest.json")
    m = next(e for e in registry.entries if e.artifact_path == "out/projections/operator_load_seasonality_001.latest.md")
    assert j.determinism_class == "DERIVED_OPTIONAL"
    assert m.determinism_class == "DERIVED_OPTIONAL"
    assert j.artifact_path not in list_ci_drift_artifact_paths(registry)

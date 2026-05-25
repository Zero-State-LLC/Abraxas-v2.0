from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths
from core.operator_narrative_report import build_operator_narrative_report_markdown, build_operator_narrative_report_packet, write_operator_narrative_report_packet


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _sources(tmp_path: Path, *, missing: str | None = None, corrupt: str | None = None, p41: str = "PASS", p31: str = "ADVISORY_ONLY") -> dict[str, str]:
    keys = ["operator_attention_weather","operator_review_routing_enhancer","operator_attention_ledger","operator_fatigue_corridor","continuity_degradation_explainer","operator_climatology_summary","pressure_motif_registry","motif_governance_audit","operator_load_seasonality","aal_viz_climate_motif_fusion_overlay","fusion_governance_audit"]
    src = {k: tmp_path / f"{k}.json" for k in keys}
    packets = {
        "operator_attention_weather": {"final_status": "ADVISORY_ONLY", "weather_posture": "CLEAR", "attention_urgency": "LOW", "weather_hash": "h29", "blocker_summary": []},
        "operator_review_routing_enhancer": {"final_status": "ADVISORY_ONLY", "routing_posture": "NORMAL", "review_priority_posture": "LOW", "enhancer_hash": "h30", "blocker_summary": []},
        "operator_attention_ledger": {"final_status": p31, "ledger_posture": "STABLE", "ledger_hash": "h31", "blocker_summary": ["L1"] if p31!="ADVISORY_ONLY" else []},
        "operator_fatigue_corridor": {"final_status": "ADVISORY_ONLY", "corridor_status": "CLEAR", "corridor_hash": "h32", "blocker_summary": []},
        "continuity_degradation_explainer": {"final_status": "ADVISORY_ONLY", "explanation_posture": "CLEAR", "dominant_degradation_vectors": [], "explainer_hash": "h33", "blocker_summary": []},
        "operator_climatology_summary": {"final_status": "ADVISORY_ONLY", "climatology_posture": "CLEAR", "observed_distribution_summary": {"signal_family_count": 8}, "summary_hash": "h34", "blocker_summary": []},
        "pressure_motif_registry": {"final_status": "ADVISORY_ONLY", "registry_posture": "CLEAR", "motif_count": 2, "registry_hash": "h36", "blocker_summary": []},
        "motif_governance_audit": {"final_status": "PASS", "audit_posture": "CLEAN", "audit_hash": "h38", "blocker_summary": []},
        "operator_load_seasonality": {"final_status": "ADVISORY_ONLY", "seasonality_posture": "CLEAR", "recurrence_summary": {"repeated_class_count": 0}, "seasonality_hash": "h39", "blocker_summary": []},
        "aal_viz_climate_motif_fusion_overlay": {"final_status": "ADVISORY_ONLY", "fusion_posture": "CLEAR", "fusion_hash": "h40", "blocker_summary": []},
        "fusion_governance_audit": {"final_status": p41, "audit_posture": "CLEAN" if p41=="PASS" else "WARNING" if p41=="WARN" else "FAILED", "audit_hash": "h41", "blocker_summary": ["F1"] if p41=="FAIL" else []},
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


def test_status_modes_and_missing_corrupt(tmp_path: Path) -> None:
    assert build_operator_narrative_report_packet(source_artifact_paths=_sources(tmp_path / "h"))["final_status"] == "REPORT_ONLY"
    degraded = build_operator_narrative_report_packet(source_artifact_paths=_sources(tmp_path / "d", p41="WARN"))
    assert degraded["final_status"] == "REPORT_DEGRADED"
    blocked = build_operator_narrative_report_packet(source_artifact_paths=_sources(tmp_path / "b", p41="FAIL"))
    assert blocked["final_status"] == "BLOCKED"
    assert build_operator_narrative_report_packet(source_artifact_paths=_sources(tmp_path / "m", missing="operator_attention_weather"))["final_status"] == "NOT_COMPUTABLE"
    assert build_operator_narrative_report_packet(source_artifact_paths=_sources(tmp_path / "c", corrupt="operator_attention_weather"))["final_status"] == "NOT_COMPUTABLE"


def test_order_markdown_hash_lineage_blockers_stability_and_immutability(tmp_path: Path) -> None:
    packet = build_operator_narrative_report_packet(source_artifact_paths=_sources(tmp_path / "o", p31="ADVISORY_DEGRADED"))
    assert [s["section_id"] for s in packet["report_sections"]] == [
        "executive_signal_state","weather_routing","memory_corridor","degradation_climatology","motifs_motif_governance","seasonality","fusion_overlay_fusion_governance","blockers","governance_boundary","source_lineage"
    ]
    md = build_operator_narrative_report_markdown(packet)
    idx = [md.index(f"## {title}") for title in [
        "Executive Signal State", "Weather + Routing", "Memory + Corridor", "Degradation + Climatology", "Motifs + Motif Governance", "Seasonality", "Fusion Overlay + Fusion Governance", "Blockers", "Governance Boundary", "Source Lineage"
    ]]
    assert idx == sorted(idx)
    assert sorted(packet["source_hash_lineage"].keys()) == ["corridor_hash","enhancer_hash","explainer_hash","fusion_audit_hash","fusion_hash","ledger_hash","motif_audit_hash","registry_hash","seasonality_hash","summary_hash","weather_hash"]
    assert packet["blocker_summary"] == sorted(packet["blocker_summary"])
    twin = build_operator_narrative_report_packet(source_artifact_paths=_sources(tmp_path / "o", p31="ADVISORY_DEGRADED"))
    assert packet["report_hash"] == twin["report_hash"]

    src_packets = {k: {} for k in _sources(tmp_path / "i").keys()}
    before = deepcopy(src_packets)
    build_operator_narrative_report_packet(source_packets=src_packets, source_artifact_paths={})
    assert src_packets == before


def test_writer_schema_governance_registry(tmp_path: Path) -> None:
    packet = build_operator_narrative_report_packet(source_artifact_paths=_sources(tmp_path / "w"))
    out = tmp_path / "p42.json"
    write_operator_narrative_report_packet(out, packet)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    schema = json.loads(Path("contracts/operator_attention/operator_narrative_report.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "OperatorNarrativeReport.v1"

    g = packet["governance_flags"]
    assert g["report_only"] and g["advisory_only"] and g["non_authoritative"] and g["source_linked"] and g["deterministic_template_only"]
    deny = ["inference_authority","prediction_allowed","forecast_authority","trend_prediction_allowed","readiness_claims_allowed","recommendation_authority","action_authority","mutation_allowed","authority_granted","execution_authority","routing_change_allowed","queue_mutation_allowed","canon_mutation_allowed","runtime_mutation_allowed","ui_command_authority","adaptive_behavior_allowed","psychological_claims_allowed","speculative_causation_allowed","auto_execute","auto_approve","command_channel","bidirectional_control"]
    assert all(g[k] is False for k in deny)

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    j = next(e for e in registry.entries if e.artifact_path == "out/reports/operator_narrative_report_001.latest.json")
    m = next(e for e in registry.entries if e.artifact_path == "out/reports/operator_narrative_report_001.latest.md")
    assert j.determinism_class == "DERIVED_OPTIONAL"
    assert m.determinism_class == "DERIVED_OPTIONAL"
    assert j.artifact_path not in list_ci_drift_artifact_paths(registry)

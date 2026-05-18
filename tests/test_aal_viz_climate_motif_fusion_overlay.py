from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.aal_viz_climate_motif_fusion_overlay import (
    NOT_COMPUTABLE,
    build_aal_viz_climate_motif_fusion_overlay_packet,
    write_aal_viz_climate_motif_fusion_overlay_packet,
)
from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _sources(tmp_path: Path, *, missing: str | None = None, corrupt: str | None = None) -> dict[str, Path]:
    src = {
        "aal_viz_operator_climate_overlay": tmp_path / "p35.json",
        "aal_viz_pressure_motif_overlay": tmp_path / "p37.json",
        "operator_load_seasonality": tmp_path / "p39.json",
    }
    p35 = {
        "final_status": "PROJECTION_ONLY",
        "overlay_posture": "CLEAR",
        "overlay_hash": "h35",
        "render_layers": [{"layer_id": "l"}],
        "overlay_nodes": [{"node_id": "node.climatology", "layer_id": "l"}],
        "overlay_cards": [{"card_id": "card.c", "title": "c", "value": "v"}],
        "overlay_badges": [{"badge_id": "badge.c", "token": "c"}],
        "overlay_edges": [{"edge_id": "edge.c", "source_node_id": "node.climatology", "target_node_id": "node.explainer", "relation": "x"}],
        "blocker_summary": [],
    }
    p37 = {
        "final_status": "PROJECTION_ONLY",
        "overlay_posture": "CLEAR",
        "overlay_hash": "h37",
        "render_layers": [{"layer_id": "m"}],
        "overlay_nodes": [{"node_id": "node.motif.motif.degradation_vector.corridor_pressure_persistence", "layer_id": "m"}],
        "overlay_cards": [{"card_id": "card.m", "title": "m", "value": "1"}],
        "overlay_badges": [{"badge_id": "badge.m", "token": "m"}],
        "overlay_edges": [{"edge_id": "edge.m", "source_node_id": "node.motif.motif.degradation_vector.corridor_pressure_persistence", "target_node_id": "node.evidence.1", "relation": "supported_by"}],
        "blocker_summary": [],
    }
    p39 = {
        "final_status": "PROJECTION_ONLY",
        "seasonality_posture": "RECURRENCE_OBSERVED",
        "seasonality_hash": "h39",
        "recurrence_summary": {"repeated_class_count": 3},
        "source_hash_lineage": {"ledger_hash": "a"},
        "blocker_summary": [],
    }
    for k, p in src.items():
        if missing == k:
            continue
        if corrupt == k:
            p.write_text("{", encoding="utf-8")
            continue
        payload = {"aal_viz_operator_climate_overlay": p35, "aal_viz_pressure_motif_overlay": p37, "operator_load_seasonality": p39}[k]
        _write(p, payload)
    return src


def test_happy_path_degraded_blocked_and_fail_closed(tmp_path: Path) -> None:
    p = build_aal_viz_climate_motif_fusion_overlay_packet(source_artifact_paths={k: v.as_posix() for k, v in _sources(tmp_path).items()})
    assert p["final_status"] == "PROJECTION_DEGRADED"
    assert p["fusion_posture"] == "RECURRENCE_OBSERVED"

    src = _sources(tmp_path / "d")
    d = json.loads(src["operator_load_seasonality"].read_text(encoding="utf-8"))
    d["seasonality_posture"] = "PRESSURE_PERSISTENCE"
    d["final_status"] = "PROJECTION_DEGRADED"
    _write(src["operator_load_seasonality"], d)
    p = build_aal_viz_climate_motif_fusion_overlay_packet(source_artifact_paths={k: v.as_posix() for k, v in src.items()})
    assert p["final_status"] == "PROJECTION_DEGRADED"

    srcb = _sources(tmp_path / "b")
    b = json.loads(srcb["aal_viz_pressure_motif_overlay"].read_text(encoding="utf-8"))
    b["final_status"] = "BLOCKED"
    _write(srcb["aal_viz_pressure_motif_overlay"], b)
    p = build_aal_viz_climate_motif_fusion_overlay_packet(source_artifact_paths={k: v.as_posix() for k, v in srcb.items()})
    assert p["final_status"] == "BLOCKED"

    assert build_aal_viz_climate_motif_fusion_overlay_packet(source_artifact_paths={k: v.as_posix() for k, v in _sources(tmp_path / "m", missing="aal_viz_operator_climate_overlay").items()})["final_status"] == NOT_COMPUTABLE
    assert build_aal_viz_climate_motif_fusion_overlay_packet(source_artifact_paths={k: v.as_posix() for k, v in _sources(tmp_path / "c", corrupt="aal_viz_pressure_motif_overlay").items()})["final_status"] == NOT_COMPUTABLE


def test_determinism_prefixes_sorting_edges_lineage_and_write(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    packet = build_aal_viz_climate_motif_fusion_overlay_packet(source_artifact_paths={k: v.as_posix() for k, v in src.items()})
    twin = build_aal_viz_climate_motif_fusion_overlay_packet(source_artifact_paths={k: v.as_posix() for k, v in src.items()})
    assert packet == twin

    assert all(x["layer_id"].startswith(("climate.", "motif.", "seasonality.")) for x in packet["render_layers"])
    assert [x["layer_id"] for x in packet["render_layers"]] == sorted(x["layer_id"] for x in packet["render_layers"])
    assert [x["node_id"] for x in packet["overlay_nodes"]] == sorted(x["node_id"] for x in packet["overlay_nodes"])
    assert [x["card_id"] for x in packet["overlay_cards"]] == sorted(x["card_id"] for x in packet["overlay_cards"])
    assert [x["badge_id"] for x in packet["overlay_badges"]] == sorted(x["badge_id"] for x in packet["overlay_badges"])
    assert [x["edge_id"] for x in packet["overlay_edges"]] == sorted(x["edge_id"] for x in packet["overlay_edges"])
    assert any(e["edge_id"].startswith("fusion.edge.") for e in packet["overlay_edges"])
    assert "p35_overlay_hash" in packet["source_hash_lineage"]

    out = tmp_path / "p40.json"
    write_aal_viz_climate_motif_fusion_overlay_packet(out, packet)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    source_packets = {
        "aal_viz_operator_climate_overlay": {"render_layers": []},
        "aal_viz_pressure_motif_overlay": {"render_layers": []},
        "operator_load_seasonality": {"recurrence_summary": {}},
    }
    before = deepcopy(source_packets)
    build_aal_viz_climate_motif_fusion_overlay_packet(source_packets=source_packets, source_artifact_paths={})
    assert source_packets == before


def test_schema_governance_and_registry() -> None:
    schema = json.loads(Path("contracts/operator_attention/aal_viz_climate_motif_fusion_overlay.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "AALVizClimateMotifFusionOverlay.v1"
    p = build_aal_viz_climate_motif_fusion_overlay_packet(
        source_packets={
            "aal_viz_operator_climate_overlay": {},
            "aal_viz_pressure_motif_overlay": {},
            "operator_load_seasonality": {},
        },
        source_artifact_paths={},
    )
    g = p["governance_flags"]
    deny = [
        "inference_authority", "prediction_allowed", "forecast_authority", "trend_prediction_allowed", "readiness_claims_allowed",
        "mutation_allowed", "authority_granted", "execution_authority", "routing_change_allowed", "queue_mutation_allowed", "canon_mutation_allowed",
        "runtime_mutation_allowed", "ui_command_authority", "adaptive_behavior_allowed", "psychological_claims_allowed", "speculative_causation_allowed",
        "auto_execute", "auto_approve", "command_channel", "bidirectional_control",
    ]
    assert g["advisory_only"] and g["projection_only"] and g["fusion_overlay_only"] and g["render_consumer_only"] and g["non_authoritative"]
    assert all(g[k] is False for k in deny)

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    j = next(e for e in registry.entries if e.artifact_path == "out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.json")
    m = next(e for e in registry.entries if e.artifact_path == "out/projections/aal_viz_climate_motif_fusion_overlay_001.latest.md")
    assert j.determinism_class == "DERIVED_OPTIONAL"
    assert m.determinism_class == "DERIVED_OPTIONAL"
    assert j.artifact_path not in list_ci_drift_artifact_paths(registry)

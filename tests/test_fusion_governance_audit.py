from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.fusion_governance_audit import build_fusion_governance_audit_receipt, write_fusion_governance_audit_receipt
from core.generated_artifact_registry import build_generated_artifact_registry


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _sources(tmp_path: Path, *, missing: str | None = None, corrupt: str | None = None) -> dict[str, str]:
    src = {
        "aal_viz_operator_climate_overlay": tmp_path / "p35.json",
        "aal_viz_pressure_motif_overlay": tmp_path / "p37.json",
        "operator_load_seasonality": tmp_path / "p39.json",
        "aal_viz_climate_motif_fusion_overlay": tmp_path / "p40.json",
    }
    p35 = {"overlay_hash": "h35", "blocker_summary": []}
    p37 = {"overlay_hash": "h37", "blocker_summary": []}
    p39 = {"seasonality_hash": "h39", "blocker_summary": []}
    p40 = {
        "render_layers": [{"layer_id": "climate.a"}, {"layer_id": "motif.b"}, {"layer_id": "seasonality.c"}],
        "overlay_nodes": [{"node_id": "climate.n1"}, {"node_id": "motif.n2"}, {"node_id": "seasonality.n3"}],
        "overlay_cards": [{"card_id": "climate.c1"}, {"card_id": "motif.c2"}, {"card_id": "seasonality.c3"}],
        "overlay_badges": [{"badge_id": "climate.b1"}, {"badge_id": "motif.b2"}, {"badge_id": "seasonality.b3"}],
        "overlay_edges": [
            {"edge_id": "climate.e1", "source_node_id": "climate.n1", "target_node_id": "motif.n2"},
            {"edge_id": "fusion.edge.e2", "source_node_id": "motif.n2", "target_node_id": "seasonality.n3"},
            {"edge_id": "motif.e3", "source_node_id": "motif.n2", "target_node_id": "climate.n1"}
        ],
        "source_hashes": {
            "aal_viz_operator_climate_overlay": "a",
            "aal_viz_pressure_motif_overlay": "b",
            "operator_load_seasonality": "c",
            "aal_viz_climate_motif_fusion_overlay": "d"
        },
        "source_hash_lineage": {"p35_overlay_hash": "h35", "p37_overlay_hash": "h37", "p39_seasonality_hash": "h39"},
        "governance_flags": {
            "advisory_only": True, "projection_only": True, "fusion_overlay_only": True, "render_consumer_only": True, "non_authoritative": True,
            "inference_authority": False, "prediction_allowed": False, "forecast_authority": False, "trend_prediction_allowed": False, "readiness_claims_allowed": False,
            "mutation_allowed": False, "authority_granted": False, "execution_authority": False, "routing_change_allowed": False, "queue_mutation_allowed": False,
            "canon_mutation_allowed": False, "runtime_mutation_allowed": False, "ui_command_authority": False, "adaptive_behavior_allowed": False,
            "psychological_claims_allowed": False, "speculative_causation_allowed": False, "auto_execute": False, "auto_approve": False,
            "command_channel": False, "bidirectional_control": False
        }
    }
    from core.canonical.json import canonical_hash

    p40["fusion_hash"] = canonical_hash(p40)

    payloads = {
        "aal_viz_operator_climate_overlay": p35,
        "aal_viz_pressure_motif_overlay": p37,
        "operator_load_seasonality": p39,
        "aal_viz_climate_motif_fusion_overlay": p40,
    }
    for k, p in src.items():
        if k == missing:
            continue
        if k == corrupt:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("{", encoding="utf-8")
            continue
        _write(p, payloads[k])
    return {k: v.as_posix() for k, v in src.items()}


def test_pass_and_not_computable(tmp_path: Path) -> None:
    assert build_fusion_governance_audit_receipt(source_artifact_paths=_sources(tmp_path))["final_status"] == "PASS"
    assert build_fusion_governance_audit_receipt(source_artifact_paths=_sources(tmp_path / "m", missing="aal_viz_climate_motif_fusion_overlay"))["final_status"] == "NOT_COMPUTABLE"
    assert build_fusion_governance_audit_receipt(source_artifact_paths=_sources(tmp_path / "c", corrupt="aal_viz_operator_climate_overlay"))["final_status"] == "NOT_COMPUTABLE"


def test_failure_modes_and_writer_and_stability(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    p40_path = Path(src["aal_viz_climate_motif_fusion_overlay"])
    p40 = json.loads(p40_path.read_text(encoding="utf-8"))
    p40["overlay_nodes"].append({"node_id": "climate.n1"})
    _write(p40_path, p40)
    assert build_fusion_governance_audit_receipt(source_artifact_paths=src)["final_status"] == "FAIL"

    src2 = _sources(tmp_path / "u")
    p40 = json.loads(Path(src2["aal_viz_climate_motif_fusion_overlay"]).read_text(encoding="utf-8"))
    p40["render_layers"] = list(reversed(p40["render_layers"]))
    _write(Path(src2["aal_viz_climate_motif_fusion_overlay"]), p40)
    assert build_fusion_governance_audit_receipt(source_artifact_paths=src2)["final_status"] == "FAIL"

    src3 = _sources(tmp_path / "e")
    p40 = json.loads(Path(src3["aal_viz_climate_motif_fusion_overlay"]).read_text(encoding="utf-8"))
    p40["overlay_edges"][0]["target_node_id"] = "invalid.unknown"
    _write(Path(src3["aal_viz_climate_motif_fusion_overlay"]), p40)
    assert build_fusion_governance_audit_receipt(source_artifact_paths=src3)["final_status"] == "FAIL"

    src4 = _sources(tmp_path / "g")
    p40 = json.loads(Path(src4["aal_viz_climate_motif_fusion_overlay"]).read_text(encoding="utf-8"))
    p40["governance_flags"]["forecast_authority"] = True
    _write(Path(src4["aal_viz_climate_motif_fusion_overlay"]), p40)
    assert build_fusion_governance_audit_receipt(source_artifact_paths=src4)["final_status"] == "FAIL"

    src5 = _sources(tmp_path / "l")
    p40 = json.loads(Path(src5["aal_viz_climate_motif_fusion_overlay"]).read_text(encoding="utf-8"))
    del p40["source_hash_lineage"]["p35_overlay_hash"]
    _write(Path(src5["aal_viz_climate_motif_fusion_overlay"]), p40)
    assert build_fusion_governance_audit_receipt(source_artifact_paths=src5)["final_status"] == "FAIL"

    src6 = _sources(tmp_path / "h")
    p40 = json.loads(Path(src6["aal_viz_climate_motif_fusion_overlay"]).read_text(encoding="utf-8"))
    p40["fusion_hash"] = "bad"
    _write(Path(src6["aal_viz_climate_motif_fusion_overlay"]), p40)
    assert build_fusion_governance_audit_receipt(source_artifact_paths=src6)["final_status"] == "FAIL"

    receipt = build_fusion_governance_audit_receipt(source_artifact_paths=_sources(tmp_path / "w"))
    twin = build_fusion_governance_audit_receipt(source_artifact_paths=_sources(tmp_path / "w"))
    assert receipt == twin
    out = tmp_path / "audit.json"
    write_fusion_governance_audit_receipt(out, receipt)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")


def test_findings_sorted_immutability_schema_registry(tmp_path: Path) -> None:
    packets = {
        "aal_viz_operator_climate_overlay": {"overlay_hash": "h35"},
        "aal_viz_pressure_motif_overlay": {"overlay_hash": "h37"},
        "operator_load_seasonality": {"seasonality_hash": "h39"},
        "aal_viz_climate_motif_fusion_overlay": {
            "render_layers": [{"layer_id": "climate.a"}, {"layer_id": "motif.b"}, {"layer_id": "seasonality.c"}],
            "overlay_nodes": [{"node_id": "climate.n1"}, {"node_id": "motif.n2"}, {"node_id": "seasonality.n3"}],
            "overlay_cards": [{"card_id": "climate.c1"}, {"card_id": "motif.c2"}, {"card_id": "seasonality.c3"}],
            "overlay_badges": [{"badge_id": "climate.b1"}, {"badge_id": "motif.b2"}, {"badge_id": "seasonality.b3"}],
            "overlay_edges": [{"edge_id": "fusion.edge.e", "source_node_id": "climate.n1", "target_node_id": "motif.n2"}],
            "source_hashes": {"aal_viz_operator_climate_overlay": "a", "aal_viz_pressure_motif_overlay": "b", "operator_load_seasonality": "c", "aal_viz_climate_motif_fusion_overlay": "d"},
            "source_hash_lineage": {"p35_overlay_hash": "h35", "p37_overlay_hash": "h37", "p39_seasonality_hash": "h39"},
            "governance_flags": {"advisory_only": True, "projection_only": True, "fusion_overlay_only": True, "render_consumer_only": True, "non_authoritative": True, "inference_authority": False, "prediction_allowed": False, "forecast_authority": False, "trend_prediction_allowed": False, "readiness_claims_allowed": False, "mutation_allowed": False, "authority_granted": False, "execution_authority": False, "routing_change_allowed": False, "queue_mutation_allowed": False, "canon_mutation_allowed": False, "runtime_mutation_allowed": False, "ui_command_authority": False, "adaptive_behavior_allowed": False, "psychological_claims_allowed": False, "speculative_causation_allowed": False, "auto_execute": False, "auto_approve": False, "command_channel": False, "bidirectional_control": False},
            "fusion_hash": "x"
        }
    }
    from core.canonical.json import canonical_hash

    packets["aal_viz_climate_motif_fusion_overlay"]["fusion_hash"] = canonical_hash({k: v for k, v in packets["aal_viz_climate_motif_fusion_overlay"].items() if k != "fusion_hash"})
    before = deepcopy(packets)
    r = build_fusion_governance_audit_receipt(source_packets=packets, source_artifact_paths={})
    assert packets == before
    order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    assert r["findings"] == sorted(r["findings"], key=lambda x: (order.get(str(x["severity"]), 9), str(x["category"]), str(x["finding_id"])))

    schema = json.loads(Path("contracts/operator_attention/fusion_governance_audit.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "FusionGovernanceAudit.v1"

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    j = next(e for e in registry.entries if e.artifact_path == "out/audit/fusion_governance_audit_001.latest.json")
    m = next(e for e in registry.entries if e.artifact_path == "out/audit/fusion_governance_audit_001.latest.md")
    assert j.determinism_class == "DERIVED_OPTIONAL"
    assert m.determinism_class == "DERIVED_OPTIONAL"

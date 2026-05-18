from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from core.aal_viz_pressure_motif_overlay import (
    NOT_COMPUTABLE,
    build_aal_viz_pressure_motif_overlay_packet,
    write_aal_viz_pressure_motif_overlay_packet,
)
from core.generated_artifact_registry import build_generated_artifact_registry, list_ci_drift_artifact_paths


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _sources(tmp_path: Path, *, missing_reg: bool = False, corrupt_reg: bool = False, missing_p35: bool = False) -> dict[str, str]:
    src = {
        "pressure_motif_registry": tmp_path / "p36.json",
        "aal_viz_operator_climate_overlay": tmp_path / "p35.json",
    }
    p36 = {
        "final_status": "ADVISORY_ONLY",
        "registry_posture": "CLEAR",
        "motif_catalog": [{"motif_id": "motif.blocker_class.abc", "motif_class": "BLOCKER_CLASS", "motif_label": "queue lag", "observed_count": 2, "source_surfaces": ["s"], "evidence_refs": ["e1"], "motif_hash": "mh1"}],
        "motif_count": 1,
        "motif_class_counts": {"BLOCKER_CLASS": 1},
        "motif_evidence_refs": ["e1"],
        "source_hash_lineage": {"x": "h"},
        "blocker_summary": [],
    }
    p35 = {"overlay_hash": "oh", "blocker_summary": []}
    if not missing_reg:
        if corrupt_reg:
            src["pressure_motif_registry"].parent.mkdir(parents=True, exist_ok=True)
            src["pressure_motif_registry"].write_text("{", encoding="utf-8")
        else:
            _write(src["pressure_motif_registry"], p36)
    if not missing_p35:
        _write(src["aal_viz_operator_climate_overlay"], p35)
    return {k: v.as_posix() for k, v in src.items()}


def test_healthy_overlay(tmp_path: Path) -> None:
    p = build_aal_viz_pressure_motif_overlay_packet(source_artifact_paths=_sources(tmp_path))
    assert p["final_status"] == "PROJECTION_ONLY"
    assert p["overlay_posture"] in {"CLEAR", "WATCH"}


def test_degraded_overlay(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["pressure_motif_registry"]), {"final_status": "ADVISORY_DEGRADED", "registry_posture": "DEGRADED", "motif_catalog": [], "motif_count": 0, "motif_class_counts": {}, "motif_evidence_refs": [], "source_hash_lineage": {}, "blocker_summary": ["b"]})
    p = build_aal_viz_pressure_motif_overlay_packet(source_artifact_paths=src)
    assert p["final_status"] == "PROJECTION_DEGRADED"


def test_blocked_state(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    _write(Path(src["pressure_motif_registry"]), {"final_status": "BLOCKED", "registry_posture": "BLOCKED", "motif_catalog": [], "motif_count": 0, "motif_class_counts": {}, "motif_evidence_refs": [], "source_hash_lineage": {}, "blocker_summary": []})
    p = build_aal_viz_pressure_motif_overlay_packet(source_artifact_paths=src)
    assert p["final_status"] == "BLOCKED"


def test_missing_and_corrupt_fail_closed(tmp_path: Path) -> None:
    assert build_aal_viz_pressure_motif_overlay_packet(source_artifact_paths=_sources(tmp_path / "m", missing_reg=True))["final_status"] == NOT_COMPUTABLE
    assert build_aal_viz_pressure_motif_overlay_packet(source_artifact_paths=_sources(tmp_path / "c", corrupt_reg=True))["final_status"] == NOT_COMPUTABLE


def test_optional_p35_missing_ok(tmp_path: Path) -> None:
    p = build_aal_viz_pressure_motif_overlay_packet(source_artifact_paths=_sources(tmp_path, missing_p35=True))
    assert p["final_status"] == "PROJECTION_ONLY"


def test_sorted_and_stable_and_writer_and_governance(tmp_path: Path) -> None:
    src = _sources(tmp_path)
    a = build_aal_viz_pressure_motif_overlay_packet(source_artifact_paths=src)
    b = build_aal_viz_pressure_motif_overlay_packet(source_artifact_paths=src)
    assert [x["layer_id"] for x in a["render_layers"]] == sorted(x["layer_id"] for x in a["render_layers"])
    assert [x["node_id"] for x in a["overlay_nodes"]] == sorted(x["node_id"] for x in a["overlay_nodes"])
    assert [x["card_id"] for x in a["overlay_cards"]] == sorted(x["card_id"] for x in a["overlay_cards"])
    assert [x["badge_id"] for x in a["overlay_badges"]] == sorted(x["badge_id"] for x in a["overlay_badges"])
    assert [x["edge_id"] for x in a["overlay_edges"]] == sorted(x["edge_id"] for x in a["overlay_edges"])
    assert a["overlay_hash"] == b["overlay_hash"]
    out = tmp_path / "p37.json"
    write_aal_viz_pressure_motif_overlay_packet(out, a)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")
    schema = json.loads(Path("contracts/operator_attention/aal_viz_pressure_motif_overlay.v1.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "AALVizPressureMotifOverlay.v1"
    g = a["governance_flags"]
    assert g["advisory_only"] and g["projection_only"] and g["render_consumer_only"] and g["motif_overlay_only"]


def test_input_not_mutated_and_registry_classification() -> None:
    packets = {
        "pressure_motif_registry": {"final_status": "ADVISORY_ONLY", "registry_posture": "CLEAR", "motif_catalog": [], "motif_count": 0, "motif_class_counts": {}, "motif_evidence_refs": [], "source_hash_lineage": {}, "blocker_summary": []},
        "aal_viz_operator_climate_overlay": {"overlay_hash": "h", "blocker_summary": []},
    }
    before = deepcopy(packets)
    build_aal_viz_pressure_motif_overlay_packet(source_packets=packets, source_artifact_paths={})
    assert packets == before
    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    j = next(e for e in registry.entries if e.artifact_path == "out/projections/aal_viz_pressure_motif_overlay_001.latest.json")
    m = next(e for e in registry.entries if e.artifact_path == "out/projections/aal_viz_pressure_motif_overlay_001.latest.md")
    assert j.determinism_class == "DERIVED_OPTIONAL"
    assert m.determinism_class == "DERIVED_OPTIONAL"
    assert j.artifact_path not in list_ci_drift_artifact_paths(registry)

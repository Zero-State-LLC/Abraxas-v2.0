from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.geometric_projection_spec import (
    SURFACE_FAMILIES,
    build_geometric_projection_spec,
    compute_geometric_projection_spec_hash,
    default_projection_surface_entries,
    serialize_geometric_projection_spec,
    validate_geometric_projection_spec,
)


def _base() -> dict:
    return build_geometric_projection_spec(
        projection_id="GPS-0001",
        source_packet_refs=["GSP-0001"],
        source_registry_refs=["MOR-0001"],
        visual_encoding={
            "color_policy": "authority-safe palette",
            "topology_encoding": "node-edge manifold",
            "metric_encoding": "placeholder glyph",
            "uncertainty_encoding": "band opacity",
            "authority_encoding": "lock badge",
        },
        provenance={
            "source": "geometric-runtime",
            "evidence_refs": ["docs/audits/REPO_AUDIT_METRIC_OPERATOR_REGISTRY_v0_1.md"],
            "generated_by": "tests",
            "upstream_schema_refs": [
                "contracts/canon/geometric_research_item.v1.schema.json",
                "contracts/canon/geometric_signal_packet.v1.schema.json",
                "contracts/canon/metric_operator_registry.v1.schema.json",
            ],
        },
        created_at_utc="2026-05-27T00:00:00Z",
    )


def test_deterministic_hash() -> None:
    assert _base()["canonical_hash"] == _base()["canonical_hash"]


def test_serialization_byte_stable() -> None:
    p = _base()
    assert serialize_geometric_projection_spec(p) == serialize_geometric_projection_spec(p)


def test_default_surface_families_complete() -> None:
    p = _base()
    assert {s["surface_family"] for s in p["projection_surfaces"]} == SURFACE_FAMILIES


def test_empty_surfaces_fails() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        build_geometric_projection_spec(projection_id="x", source_packet_refs=["a"], source_registry_refs=["b"], visual_encoding={"color_policy":"x","topology_encoding":"x","metric_encoding":"x","uncertainty_encoding":"x","authority_encoding":"x"}, provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x", projection_surfaces=[])


def test_duplicate_surface_id_fails() -> None:
    p = _base()
    ss = p["projection_surfaces"] + [p["projection_surfaces"][0]]
    with pytest.raises(ValueError, match="duplicate surface_id"):
        build_geometric_projection_spec(projection_id="x", source_packet_refs=["a"], source_registry_refs=["b"], visual_encoding=p["visual_encoding"], provenance=p["provenance"], created_at_utc="x", projection_surfaces=ss)


def test_unknown_surface_family_fails() -> None:
    p = _base()
    ss = [dict(p["projection_surfaces"][0], surface_family="NOPE")] + p["projection_surfaces"][1:]
    with pytest.raises(ValueError, match="unknown surface_family"):
        build_geometric_projection_spec(projection_id="x", source_packet_refs=["a"], source_registry_refs=["b"], visual_encoding=p["visual_encoding"], provenance=p["provenance"], created_at_utc="x", projection_surfaces=ss)


def test_unknown_metric_placeholder_fails() -> None:
    p = _base()
    ss = [dict(p["projection_surfaces"][0], source_metric_placeholders=["NOPE"])]+p["projection_surfaces"][1:]
    with pytest.raises(ValueError, match="unknown metric placeholder"):
        build_geometric_projection_spec(projection_id="x", source_packet_refs=["a"], source_registry_refs=["b"], visual_encoding=p["visual_encoding"], provenance=p["provenance"], created_at_utc="x", projection_surfaces=ss)


def test_unknown_architecture_target_fails() -> None:
    p = _base()
    ss = [dict(p["projection_surfaces"][0], architecture_targets=["NOPE"])]+p["projection_surfaces"][1:]
    with pytest.raises(ValueError, match="unknown architecture target"):
        build_geometric_projection_spec(projection_id="x", source_packet_refs=["a"], source_registry_refs=["b"], visual_encoding=p["visual_encoding"], provenance=p["provenance"], created_at_utc="x", projection_surfaces=ss)


def test_unknown_status_fails() -> None:
    p = _base()
    ss = [dict(p["projection_surfaces"][0], projection_status="NOPE")]+p["projection_surfaces"][1:]
    with pytest.raises(ValueError, match="unknown projection_status"):
        build_geometric_projection_spec(projection_id="x", source_packet_refs=["a"], source_registry_refs=["b"], visual_encoding=p["visual_encoding"], provenance=p["provenance"], created_at_utc="x", projection_surfaces=ss)


def test_interaction_controls_must_remain_true() -> None:
    p = _base()
    bad = dict(p)
    bad["interaction_model"] = {**p["interaction_model"], "no_runtime_controls": False}
    with pytest.raises(ValueError, match="interaction_model.no_runtime_controls"):
        validate_geometric_projection_spec(bad)


def test_governance_flags_cannot_be_true() -> None:
    p = _base()
    bad = dict(p)
    bad["governance_flags"] = {**p["governance_flags"], "forecast_influence": True}
    with pytest.raises(ValueError, match="forecast_influence"):
        validate_geometric_projection_spec(bad)


def test_hash_excludes_preimage() -> None:
    p = _base()
    changed = {**p, "canonical_hash": "0" * 64}
    assert compute_geometric_projection_spec_hash(changed) == p["canonical_hash"]


def test_hash_changes_when_surface_changes() -> None:
    p = _base()
    ss = [dict(p["projection_surfaces"][0], description="changed")] + p["projection_surfaces"][1:]
    changed = build_geometric_projection_spec(projection_id="x", source_packet_refs=["a"], source_registry_refs=["b"], visual_encoding=p["visual_encoding"], provenance=p["provenance"], created_at_utc="x", projection_surfaces=ss)
    assert changed["canonical_hash"] != p["canonical_hash"]


def test_schema_validation_if_available() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/geometric_projection_spec.v1.schema.json").read_text())
    jsonschema.validate(_base(), schema)


def test_metadata_refs_only_no_object_imports() -> None:
    p = _base()
    text = json.dumps(p)
    assert "core.geometric_research_item" not in text
    assert "core.geometric_signal_packet" not in text
    assert "core.metric_operator_registry" not in text


def test_default_entries_count() -> None:
    assert len(default_projection_surface_entries()) == 10

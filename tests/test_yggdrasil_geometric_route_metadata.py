from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.yggdrasil_geometric_route_metadata import (
    build_yggdrasil_geometric_route_metadata,
    compute_yggdrasil_geometric_route_metadata_hash,
    default_absent_geometric_annotations,
    default_absent_topology_annotations,
    serialize_yggdrasil_geometric_route_metadata,
    validate_yggdrasil_geometric_route_metadata,
)


def _base() -> dict:
    return build_yggdrasil_geometric_route_metadata(
        metadata_id="YGRM-0001",
        route_ref={"route_id": "R-1", "route_label": "shadow-route", "route_scope": "SHADOW_ANALYSIS"},
        source_packet_refs=["GSP-0001"],
        source_registry_refs=["MOR-0001"],
        geometric_annotations=default_absent_geometric_annotations(),
        topology_annotations=default_absent_topology_annotations(),
        metric_operator_refs=[],
        projection_refs=["GPS-0001"],
        provenance={"source": "yggdrasil-shadow", "evidence_refs": ["docs/audits/REPO_AUDIT_GEOMETRIC_PROJECTION_SPEC_v0_1.md"], "generated_by": "tests", "upstream_schema_refs": ["contracts/canon/geometric_signal_packet.v1.schema.json", "contracts/canon/metric_operator_registry.v1.schema.json", "contracts/canon/geometric_projection_spec.v1.schema.json"]},
        created_at_utc="2026-05-27T00:00:00Z",
    )


def test_deterministic_hash() -> None:
    assert _base()["canonical_hash"] == _base()["canonical_hash"]


def test_serialization_byte_stable() -> None:
    p = _base()
    assert serialize_yggdrasil_geometric_route_metadata(p) == serialize_yggdrasil_geometric_route_metadata(p)


def test_default_absent_allows_empty_metric_refs() -> None:
    p = _base()
    assert p["metric_operator_refs"] == []


def test_non_absent_requires_metric_refs() -> None:
    with pytest.raises(ValueError, match="require metric_operator_refs"):
        build_yggdrasil_geometric_route_metadata(metadata_id="x", route_ref={"route_id":"r","route_label":"l","route_scope":"ROUTE_GRAPH"}, source_packet_refs=[], source_registry_refs=[], geometric_annotations={**default_absent_geometric_annotations(), "manifold_context":"OBSERVED"}, topology_annotations=default_absent_topology_annotations(), metric_operator_refs=[], projection_refs=[], provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_route_scope_fails() -> None:
    with pytest.raises(ValueError, match="unknown route_scope"):
        build_yggdrasil_geometric_route_metadata(metadata_id="x", route_ref={"route_id":"r","route_label":"l","route_scope":"NOPE"}, source_packet_refs=[], source_registry_refs=[], geometric_annotations=default_absent_geometric_annotations(), topology_annotations=default_absent_topology_annotations(), metric_operator_refs=[], projection_refs=[], provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_geometric_annotation_fails() -> None:
    with pytest.raises(ValueError, match="geometric annotation"):
        build_yggdrasil_geometric_route_metadata(metadata_id="x", route_ref={"route_id":"r","route_label":"l","route_scope":"ROUTE_GRAPH"}, source_packet_refs=[], source_registry_refs=[], geometric_annotations={**default_absent_geometric_annotations(), "curvature_context":"NOPE"}, topology_annotations=default_absent_topology_annotations(), metric_operator_refs=[], projection_refs=[], provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_topology_annotation_fails() -> None:
    with pytest.raises(ValueError, match="topology annotation"):
        build_yggdrasil_geometric_route_metadata(metadata_id="x", route_ref={"route_id":"r","route_label":"l","route_scope":"ROUTE_GRAPH"}, source_packet_refs=[], source_registry_refs=[], geometric_annotations=default_absent_geometric_annotations(), topology_annotations={**default_absent_topology_annotations(), "edge_topology":"NOPE"}, metric_operator_refs=[], projection_refs=[], provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_metric_operator_ref_fails() -> None:
    with pytest.raises(ValueError, match="unknown metric operator ref"):
        build_yggdrasil_geometric_route_metadata(metadata_id="x", route_ref={"route_id":"r","route_label":"l","route_scope":"ROUTE_GRAPH"}, source_packet_refs=[], source_registry_refs=[], geometric_annotations=default_absent_geometric_annotations(), topology_annotations=default_absent_topology_annotations(), metric_operator_refs=["NOPE"], projection_refs=[], provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_route_effects_cannot_be_true() -> None:
    p = _base()
    bad = dict(p)
    bad["route_effects"] = {**p["route_effects"], "affects_route_selection": True}
    with pytest.raises(ValueError, match="route_effects.affects_route_selection"):
        validate_yggdrasil_geometric_route_metadata(bad)


def test_governance_flags_cannot_be_true() -> None:
    p = _base()
    bad = dict(p)
    bad["governance_flags"] = {**p["governance_flags"], "forecast_influence": True}
    with pytest.raises(ValueError, match="forecast_influence"):
        validate_yggdrasil_geometric_route_metadata(bad)


def test_forbidden_references_rejected() -> None:
    p = _base()
    bad = dict(p)
    bad["provenance"] = {**p["provenance"], "source": "runtime dispatch route selection"}
    with pytest.raises(ValueError, match="forbidden"):
        validate_yggdrasil_geometric_route_metadata(bad)


def test_hash_excludes_preimage() -> None:
    p = _base()
    changed = {**p, "canonical_hash": "0" * 64}
    assert compute_yggdrasil_geometric_route_metadata_hash(changed) == p["canonical_hash"]


def test_hash_changes_on_meaningful_change() -> None:
    p = _base()
    changed = build_yggdrasil_geometric_route_metadata(metadata_id="YGRM-0001", route_ref={"route_id":"R-1","route_label":"shadow-route","route_scope":"SHADOW_ANALYSIS"}, source_packet_refs=["GSP-0002"], source_registry_refs=["MOR-0001"], geometric_annotations=default_absent_geometric_annotations(), topology_annotations=default_absent_topology_annotations(), metric_operator_refs=[], projection_refs=["GPS-0001"], provenance=p["provenance"], created_at_utc="2026-05-27T00:00:00Z")
    assert changed["canonical_hash"] != p["canonical_hash"]


def test_schema_validation_if_available() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/yggdrasil_geometric_route_metadata.v1.schema.json").read_text())
    jsonschema.validate(_base(), schema)


def test_references_are_id_only() -> None:
    p = _base()
    blob = json.dumps(p)
    assert "core.geometric_signal_packet" not in blob
    assert "core.metric_operator_registry" not in blob
    assert "core.geometric_projection_spec" not in blob

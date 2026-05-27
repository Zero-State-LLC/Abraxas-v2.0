from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.oracle_geometric_signal_attachment import (
    build_oracle_geometric_signal_attachment,
    compute_oracle_geometric_signal_attachment_hash,
    serialize_oracle_geometric_signal_attachment,
    validate_oracle_geometric_signal_attachment,
)


def _base() -> dict:
    return build_oracle_geometric_signal_attachment(
        attachment_id="OGSA-0001",
        oracle_surface_ref={"surface_id": "oracle-shadow-1", "surface_type": "ORACLE_SHADOW_PACKET", "surface_scope": "SHADOW"},
        source_signal_packet_refs=["GSP-0001"],
        source_metric_registry_refs=["MOR-0001"],
        source_projection_refs=["GPS-0001"],
        source_route_metadata_refs=["YGRM-0001"],
        attachment_summary="Attach geometric metadata to oracle shadow packet.",
        geometric_attachment_mode="SHADOW_METADATA_ONLY",
        provenance={"source": "oracle-shadow", "evidence_refs": ["docs/audits/REPO_AUDIT_YGGDRASIL_GEOMETRIC_ROUTE_METADATA_v0_1.md"], "generated_by": "tests", "upstream_schema_refs": ["contracts/canon/geometric_signal_packet.v1.schema.json", "contracts/canon/metric_operator_registry.v1.schema.json", "contracts/canon/geometric_projection_spec.v1.schema.json", "contracts/canon/yggdrasil_geometric_route_metadata.v1.schema.json"]},
        created_at_utc="2026-05-27T00:00:00Z",
    )


def test_valid_deterministic_hash() -> None:
    assert _base()["canonical_hash"] == _base()["canonical_hash"]


def test_serialization_byte_stable() -> None:
    p = _base()
    assert serialize_oracle_geometric_signal_attachment(p) == serialize_oracle_geometric_signal_attachment(p)


def test_source_refs_required_unless_not_computable() -> None:
    with pytest.raises(ValueError, match="source_signal_packet_refs required"):
        build_oracle_geometric_signal_attachment(attachment_id="x", oracle_surface_ref={"surface_id":"s","surface_type":"ORACLE_SIGNAL_LAYER","surface_scope":"SHADOW"}, source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[], attachment_summary="x", geometric_attachment_mode="SHADOW_METADATA_ONLY", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_not_computable_allows_empty_source_refs() -> None:
    p = build_oracle_geometric_signal_attachment(attachment_id="x", oracle_surface_ref={"surface_id":"s","surface_type":"ORACLE_SIGNAL_LAYER","surface_scope":"SHADOW"}, source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[], attachment_summary="x", geometric_attachment_mode="NOT_COMPUTABLE", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")
    assert p["source_signal_packet_refs"] == []


def test_unknown_surface_type_fails() -> None:
    with pytest.raises(ValueError, match="unknown surface_type"):
        build_oracle_geometric_signal_attachment(attachment_id="x", oracle_surface_ref={"surface_id":"s","surface_type":"NOPE","surface_scope":"SHADOW"}, source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[], attachment_summary="x", geometric_attachment_mode="NOT_COMPUTABLE", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_surface_scope_fails() -> None:
    with pytest.raises(ValueError, match="unknown surface_scope"):
        build_oracle_geometric_signal_attachment(attachment_id="x", oracle_surface_ref={"surface_id":"s","surface_type":"ORACLE_SIGNAL_LAYER","surface_scope":"NOPE"}, source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[], attachment_summary="x", geometric_attachment_mode="NOT_COMPUTABLE", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_mode_fails() -> None:
    with pytest.raises(ValueError, match="unknown geometric_attachment_mode"):
        build_oracle_geometric_signal_attachment(attachment_id="x", oracle_surface_ref={"surface_id":"s","surface_type":"ORACLE_SIGNAL_LAYER","surface_scope":"SHADOW"}, source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[], attachment_summary="x", geometric_attachment_mode="NOPE", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_oracle_effects_cannot_be_true() -> None:
    p = _base()
    bad = dict(p)
    bad["oracle_effects"] = {**p["oracle_effects"], "affects_oracle_scores": True}
    with pytest.raises(ValueError, match="affects_oracle_scores"):
        validate_oracle_geometric_signal_attachment(bad)


def test_shadow_constraints_cannot_be_false() -> None:
    p = _base()
    bad = dict(p)
    bad["shadow_constraints"] = {**p["shadow_constraints"], "observation_only": False}
    with pytest.raises(ValueError, match="observation_only"):
        validate_oracle_geometric_signal_attachment(bad)


def test_governance_flags_cannot_be_true() -> None:
    p = _base()
    bad = dict(p)
    bad["governance_flags"] = {**p["governance_flags"], "forecast_influence": True}
    with pytest.raises(ValueError, match="forecast_influence"):
        validate_oracle_geometric_signal_attachment(bad)


def test_forbidden_references_rejected() -> None:
    p = _base()
    bad = dict(p)
    bad["provenance"] = {**p["provenance"], "source": "runtime scheduler scoring"}
    with pytest.raises(ValueError, match="forbidden"):
        validate_oracle_geometric_signal_attachment(bad)


def test_hash_excludes_preimage() -> None:
    p = _base()
    changed = {**p, "canonical_hash": "0" * 64}
    assert compute_oracle_geometric_signal_attachment_hash(changed) == p["canonical_hash"]


def test_hash_changes_on_metadata_change() -> None:
    p = _base()
    changed = build_oracle_geometric_signal_attachment(attachment_id="OGSA-0001", oracle_surface_ref=p["oracle_surface_ref"], source_signal_packet_refs=["GSP-0002"], source_metric_registry_refs=["MOR-0001"], source_projection_refs=["GPS-0001"], source_route_metadata_refs=["YGRM-0001"], attachment_summary="Attach geometric metadata to oracle shadow packet.", geometric_attachment_mode="SHADOW_METADATA_ONLY", provenance=p["provenance"], created_at_utc="2026-05-27T00:00:00Z")
    assert changed["canonical_hash"] != p["canonical_hash"]


def test_schema_validation_if_available() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/oracle_geometric_signal_attachment.v1.schema.json").read_text())
    jsonschema.validate(_base(), schema)


def test_id_only_references() -> None:
    p = _base()
    blob = json.dumps(p)
    assert "core.geometric_signal_packet" not in blob
    assert "core.metric_operator_registry" not in blob
    assert "core.geometric_projection_spec" not in blob
    assert "core.yggdrasil_geometric_route_metadata" not in blob

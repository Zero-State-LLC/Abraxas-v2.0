from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.counterfactual_geometry_engine import (
    build_counterfactual_geometry_engine,
    compute_counterfactual_geometry_engine_hash,
    default_branch_declarations,
    serialize_counterfactual_geometry_engine,
    validate_counterfactual_geometry_engine,
)


def _base() -> dict:
    return build_counterfactual_geometry_engine(
        engine_id="CGE-0001",
        source_attachment_refs=["OGSA-0001"],
        source_signal_packet_refs=["GSP-0001"],
        source_metric_registry_refs=["MOR-0001"],
        source_projection_refs=["GPS-0001"],
        source_route_metadata_refs=["YGRM-0001"],
        counterfactual_scope={"domain": "oracle_shadow", "observation_window": "rolling-30", "branch_family": "TEMPORAL_BRANCH", "intended_lane": "SHADOW"},
        branch_declarations=default_branch_declarations(),
        computation_status="METADATA_ONLY",
        provenance={
            "source": "counterfactual-shadow-observation",
            "evidence_refs": ["docs/audits/REPO_AUDIT_HEAVY_TAIL_SIGNAL_CALIBRATOR_v0_1.md"],
            "generated_by": "tests",
            "upstream_schema_refs": [
                "contracts/canon/oracle_geometric_signal_attachment.v1.schema.json",
                "contracts/canon/geometric_signal_packet.v1.schema.json",
                "contracts/canon/metric_operator_registry.v1.schema.json",
                "contracts/canon/geometric_projection_spec.v1.schema.json",
                "contracts/canon/yggdrasil_geometric_route_metadata.v1.schema.json",
            ],
        },
        created_at_utc="2026-05-27T00:00:00Z",
    )


def test_deterministic_hash() -> None:
    assert _base()["canonical_hash"] == _base()["canonical_hash"]


def test_serialization_stable() -> None:
    p = _base()
    assert serialize_counterfactual_geometry_engine(p) == serialize_counterfactual_geometry_engine(p)


def test_default_branches_non_empty() -> None:
    a = default_branch_declarations()
    b = default_branch_declarations()
    assert a and a == b


def test_duplicate_branch_id_fails() -> None:
    branches = default_branch_declarations() * 2
    with pytest.raises(ValueError, match="duplicate branch_id"):
        build_counterfactual_geometry_engine(engine_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[], counterfactual_scope={"domain":"d","observation_window":"w","branch_family":"TEMPORAL_BRANCH","intended_lane":"SHADOW"}, branch_declarations=branches, computation_status="DECLARED_ONLY", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_intended_lane_fails() -> None:
    with pytest.raises(ValueError, match="unknown intended_lane"):
        build_counterfactual_geometry_engine(engine_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[], counterfactual_scope={"domain":"d","observation_window":"w","branch_family":"TEMPORAL_BRANCH","intended_lane":"NOPE"}, branch_declarations=default_branch_declarations(), computation_status="DECLARED_ONLY", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_branch_family_fails() -> None:
    with pytest.raises(ValueError, match="unknown branch_family"):
        build_counterfactual_geometry_engine(engine_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[], counterfactual_scope={"domain":"d","observation_window":"w","branch_family":"NOPE","intended_lane":"SHADOW"}, branch_declarations=default_branch_declarations(), computation_status="DECLARED_ONLY", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_branch_type_fails() -> None:
    b = default_branch_declarations()
    b[0]["branch_type"] = "NOPE"
    with pytest.raises(ValueError, match="unknown branch_type"):
        build_counterfactual_geometry_engine(engine_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[], counterfactual_scope={"domain":"d","observation_window":"w","branch_family":"TEMPORAL_BRANCH","intended_lane":"SHADOW"}, branch_declarations=b, computation_status="DECLARED_ONLY", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_declared_use_fails() -> None:
    b = default_branch_declarations()
    b[0]["declared_use"] = "NOPE"
    with pytest.raises(ValueError, match="unknown declared_use"):
        build_counterfactual_geometry_engine(engine_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[], counterfactual_scope={"domain":"d","observation_window":"w","branch_family":"TEMPORAL_BRANCH","intended_lane":"SHADOW"}, branch_declarations=b, computation_status="DECLARED_ONLY", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_evidence_required_fails() -> None:
    b = default_branch_declarations()
    b[0]["evidence_required"] = ["NOPE"]
    with pytest.raises(ValueError, match="unknown evidence_required"):
        build_counterfactual_geometry_engine(engine_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[], counterfactual_scope={"domain":"d","observation_window":"w","branch_family":"TEMPORAL_BRANCH","intended_lane":"SHADOW"}, branch_declarations=b, computation_status="DECLARED_ONLY", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_implementation_status_fails() -> None:
    b = default_branch_declarations()
    b[0]["implementation_status"] = "NOPE"
    with pytest.raises(ValueError, match="unknown implementation_status"):
        build_counterfactual_geometry_engine(engine_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[], counterfactual_scope={"domain":"d","observation_window":"w","branch_family":"TEMPORAL_BRANCH","intended_lane":"SHADOW"}, branch_declarations=b, computation_status="DECLARED_ONLY", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_policy_locks() -> None:
    p = _base()
    p1 = dict(p)
    p1["geometry_policy"] = {**p["geometry_policy"], "geometry_computed": True}
    with pytest.raises(ValueError, match="geometry_policy.geometry_computed"):
        validate_counterfactual_geometry_engine(p1)

    p2 = dict(p)
    p2["diffusion_policy"] = {**p["diffusion_policy"], "generated_scenarios": True}
    with pytest.raises(ValueError, match="diffusion_policy.generated_scenarios"):
        validate_counterfactual_geometry_engine(p2)

    p3 = dict(p)
    p3["comparison_policy"] = {**p["comparison_policy"], "affects_forecast": True}
    with pytest.raises(ValueError, match="comparison_policy.affects_forecast"):
        validate_counterfactual_geometry_engine(p3)

    p4 = dict(p)
    p4["output_contract"] = {**p["output_contract"], "emits_branch_scores": True}
    with pytest.raises(ValueError, match="output_contract.emits_branch_scores"):
        validate_counterfactual_geometry_engine(p4)


def test_governance_flags_cannot_be_true() -> None:
    p = _base()
    bad = dict(p)
    bad["governance_flags"] = {**p["governance_flags"], "runtime_authority": True}
    with pytest.raises(ValueError, match="runtime_authority"):
        validate_counterfactual_geometry_engine(bad)


def test_forbidden_provenance_references() -> None:
    p = _base()
    bad = dict(p)
    bad["provenance"] = {**p["provenance"], "source": "scenario-generation probability scoring runtime"}
    with pytest.raises(ValueError, match="forbidden"):
        validate_counterfactual_geometry_engine(bad)


def test_hash_preimage_excludes_hash() -> None:
    p = _base()
    changed = {**p, "canonical_hash": "0" * 64}
    assert compute_counterfactual_geometry_engine_hash(changed) == p["canonical_hash"]


def test_hash_changes_on_change() -> None:
    p = _base()
    changed = build_counterfactual_geometry_engine(
        engine_id="CGE-0001",
        source_attachment_refs=["OGSA-0002"],
        source_signal_packet_refs=["GSP-0001"],
        source_metric_registry_refs=["MOR-0001"],
        source_projection_refs=["GPS-0001"],
        source_route_metadata_refs=["YGRM-0001"],
        counterfactual_scope={"domain": "oracle_shadow", "observation_window": "rolling-30", "branch_family": "TEMPORAL_BRANCH", "intended_lane": "SHADOW"},
        branch_declarations=default_branch_declarations(),
        computation_status="METADATA_ONLY",
        provenance=p["provenance"],
        created_at_utc="2026-05-27T00:00:00Z",
    )
    assert changed["canonical_hash"] != p["canonical_hash"]


def test_schema_validation_if_available() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/counterfactual_geometry_engine.v1.schema.json").read_text())
    jsonschema.validate(_base(), schema)


def test_id_only_references() -> None:
    blob = json.dumps(_base())
    assert "core.oracle_geometric_signal_attachment" not in blob
    assert "core.geometric_signal_packet" not in blob
    assert "core.metric_operator_registry" not in blob
    assert "core.geometric_projection_spec" not in blob
    assert "core.yggdrasil_geometric_route_metadata" not in blob

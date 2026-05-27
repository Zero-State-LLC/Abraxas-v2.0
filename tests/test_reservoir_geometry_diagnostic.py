from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.reservoir_geometry_diagnostic import (
    build_reservoir_geometry_diagnostic,
    compute_reservoir_geometry_diagnostic_hash,
    default_reservoir_declarations,
    serialize_reservoir_geometry_diagnostic,
    validate_reservoir_geometry_diagnostic,
)


def _base() -> dict:
    return build_reservoir_geometry_diagnostic(
        diagnostic_id="RGD-0001",
        source_attachment_refs=["OGSA-0001"],
        source_signal_packet_refs=["GSP-0001"],
        source_metric_registry_refs=["MOR-0001"],
        source_projection_refs=["GPS-0001"],
        source_route_metadata_refs=["YGRM-0001"],
        diagnostic_scope={"domain": "oracle_shadow", "observation_window": "rolling-30", "reservoir_family": "STATE_SPACE_RESERVOIR", "intended_lane": "SHADOW"},
        reservoir_declarations=default_reservoir_declarations(),
        computation_status="METADATA_ONLY",
        provenance={
            "source": "reservoir-shadow-observation",
            "evidence_refs": ["docs/audits/REPO_AUDIT_COUNTERFACTUAL_GEOMETRY_ENGINE_v0_1.md"],
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


def test_valid_deterministic_hash() -> None:
    assert _base()["canonical_hash"] == _base()["canonical_hash"]


def test_serialization_stable() -> None:
    p = _base()
    assert serialize_reservoir_geometry_diagnostic(p) == serialize_reservoir_geometry_diagnostic(p)


def test_default_declarations_non_empty() -> None:
    assert default_reservoir_declarations()
    assert default_reservoir_declarations() == default_reservoir_declarations()


def test_duplicate_reservoir_id_fails() -> None:
    with pytest.raises(ValueError, match="duplicate reservoir_id"):
        build_reservoir_geometry_diagnostic(
            diagnostic_id="x",
            source_attachment_refs=[],
            source_signal_packet_refs=[],
            source_metric_registry_refs=[],
            source_projection_refs=[],
            source_route_metadata_refs=[],
            diagnostic_scope={"domain": "d", "observation_window": "w", "reservoir_family": "STATE_SPACE_RESERVOIR", "intended_lane": "SHADOW"},
            reservoir_declarations=default_reservoir_declarations() * 2,
            computation_status="DECLARED_ONLY",
            provenance={"source": "x", "evidence_refs": [], "generated_by": "x", "upstream_schema_refs": []},
            created_at_utc="x",
        )


def test_unknown_fields_fail() -> None:
    with pytest.raises(ValueError, match="unknown intended_lane"):
        build_reservoir_geometry_diagnostic(
            diagnostic_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[],
            diagnostic_scope={"domain": "d", "observation_window": "w", "reservoir_family": "STATE_SPACE_RESERVOIR", "intended_lane": "NOPE"},
            reservoir_declarations=default_reservoir_declarations(), computation_status="DECLARED_ONLY",
            provenance={"source": "x", "evidence_refs": [], "generated_by": "x", "upstream_schema_refs": []}, created_at_utc="x",
        )
    with pytest.raises(ValueError, match="unknown reservoir_family"):
        build_reservoir_geometry_diagnostic(
            diagnostic_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[],
            diagnostic_scope={"domain": "d", "observation_window": "w", "reservoir_family": "NOPE", "intended_lane": "SHADOW"},
            reservoir_declarations=default_reservoir_declarations(), computation_status="DECLARED_ONLY",
            provenance={"source": "x", "evidence_refs": [], "generated_by": "x", "upstream_schema_refs": []}, created_at_utc="x",
        )


def test_unknown_declaration_values_fail() -> None:
    d = default_reservoir_declarations()
    d[0]["reservoir_type"] = "NOPE"
    with pytest.raises(ValueError, match="unknown reservoir_type"):
        build_reservoir_geometry_diagnostic(diagnostic_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[], diagnostic_scope={"domain": "d", "observation_window": "w", "reservoir_family": "STATE_SPACE_RESERVOIR", "intended_lane": "SHADOW"}, reservoir_declarations=d, computation_status="DECLARED_ONLY", provenance={"source": "x", "evidence_refs": [], "generated_by": "x", "upstream_schema_refs": []}, created_at_utc="x")
    d = default_reservoir_declarations()
    d[0]["declared_use"] = "NOPE"
    with pytest.raises(ValueError, match="unknown declared_use"):
        build_reservoir_geometry_diagnostic(diagnostic_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], source_projection_refs=[], source_route_metadata_refs=[], diagnostic_scope={"domain": "d", "observation_window": "w", "reservoir_family": "STATE_SPACE_RESERVOIR", "intended_lane": "SHADOW"}, reservoir_declarations=d, computation_status="DECLARED_ONLY", provenance={"source": "x", "evidence_refs": [], "generated_by": "x", "upstream_schema_refs": []}, created_at_utc="x")


def test_policy_and_output_locks() -> None:
    p = _base()
    b = dict(p)
    b["state_space_policy"] = {**p["state_space_policy"], "state_space_simulated": True}
    with pytest.raises(ValueError, match="state_space_policy.state_space_simulated"):
        validate_reservoir_geometry_diagnostic(b)


def test_remaining_checks() -> None:
    p = _base()
    bad = dict(p)
    bad["governance_flags"] = {**p["governance_flags"], "runtime_authority": True}
    with pytest.raises(ValueError, match="runtime_authority"):
        validate_reservoir_geometry_diagnostic(bad)
    bad = dict(p)
    bad["provenance"] = {**p["provenance"], "source": "spectral krylov runtime"}
    with pytest.raises(ValueError, match="forbidden"):
        validate_reservoir_geometry_diagnostic(bad)
    changed = {**p, "canonical_hash": "0" * 64}
    assert compute_reservoir_geometry_diagnostic_hash(changed) == p["canonical_hash"]


def test_hash_schema_idonly() -> None:
    p = _base()
    changed = build_reservoir_geometry_diagnostic(
        diagnostic_id="RGD-0001", source_attachment_refs=["OGSA-0002"], source_signal_packet_refs=["GSP-0001"], source_metric_registry_refs=["MOR-0001"], source_projection_refs=["GPS-0001"], source_route_metadata_refs=["YGRM-0001"], diagnostic_scope={"domain": "oracle_shadow", "observation_window": "rolling-30", "reservoir_family": "STATE_SPACE_RESERVOIR", "intended_lane": "SHADOW"}, reservoir_declarations=default_reservoir_declarations(), computation_status="METADATA_ONLY", provenance=p["provenance"], created_at_utc="2026-05-27T00:00:00Z"
    )
    assert changed["canonical_hash"] != p["canonical_hash"]
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/reservoir_geometry_diagnostic.v1.schema.json").read_text())
    jsonschema.validate(_base(), schema)
    blob = json.dumps(_base())
    assert "core.oracle_geometric_signal_attachment" not in blob

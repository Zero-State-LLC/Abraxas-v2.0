from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.geodesic_distance_implementation_readiness_dossier import (
    LOCKED_FALSE_GOVERNANCE_FLAGS,
    GeodesicDistanceImplementationReadinessDossierValidationError,
    build_geodesic_distance_implementation_readiness_dossier,
    default_authority_locks,
    default_blocked_scopes,
    default_mathematical_requirements,
    default_numerical_constraints,
    default_numerical_stability_requirements,
    default_output_contract,
    serialize_geodesic_distance_implementation_readiness_dossier,
)


def _payload() -> dict:
    return {
        "dossier_id": "geodesic-readiness-dossier-test-001",
        "implementation_scope": {
            "mode": "PLANNING_ONLY",
            "planning_lane": "SHADOW_METRIC_OPERATOR",
            "readiness_status": "GEODESIC_READINESS_DOSSIER_DEFINED",
        },
        "mathematical_requirements": default_mathematical_requirements(),
        "input_shape_requirements": ["Graph as adjacency list with non-negative float64 weights."],
        "determinism_requirements": ["Dijkstra with deterministic tie-breaking is fully deterministic."],
        "numerical_constraints": default_numerical_constraints(),
        "numerical_stability_requirements": default_numerical_stability_requirements(),
        "dependency_inventory": [],
        "implementation_prerequisites": [],
        "implementation_risks": [],
        "validation_requirements": [{"description": "Reference vector validation.", "validation_type": "REFERENCE_VECTOR", "evidence_refs": []}],
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "output_contract": default_output_contract(),
        "governance_flags": {k: False for k in LOCKED_FALSE_GOVERNANCE_FLAGS},
        "provenance": {
            "source": "GEODESIC_READINESS_DOSSIER_TEST",
            "evidence_refs": ["MetricOperatorRank3SelectionPlan.v1:selection-001"],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/geodesic_distance_implementation_readiness_dossier.v1.schema.json"
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_hash_deterministic() -> None:
    a = build_geodesic_distance_implementation_readiness_dossier(_payload())
    b = build_geodesic_distance_implementation_readiness_dossier(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_schema_version_fixed() -> None:
    p = build_geodesic_distance_implementation_readiness_dossier(_payload())
    assert p["schema_version"] == "GeodesicDistanceImplementationReadinessDossier.v1"


def test_dossier_type_fixed() -> None:
    p = build_geodesic_distance_implementation_readiness_dossier(_payload())
    assert p["dossier_type"] == "GEODESIC_DISTANCE_IMPLEMENTATION_READINESS_DOSSIER"


def test_selected_operator_fixed() -> None:
    p = build_geodesic_distance_implementation_readiness_dossier(_payload())
    assert p["selected_operator"] == "GEODESIC"


def test_dossier_status_fixed() -> None:
    p = build_geodesic_distance_implementation_readiness_dossier(_payload())
    assert p["dossier_status"] == "GEODESIC_READINESS_DOSSIER_DEFINED"


def test_intended_lane_fixed() -> None:
    p = build_geodesic_distance_implementation_readiness_dossier(_payload())
    assert p["intended_lane"] == "SHADOW"


def test_authority_locks_advisory_only_true() -> None:
    locks = default_authority_locks()
    assert locks["advisory_only"] is True
    assert locks["shadow_lane_only"] is True
    assert locks["readiness_dossier_only"] is True


def test_authority_locks_computation_false() -> None:
    locks = default_authority_locks()
    assert locks["geodesic_computation_authorized"] is False
    assert locks["emits_metric_values"] is False
    assert locks["forecast_influence"] is False
    assert locks["p43_surface_lanes_authorized"] is False
    assert locks["execution_authority"] is False


def test_required_blocked_scopes_present() -> None:
    scopes = set(default_blocked_scopes())
    assert "geodesic_computation" in scopes
    assert "emits_metric_values" in scopes
    assert "forecast_influence" in scopes
    assert "p43_surface_lanes" in scopes
    assert "runtime_mutation" in scopes


def test_mathematical_requirements_non_empty() -> None:
    reqs = default_mathematical_requirements()
    assert len(reqs) >= 1
    assert all(isinstance(r, str) and len(r) > 0 for r in reqs)


def test_numerical_constraints_non_empty() -> None:
    c = default_numerical_constraints()
    assert len(c) >= 1


def test_output_contract_all_false() -> None:
    c = default_output_contract()
    assert all(v is False for v in c.values())


def test_all_governance_flags_false() -> None:
    p = build_geodesic_distance_implementation_readiness_dossier(_payload())
    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        assert p["governance_flags"][flag] is False


def test_canonical_hash_64_hex() -> None:
    p = build_geodesic_distance_implementation_readiness_dossier(_payload())
    h = p["canonical_hash"]
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_blocked_scopes_sorted() -> None:
    p = build_geodesic_distance_implementation_readiness_dossier(_payload())
    assert p["blocked_scopes"] == sorted(p["blocked_scopes"])


def test_serialize_is_valid_json() -> None:
    p = build_geodesic_distance_implementation_readiness_dossier(_payload())
    raw = serialize_geodesic_distance_implementation_readiness_dossier(p)
    parsed = json.loads(raw)
    assert parsed["schema_version"] == "GeodesicDistanceImplementationReadinessDossier.v1"


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (
            lambda p: p["governance_flags"].__setitem__("execution_authority", True),
            "governance_flag_must_be_false:execution_authority",
        ),
        (
            lambda p: p.__setitem__(
                "blocked_scopes",
                [s for s in default_blocked_scopes() if s != "geodesic_computation"],
            ),
            "missing_required_blocked_scopes",
        ),
        (
            lambda p: p["provenance"].__setitem__(
                "generated_by", "bad-geodesic-distance-ref"
            ),
            "forbidden_provenance_reference_detected",
        ),
    ],
)
def test_validation_rejects_invalid(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(
        GeodesicDistanceImplementationReadinessDossierValidationError, match=err
    ):
        build_geodesic_distance_implementation_readiness_dossier(payload)


def test_committed_artifact_parseable() -> None:
    path = Path(
        "out/metric_operator/"
        "geodesic_distance_implementation_readiness_dossier_001.latest.json"
    )
    if not path.exists():
        pytest.skip("artifact not yet emitted")
    data = json.loads(path.read_text())
    assert data["schema_version"] == "GeodesicDistanceImplementationReadinessDossier.v1"
    assert data["selected_operator"] == "GEODESIC"
    assert len(data["canonical_hash"]) == 64

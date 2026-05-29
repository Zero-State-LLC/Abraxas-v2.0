from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.wasserstein_distance_implementation_readiness_dossier import (
    DOSSIER_STATUS,
    INTENDED_LANE,
    OPERATOR_ID,
    READINESS_SCOPE,
    REQUIRED_BLOCKED_SCOPES,
    build_wasserstein_distance_implementation_readiness_dossier,
    compute_wasserstein_distance_implementation_readiness_dossier_hash,
    default_authority_locks,
    default_governance_flags,
    default_output_contract,
    serialize_wasserstein_distance_implementation_readiness_dossier,
)

_VALID_HASH_A = "a" * 64
_VALID_HASH_B = "b" * 64
_VALID_HASH_C = "c" * 64
_VALID_HASH_D = "d" * 64


def _payload() -> dict:
    return {
        "dossier_id": "wasserstein-readiness-dossier-test-001",
        "source_selection_plan_hash": _VALID_HASH_A,
        "source_metric_preflight_hash": _VALID_HASH_B,
        "source_metric_registry_hash": _VALID_HASH_C,
        "source_baseline_vector_pack_hash": _VALID_HASH_D,
        "implementation_scope": {
            "mode": "PLANNING_ONLY",
            "planning_lane": "SHADOW_METRIC_OPERATOR",
            "readiness_status": "WASSERSTEIN_READINESS_DOSSIER_DEFINED",
        },
        "mathematical_requirements": [
            "1D Wasserstein is deterministic via sort-based algorithm.",
        ],
        "input_shape_requirements": [
            "Two discrete probability distributions over a shared metric space.",
        ],
        "determinism_requirements": [
            "All computations must be deterministic given identical inputs.",
        ],
        "numerical_stability_requirements": [
            "Float64 precision required throughout.",
        ],
        "validation_requirements": [
            {
                "strategy_id": "val-001",
                "validation_type": "DETERMINISTIC_REPLAY",
                "description": "Replay dossier with stable hash equivalence.",
                "evidence_refs": [
                    "MetricOperatorBaselineTestVectorPack.v1:pack-001",
                ],
            },
        ],
        "implementation_prerequisites": [
            {
                "prerequisite_id": "prereq-001",
                "status": "REQUIRED",
                "description": "Selection plan must be present and sealed.",
                "evidence_refs": [
                    "MetricOperatorImplementationSelectionPlan.v1:plan-001",
                ],
            },
        ],
        "dependency_inventory": [
            {
                "dependency_id": "dep-001",
                "dependency_type": "TEST_VECTOR",
                "description": "Wasserstein baseline test vector.",
                "required": True,
                "evidence_refs": [
                    "MetricOperatorBaselineTestVectorPack.v1:pack-001",
                ],
            },
        ],
        "numerical_constraints": [
            "No floating-point kernel execution in this planning lane.",
        ],
        "implementation_risks": [
            {
                "risk_id": "risk-001",
                "risk_level": "MEDIUM",
                "description": "Dimensionality of geometric surface inputs is unspecified.",
                "mitigation": "Defer to test vector schema plan.",
                "evidence_refs": [],
            },
        ],
        "blocked_scopes": sorted(REQUIRED_BLOCKED_SCOPES),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_TEST_VECTOR_SCHEMA_PLAN",
        "output_contract": default_output_contract(),
        "governance_flags": default_governance_flags(),
        "provenance": {
            "source": "WASSERSTEIN_READINESS_DOSSIER_v0.1",
            "evidence_refs": [
                "MetricOperatorImplementationSelectionPlan.v1:plan-001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/wasserstein_distance_implementation_readiness_dossier.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


def test_deterministic_hash_and_serialization() -> None:
    a = build_wasserstein_distance_implementation_readiness_dossier(_payload())
    b = build_wasserstein_distance_implementation_readiness_dossier(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_wasserstein_distance_implementation_readiness_dossier(
        a
    ) == serialize_wasserstein_distance_implementation_readiness_dossier(b)


def test_constants_on_built_artifact() -> None:
    packet = build_wasserstein_distance_implementation_readiness_dossier(_payload())
    assert packet["selected_operator"] == OPERATOR_ID
    assert packet["dossier_status"] == DOSSIER_STATUS
    assert packet["intended_lane"] == INTENDED_LANE
    assert packet["readiness_scope"] == READINESS_SCOPE


def test_all_governance_flags_false() -> None:
    packet = build_wasserstein_distance_implementation_readiness_dossier(_payload())
    assert all(v is False for v in packet["governance_flags"].values())


def test_authority_locks_correct() -> None:
    packet = build_wasserstein_distance_implementation_readiness_dossier(_payload())
    locks = packet["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["shadow_lane_only"] is True
    assert locks["readiness_dossier_only"] is True
    assert locks["wasserstein_computation_authorized"] is False
    assert locks["emits_metric_values"] is False
    assert locks["forecast_influence"] is False
    assert locks["p43_surface_lanes_authorized"] is False
    assert locks["production_activation"] is False
    assert locks["canon_promotion"] is False
    assert locks["runtime_mutation"] is False
    assert locks["execution_authority"] is False
    assert locks["inference_authority"] is False


def test_output_contract_all_false() -> None:
    packet = build_wasserstein_distance_implementation_readiness_dossier(_payload())
    assert all(v is False for v in packet["output_contract"].values())


def test_all_required_blocked_scopes_present() -> None:
    packet = build_wasserstein_distance_implementation_readiness_dossier(_payload())
    blocked = set(packet["blocked_scopes"])
    assert REQUIRED_BLOCKED_SCOPES.issubset(blocked)


def test_source_hashes_present() -> None:
    packet = build_wasserstein_distance_implementation_readiness_dossier(_payload())
    assert packet["source_selection_plan_hash"] == _VALID_HASH_A
    assert packet["source_metric_preflight_hash"] == _VALID_HASH_B
    assert packet["source_metric_registry_hash"] == _VALID_HASH_C
    assert packet["source_baseline_vector_pack_hash"] == _VALID_HASH_D


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (
            lambda p: p["implementation_scope"].__setitem__("mode", "BAD"),
            "unknown_implementation_scope_mode",
        ),
        (
            lambda p: p["implementation_prerequisites"][0].__setitem__("status", "BAD"),
            "unknown_prerequisite_status",
        ),
        (
            lambda p: p["dependency_inventory"][0].__setitem__("dependency_type", "BAD"),
            "unknown_dependency_type",
        ),
        (
            lambda p: p["validation_requirements"][0].__setitem__("validation_type", "BAD"),
            "unknown_validation_type",
        ),
        (
            lambda p: p["implementation_risks"][0].__setitem__("risk_level", "BAD"),
            "unknown_risk_level",
        ),
    ],
)
def test_enum_failures(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(ValueError, match=err):
        build_wasserstein_distance_implementation_readiness_dossier(payload)


def test_invalid_source_hash_rejected() -> None:
    payload = _payload()
    payload["source_selection_plan_hash"] = "not-a-hash"
    with pytest.raises(ValueError, match="invalid_sha256_hash"):
        build_wasserstein_distance_implementation_readiness_dossier(payload)



def test_missing_blocked_scope_rejected() -> None:
    payload = _payload()
    payload["blocked_scopes"] = ["emits_metric_values"]
    with pytest.raises(ValueError, match="missing_required_blocked_scopes"):
        build_wasserstein_distance_implementation_readiness_dossier(payload)


def test_duplicate_id_failures() -> None:
    payload = _payload()
    payload["implementation_prerequisites"].append(
        dict(payload["implementation_prerequisites"][0])
    )
    with pytest.raises(ValueError, match="duplicate_prerequisite_id"):
        build_wasserstein_distance_implementation_readiness_dossier(payload)

    payload = _payload()
    payload["dependency_inventory"].append(dict(payload["dependency_inventory"][0]))
    with pytest.raises(ValueError, match="duplicate_dependency_id"):
        build_wasserstein_distance_implementation_readiness_dossier(payload)

    payload = _payload()
    payload["validation_requirements"].append(
        dict(payload["validation_requirements"][0])
    )
    with pytest.raises(ValueError, match="duplicate_validation_strategy_id"):
        build_wasserstein_distance_implementation_readiness_dossier(payload)

    payload = _payload()
    payload["implementation_risks"].append(dict(payload["implementation_risks"][0]))
    with pytest.raises(ValueError, match="duplicate_risk_id"):
        build_wasserstein_distance_implementation_readiness_dossier(payload)


def test_authority_lock_true_flags_enforced() -> None:
    for key in ("advisory_only", "shadow_lane_only", "readiness_dossier_only"):
        payload = _payload()
        payload["authority_locks"][key] = False
        with pytest.raises(ValueError, match="authority_lock_must_be_true"):
            build_wasserstein_distance_implementation_readiness_dossier(payload)


def test_authority_lock_false_flags_enforced() -> None:
    for key in (
        "wasserstein_computation_authorized",
        "emits_metric_values",
        "execution_authority",
    ):
        payload = _payload()
        payload["authority_locks"][key] = True
        with pytest.raises(ValueError, match="authority_lock_must_be_false"):
            build_wasserstein_distance_implementation_readiness_dossier(payload)


def test_governance_flag_enforcement() -> None:
    payload = _payload()
    payload["governance_flags"]["execution_authority"] = True
    with pytest.raises(ValueError, match="governance_flag_must_be_false"):
        build_wasserstein_distance_implementation_readiness_dossier(payload)


def test_output_contract_lock() -> None:
    payload = _payload()
    payload["output_contract"] = {
        "implementation_completed": True,
        "runtime_enabled": False,
        "scheduler_enabled": False,
        "renderer_enabled": False,
        "oracle_enabled": False,
        "forecast_enabled": False,
        "production_ready": False,
    }
    with pytest.raises(ValueError, match="invalid_output_contract"):
        build_wasserstein_distance_implementation_readiness_dossier(payload)


def test_provenance_forbidden_token_rejection() -> None:
    payload = _payload()
    payload["provenance"]["source"] = "runtime activation and autonomous execution"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_distance_implementation_readiness_dossier(payload)


def test_hash_preimage_excludes_hash_field() -> None:
    packet = build_wasserstein_distance_implementation_readiness_dossier(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_wasserstein_distance_implementation_readiness_dossier_hash(
        packet
    ) == compute_wasserstein_distance_implementation_readiness_dossier_hash(altered)


def test_meaningful_change_alters_hash() -> None:
    packet_a = build_wasserstein_distance_implementation_readiness_dossier(_payload())
    payload_b = _payload()
    payload_b["implementation_scope"]["mode"] = "CPU_REFERENCE_ONLY"
    packet_b = build_wasserstein_distance_implementation_readiness_dossier(payload_b)
    assert packet_a["canonical_hash"] != packet_b["canonical_hash"]


def test_schema_validation() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path(
            "contracts/canon/wasserstein_distance_implementation_readiness_dossier.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    packet = build_wasserstein_distance_implementation_readiness_dossier(_payload())
    jsonschema.validate(packet, schema)


def test_recommended_next_step_present() -> None:
    packet = build_wasserstein_distance_implementation_readiness_dossier(_payload())
    assert packet["recommended_next_step"] == "WASSERSTEIN_TEST_VECTOR_SCHEMA_PLAN"


def test_blocked_scopes_sorted() -> None:
    packet = build_wasserstein_distance_implementation_readiness_dossier(_payload())
    assert packet["blocked_scopes"] == sorted(packet["blocked_scopes"])

from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicExpectedValuesGate.v1"
GATE_ID = "geodesic_expected_values_gate_001"
OPERATOR_ID = "GEODESIC"
GATE_STATUS = "GEODESIC_EXPECTED_VALUES_GATE_READY"
GATE_STAGE = "EXPECTED_VALUES_GATE_ONLY"

SOURCE_FIXTURE_PLAN_HASH = (
    "de12f32211cb7fa7912a963355893e7922cb52f2b3de75b346b7b37740daee83"
)
SOURCE_FIXTURE_MANIFEST_HASH = (
    "3ed5b27dc5879a41c4f0147e6371fe7a1cdf40f929a282d378ed9740ee76c4e2"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")

VALID_FIXTURE_IDS = (
    "geodesic.valid.valid_001_simple_connected_weighted_graph.v1",
    "geodesic.valid.valid_002_multi_hop_graph.v1",
    "geodesic.valid.valid_003_self_loop.v1",
    "geodesic.valid.valid_004_unweighted_graph.v1",
    "geodesic.valid.valid_005_complete_graph.v1",
)
INVALID_FIXTURE_IDS = (
    "geodesic.invalid.invalid_001_missing_source_node.v1",
    "geodesic.invalid.invalid_002_missing_target_node.v1",
    "geodesic.invalid.invalid_003_missing_edge_list.v1",
    "geodesic.invalid.invalid_004_negative_edge_weight.v1",
)
NC_FIXTURE_IDS = (
    "geodesic.not_computable.nc_001_empty_graph.v1",
    "geodesic.not_computable.nc_002_disconnected_graph.v1",
    "geodesic.not_computable.nc_003_source_not_in_graph.v1",
    "geodesic.not_computable.nc_004_target_not_in_graph.v1",
)

FORBIDDEN = (
    "geodesic-distance",
    "dijkstra-execution",
    "shortest-path-computation",
    "metric-value",
    "metric-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class GeodesicExpectedValuesGateValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise GeodesicExpectedValuesGateValidationError(
            "forbidden_token_detected_in_string_value"
        )


def build_valid_fixture_review() -> dict[str, Any]:
    return {
        "fixtures_reviewed": list(VALID_FIXTURE_IDS),
        "fixture_count": len(VALID_FIXTURE_IDS),
        "current_state": {
            fid: {
                "expected_geodesic_distance_included": False,
                "metric_value_emitted": False,
                "fixture_type": "VALID",
                "intended_lane": "SHADOW",
            }
            for fid in VALID_FIXTURE_IDS
        },
        "review_finding": (
            "All 5 valid fixtures confirmed: canonical_hash present, "
            "expected_geodesic_distance_included=false on all, "
            "metric_value_emitted=false on all, intended_lane=SHADOW on all. "
            "Static expected-distance values may be added."
        ),
        "addition_permitted": True,
        "addition_scope": "static_declared_values_only",
        "computation_blocked": True,
    }


def build_expected_value_authorization_scope() -> dict[str, Any]:
    return {
        "authorized_fixture_ids": list(VALID_FIXTURE_IDS),
        "authorized_fixture_count": len(VALID_FIXTURE_IDS),
        "authorization_type": "STATIC_DECLARED_VALUES_ONLY",
        "expected_value_field": "expected_geodesic_distance",
        "inclusion_flag_field": "expected_geodesic_distance_included",
        "value_type": "float64_non_negative",
        "self_loop_convention": "source_equals_target_yields_zero",
        "computation_blocked": True,
        "runtime_math_blocked": True,
        "metric_emission_blocked": True,
        "fixture_files_not_modified_by_gate": True,
    }


def build_invalid_fixture_exclusion_scope() -> dict[str, Any]:
    return {
        "excluded_fixture_ids": list(INVALID_FIXTURE_IDS),
        "excluded_fixture_count": len(INVALID_FIXTURE_IDS),
        "exclusion_reason": (
            "Invalid fixtures yield INVALID_INPUT_NO_EXPECTED_DISTANCE. "
            "No expected_geodesic_distance may be added to invalid fixtures."
        ),
        "expected_geodesic_distance_blocked": True,
        "metric_value_blocked": True,
    }


def build_not_computable_fixture_exclusion_scope() -> dict[str, Any]:
    return {
        "excluded_fixture_ids": list(NC_FIXTURE_IDS),
        "excluded_fixture_count": len(NC_FIXTURE_IDS),
        "exclusion_reason": (
            "NOT_COMPUTABLE fixtures yield NOT_COMPUTABLE_NO_EXPECTED_DISTANCE. "
            "No expected_geodesic_distance may be added to NOT_COMPUTABLE fixtures."
        ),
        "expected_geodesic_distance_blocked": True,
        "metric_value_blocked": True,
    }


def build_metric_emission_block() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "emits_expected_geodesic_distances_via_gate": False,
        "metric_emission_blocked": True,
        "block_reason": (
            "This gate authorizes static expected-distance field addition only. "
            "No metric values are emitted by this artifact."
        ),
    }


def build_forecast_influence_block() -> dict[str, Any]:
    return {
        "forecast_influence": False,
        "forecast_blocked": True,
        "block_reason": (
            "GEODESIC operator is SHADOW_STUB_ONLY. "
            "No forecast influence permitted at any gate stage."
        ),
    }


def build_p43_surface_lane_block() -> dict[str, Any]:
    return {
        "p43_surface_lanes_authorized": False,
        "p43_blocked": True,
        "block_reason": (
            "P43 surface lanes require full implementation authorization. "
            "Expected-values gate does not open P43 lanes."
        ),
    }


def build_blocked_scopes() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "expected_values_gate_only": True,
        "expected_geodesic_distances_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def build_expected_values_gate(
    gate_id: str = GATE_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
    intended_lane: str = "SHADOW",
) -> dict[str, Any]:
    if intended_lane not in ALLOWED_LANE:
        raise GeodesicExpectedValuesGateValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "gate_id": gate_id,
        "operator_id": OPERATOR_ID,
        "gate_status": GATE_STATUS,
        "gate_stage": GATE_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": intended_lane,
        "source_fixture_plan_hash": SOURCE_FIXTURE_PLAN_HASH,
        "source_fixture_manifest_hash": SOURCE_FIXTURE_MANIFEST_HASH,
        "valid_fixture_review": build_valid_fixture_review(),
        "expected_value_authorization_scope": build_expected_value_authorization_scope(),
        "invalid_fixture_exclusion_scope": build_invalid_fixture_exclusion_scope(),
        "not_computable_fixture_exclusion_scope": build_not_computable_fixture_exclusion_scope(),
        "metric_emission_block": build_metric_emission_block(),
        "forecast_influence_block": build_forecast_influence_block(),
        "p43_surface_lane_block": build_p43_surface_lane_block(),
        "blocked_scopes": build_blocked_scopes(),
        "authority_locks": build_authority_locks(),
        "recommended_next_step": "GEODESIC_EXPECTED_VALUES_ADDITION_RECEIPT",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return _finalize(result)


def validate_expected_values_gate(gate: dict[str, Any]) -> None:
    if gate.get("schema_version") != SCHEMA_VERSION:
        raise GeodesicExpectedValuesGateValidationError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if gate.get("operator_id") != OPERATOR_ID:
        raise GeodesicExpectedValuesGateValidationError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if gate.get("gate_status") != GATE_STATUS:
        raise GeodesicExpectedValuesGateValidationError(
            f"gate_status must be {GATE_STATUS!r}"
        )
    if gate.get("gate_stage") != GATE_STAGE:
        raise GeodesicExpectedValuesGateValidationError(
            f"gate_stage must be {GATE_STAGE!r}"
        )
    if gate.get("intended_lane") not in ALLOWED_LANE:
        raise GeodesicExpectedValuesGateValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )
    if gate.get("source_fixture_plan_hash") != SOURCE_FIXTURE_PLAN_HASH:
        raise GeodesicExpectedValuesGateValidationError(
            "source_fixture_plan_hash mismatch"
        )
    if gate.get("source_fixture_manifest_hash") != SOURCE_FIXTURE_MANIFEST_HASH:
        raise GeodesicExpectedValuesGateValidationError(
            "source_fixture_manifest_hash mismatch"
        )
    locks = gate.get("authority_locks", {})
    if locks.get("advisory_only") is not True:
        raise GeodesicExpectedValuesGateValidationError(
            "authority_locks.advisory_only must be True"
        )
    if locks.get("expected_values_gate_only") is not True:
        raise GeodesicExpectedValuesGateValidationError(
            "authority_locks.expected_values_gate_only must be True"
        )
    if locks.get("expected_geodesic_distances_authorized") is not True:
        raise GeodesicExpectedValuesGateValidationError(
            "authority_locks.expected_geodesic_distances_authorized must be True"
        )
    if locks.get("emits_metric_values") is not False:
        raise GeodesicExpectedValuesGateValidationError(
            "authority_locks.emits_metric_values must be False"
        )
    if locks.get("forecast_influence") is not False:
        raise GeodesicExpectedValuesGateValidationError(
            "authority_locks.forecast_influence must be False"
        )
    if locks.get("p43_surface_lanes_authorized") is not False:
        raise GeodesicExpectedValuesGateValidationError(
            "authority_locks.p43_surface_lanes_authorized must be False"
        )
    if locks.get("production_activation") is not False:
        raise GeodesicExpectedValuesGateValidationError(
            "authority_locks.production_activation must be False"
        )
    if locks.get("execution_authority") is not False:
        raise GeodesicExpectedValuesGateValidationError(
            "authority_locks.execution_authority must be False"
        )
    vfr = gate.get("valid_fixture_review", {})
    if vfr.get("fixture_count") != 5:
        raise GeodesicExpectedValuesGateValidationError(
            "valid_fixture_review.fixture_count must be 5"
        )
    if vfr.get("addition_permitted") is not True:
        raise GeodesicExpectedValuesGateValidationError(
            "valid_fixture_review.addition_permitted must be True"
        )
    if vfr.get("computation_blocked") is not True:
        raise GeodesicExpectedValuesGateValidationError(
            "valid_fixture_review.computation_blocked must be True"
        )
    exc_inv = gate.get("invalid_fixture_exclusion_scope", {})
    if exc_inv.get("excluded_fixture_count") != 4:
        raise GeodesicExpectedValuesGateValidationError(
            "invalid_fixture_exclusion_scope.excluded_fixture_count must be 4"
        )
    exc_nc = gate.get("not_computable_fixture_exclusion_scope", {})
    if exc_nc.get("excluded_fixture_count") != 4:
        raise GeodesicExpectedValuesGateValidationError(
            "not_computable_fixture_exclusion_scope.excluded_fixture_count must be 4"
        )
    h = gate.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise GeodesicExpectedValuesGateValidationError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(gate))
    if recomputed != h:
        raise GeodesicExpectedValuesGateValidationError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )

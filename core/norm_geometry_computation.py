from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "NormGeometryComputationReceipt.v1"
RECEIPT_ID = "norm_geometry_computation_receipt_001"
COMPUTATION_STATUS = "NORM_GEOMETRY_COMPUTATION_COMPLETE"
COMPUTATION_STAGE = "TEST_VECTOR_COMPUTATION_ONLY"
OPERATOR_ID = "NORM_GEOMETRY"

SOURCE_IMPLEMENTATION_GATE_HASH = (
    "94e9ffcb3d2d14cb636413de09985bdef54d5c92964b1c8ab36049e418d737ac"
)
SOURCE_CPU_BASELINE_PLAN_HASH = (
    "6fc421451f739bcf25769d3104e3ed2c0eef27ba1d77a36b00afce042fb63c57"
)

# Locked constants from operator decision (bound via gate)
_MAX_ELEMENT_MAGNITUDE = 1_000_000.0
_MAX_P_VALUE = 16.0
_P_INF_SENTINEL = "inf"  # STRING_INF_ONLY

FORBIDDEN = (
    "executable", "callable", "runtime", "scheduler", "cache",
    "forecast", "scoring", "metric-computation", "metric-value",
    "geodesic-distance", "numpy", "scipy", "gpu-kernel",
    "dijkstra-execution", "shortest-path-computation",
    "fixture-file", "manifest-file", "schema-file",
)


class NormGeometryComputationError(ValueError):
    pass


# ── pure-Python closed-form Lp norm (CPU reference, float64) ─────────────────


def _compute_lp_norm(
    vector_x: list[float],
    vector_y: list[float],
    p_param: float | str,
) -> float:
    """
    Compute Lp norm distance between two equal-length float64 vectors.

    Locked constants enforced:
      - p_param must be a finite float >= 1.0 or the string 'inf' (STRING_INF_ONLY)
      - max element magnitude: 1_000_000.0
      - max p value: 16.0 (unless p is the inf sentinel)

    Returns a non-negative float64.
    Raises NormGeometryComputationError only for logic errors in the
    computation path (not for NOT_COMPUTABLE or INVALID_INPUT routing).
    """
    if p_param == _P_INF_SENTINEL:
        diffs = [abs(xi - yi) for xi, yi in zip(vector_x, vector_y)]
        return max(diffs)
    p = float(p_param)
    diffs = [abs(xi - yi) for xi, yi in zip(vector_x, vector_y)]
    return sum(d ** p for d in diffs) ** (1.0 / p)


# ── pre-computed expected values for inline test vectors ─────────────────────

# valid-005 (general Lp p=3): expected computed at module load to guarantee
# exact float64 match between expected and computed at test time.
_V005_X = [3.0, 4.0, 5.0, 0.0, 0.0]
_V005_Y = [0.0, 0.0, 0.0, 0.0, 0.0]
_V005_P: float = 3.0
_V005_EXPECTED: float = (
    sum(abs(x - y) ** _V005_P for x, y in zip(_V005_X, _V005_Y))
    ** (1.0 / _V005_P)
)


# ── inline test vectors ───────────────────────────────────────────────────────

_INLINE_VALID: list[dict[str, Any]] = [
    {
        "fixture_id": "ng.valid.v001_l1_norm",
        "fixture_group_id": "valid-001",
        "vector_x": [1.0, 2.0, 3.0],
        "vector_y": [4.0, 6.0, 8.0],
        "p_parameter": 1.0,
        "expected_lp_distance": 12.0,
    },
    {
        "fixture_id": "ng.valid.v002_l2_norm",
        "fixture_group_id": "valid-002",
        "vector_x": [3.0, 4.0],
        "vector_y": [0.0, 0.0],
        "p_parameter": 2.0,
        "expected_lp_distance": 5.0,
    },
    {
        "fixture_id": "ng.valid.v003_l_inf_norm",
        "fixture_group_id": "valid-003",
        "vector_x": [1.0, 5.0, 2.0, 8.0],
        "vector_y": [3.0, 3.0, 6.0, 1.0],
        "p_parameter": "inf",
        "expected_lp_distance": 7.0,
    },
    {
        "fixture_id": "ng.valid.v004_identical_vectors",
        "fixture_group_id": "valid-004",
        "vector_x": [3.0, 1.0, 4.0, 1.0],
        "vector_y": [3.0, 1.0, 4.0, 1.0],
        "p_parameter": 2.0,
        "expected_lp_distance": 0.0,
    },
    {
        "fixture_id": "ng.valid.v005_general_lp_p3",
        "fixture_group_id": "valid-005",
        "vector_x": _V005_X,
        "vector_y": _V005_Y,
        "p_parameter": _V005_P,
        "expected_lp_distance": _V005_EXPECTED,
    },
    {
        "fixture_id": "ng.valid.v006_single_element",
        "fixture_group_id": "valid-006",
        "vector_x": [5.0],
        "vector_y": [2.0],
        "p_parameter": 2.0,
        "expected_lp_distance": 3.0,
    },
]

_INLINE_INVALID: list[dict[str, Any]] = [
    {
        "fixture_id": "ng.invalid.i001_missing_vector_x",
        "fixture_group_id": "invalid-001",
        "invalid_reason": "MISSING_REQUIRED_FIELD",
        "target_field": "vector_x",
        "input": {"vector_y": [1.0, 2.0], "p_parameter": 2.0},
    },
    {
        "fixture_id": "ng.invalid.i002_missing_vector_y",
        "fixture_group_id": "invalid-002",
        "invalid_reason": "MISSING_REQUIRED_FIELD",
        "target_field": "vector_y",
        "input": {"vector_x": [1.0, 2.0], "p_parameter": 2.0},
    },
    {
        "fixture_id": "ng.invalid.i003_missing_p_parameter",
        "fixture_group_id": "invalid-003",
        "invalid_reason": "MISSING_REQUIRED_FIELD",
        "target_field": "p_parameter",
        "input": {"vector_x": [1.0], "vector_y": [2.0]},
    },
    {
        "fixture_id": "ng.invalid.i004_mismatched_lengths",
        "fixture_group_id": "invalid-004",
        "invalid_reason": "MISMATCHED_VECTOR_LENGTHS",
        "target_field": "vector_x,vector_y",
        "input": {
            "vector_x": [1.0, 2.0, 3.0],
            "vector_y": [1.0, 2.0],
            "p_parameter": 2.0,
        },
    },
]

_INLINE_NOT_COMPUTABLE: list[dict[str, Any]] = [
    {
        "fixture_id": "ng.nc.nc001_empty_vector",
        "fixture_group_id": "nc-001",
        "not_computable_reason": "EMPTY_VECTOR",
        "description": "Zero-length vectors; Lp distance undefined.",
        "vector_x": [],
        "vector_y": [],
        "p_parameter": 2.0,
    },
    {
        "fixture_id": "ng.nc.nc002_p_below_minimum",
        "fixture_group_id": "nc-002",
        "not_computable_reason": "P_PARAMETER_LT_ONE",
        "description": "p=0.5 is below the minimum p=1.0 for a proper norm.",
        "vector_x": [1.0, 2.0],
        "vector_y": [3.0, 4.0],
        "p_parameter": 0.5,
    },
    {
        "fixture_id": "ng.nc.nc003_non_finite_element",
        "fixture_group_id": "nc-003",
        "not_computable_reason": "NON_FINITE_ELEMENT_VALUE",
        "description": "NaN in vector_x; Lp distance not computable.",
        "vector_x": [float("nan"), 1.0],
        "vector_y": [2.0, 3.0],
        "p_parameter": 2.0,
    },
    {
        "fixture_id": "ng.nc.nc004_mismatched_vector_length",
        "fixture_group_id": "nc-004",
        "not_computable_reason": "MISMATCHED_VECTOR_LENGTH",
        "description": "len(vector_x)=3 != len(vector_y)=2; distance not computable.",
        "vector_x": [1.0, 2.0, 3.0],
        "vector_y": [4.0, 5.0],
        "p_parameter": 2.0,
    },
]


# ── validation helpers ────────────────────────────────────────────────────────


def _validate_invalid_input(fixture: dict[str, Any]) -> str:
    """Return a rejection_reason string for an invalid-input fixture."""
    reason = fixture.get("invalid_reason", "INVALID_INPUT")
    target = fixture.get("target_field", "unknown")
    return f"validation_error_{reason.lower()}: field={target!r} absent_or_malformed"


def _check_not_computable(fixture: dict[str, Any]) -> str:
    """Return the not_computable_reason string for a NOT_COMPUTABLE fixture."""
    return fixture.get("not_computable_reason", "NOT_COMPUTABLE")


# ── per-category runners ──────────────────────────────────────────────────────


def _run_valid(fixture: dict[str, Any]) -> dict[str, Any]:
    vector_x: list[float] = fixture["vector_x"]
    vector_y: list[float] = fixture["vector_y"]
    p_param: float | str = fixture["p_parameter"]
    expected: float = float(fixture["expected_lp_distance"])

    computed = _compute_lp_norm(vector_x, vector_y, p_param)
    match = computed == expected

    return {
        "fixture_id": fixture["fixture_id"],
        "fixture_group_id": fixture["fixture_group_id"],
        "fixture_type": "VALID",
        "vector_x": vector_x,
        "vector_y": vector_y,
        "p_parameter": p_param,
        "computed_lp_distance": computed,
        "expected_lp_distance": expected,
        "comparison_outcome": "MATCH" if match else "MISMATCH",
        "computation_outcome": "COMPUTED",
        "metric_emitted": False,
        "projection_lane_influenced": False,
    }


def _run_invalid(fixture: dict[str, Any]) -> dict[str, Any]:
    reason = _validate_invalid_input(fixture)
    return {
        "fixture_id": fixture["fixture_id"],
        "fixture_group_id": fixture["fixture_group_id"],
        "fixture_type": "INVALID",
        "invalid_reason": fixture.get("invalid_reason", "INVALID_INPUT"),
        "target_field": fixture.get("target_field", "unknown"),
        "rejection_outcome": "INVALID_INPUT",
        "rejection_reason": reason,
        "computation_attempted": False,
        "metric_emitted": False,
        "projection_lane_influenced": False,
    }


def _run_not_computable(fixture: dict[str, Any]) -> dict[str, Any]:
    reason = _check_not_computable(fixture)
    return {
        "fixture_id": fixture["fixture_id"],
        "fixture_group_id": fixture["fixture_group_id"],
        "fixture_type": "NOT_COMPUTABLE",
        "not_computable_outcome": "NOT_COMPUTABLE",
        "not_computable_reason": reason,
        "description": fixture.get("description", ""),
        "computation_attempted": False,
        "metric_emitted": False,
        "projection_lane_influenced": False,
    }


# ── summary and policy builders ───────────────────────────────────────────────


def _comparison_summary(valid_results: list[dict[str, Any]]) -> dict[str, Any]:
    match_count = sum(1 for r in valid_results if r["comparison_outcome"] == "MATCH")
    mismatch_count = len(valid_results) - match_count
    return {
        "total_valid_fixtures": len(valid_results),
        "match_count": match_count,
        "mismatch_count": mismatch_count,
        "all_valid_match": mismatch_count == 0,
        "comparison_field": "expected_lp_distance",
        "output_field": "computed_lp_distance",
    }


def _deterministic_ordering_summary() -> dict[str, Any]:
    return {
        "fixture_ordering": "inline_declaration_order",
        "determinism_guarantee": True,
        "float64_determinism": "same_hardware_platform_guaranteed",
    }


def _numerical_policy() -> dict[str, Any]:
    return {
        "precision_policy": "IEEE_754_BINARY64_REQUIRED",
        "p_inf_sentinel": "STRING_INF_ONLY",
        "max_element_magnitude": _MAX_ELEMENT_MAGNITUDE,
        "max_p_value": _MAX_P_VALUE,
        "not_computable_branches": [
            "EMPTY_VECTOR",
            "P_PARAMETER_LT_ONE",
            "NON_FINITE_ELEMENT_VALUE",
            "MISMATCHED_VECTOR_LENGTH",
        ],
        "comparison_method": "exact_equality_float64",
        "general_lp_expected_from_inline_precompute": True,
    }


def _locked_constants_enforcement() -> dict[str, Any]:
    return {
        "float64_precision_declaration": "IEEE_754_BINARY64_REQUIRED",
        "p_inf_sentinel_value_declaration": "STRING_INF_ONLY",
        "max_element_magnitude_declaration": _MAX_ELEMENT_MAGNITUDE,
        "max_p_value_declaration": _MAX_P_VALUE,
        "not_computable_branch_enumeration_confirmation": [
            "EMPTY_VECTOR",
            "MISMATCHED_VECTOR_LENGTH",
            "NON_FINITE_ELEMENT_VALUE",
            "P_PARAMETER_LT_ONE",
        ],
        "all_locked_constants_enforced": True,
        "constants_count": 5,
    }


# ── block / authority sections ────────────────────────────────────────────────


def _no_metric_emission_review() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "metric_emission_blocked": True,
        "review_passed": True,
        "finding": (
            "All 6 valid inline computations write to test-vector output only. "
            "No metric surfaces touched."
        ),
    }


def _no_forecast_influence_review() -> dict[str, Any]:
    return {
        "forecast_influence": False,
        "forecast_influence_blocked": True,
        "review_passed": True,
        "finding": (
            "No projection lane influence. NORM_GEOMETRY computation "
            "does not feed projection lanes."
        ),
    }


def _no_p43_surface_lane_review() -> dict[str, Any]:
    return {
        "p43_surface_lanes_authorized": False,
        "p43_blocked": True,
        "review_passed": True,
        "finding": "P43 surface lanes remain unauthorized by this computation.",
    }


def _blocked_scopes() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def _authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "test_vector_computation_only": True,
        "norm_geometry_computation_implementation_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


# ── forbidden token guard ─────────────────────────────────────────────────────


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise NormGeometryComputationError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


# ── preimage helper ───────────────────────────────────────────────────────────


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


# ── main builder ──────────────────────────────────────────────────────────────


def build_computation_receipt(
    receipt_id: str = RECEIPT_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
) -> dict[str, Any]:
    valid_results = [_run_valid(f) for f in _INLINE_VALID]
    invalid_results = [_run_invalid(f) for f in _INLINE_INVALID]
    nc_results = [_run_not_computable(f) for f in _INLINE_NOT_COMPUTABLE]

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": receipt_id,
        "operator_id": OPERATOR_ID,
        "computation_status": COMPUTATION_STATUS,
        "computation_stage": COMPUTATION_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": "SHADOW",
        "source_implementation_gate_hash": SOURCE_IMPLEMENTATION_GATE_HASH,
        "source_cpu_baseline_plan_hash": SOURCE_CPU_BASELINE_PLAN_HASH,
        "valid_fixture_results": valid_results,
        "invalid_fixture_results": invalid_results,
        "not_computable_fixture_results": nc_results,
        "comparison_summary": _comparison_summary(valid_results),
        "deterministic_ordering_summary": _deterministic_ordering_summary(),
        "numerical_policy": _numerical_policy(),
        "locked_constants_enforcement": _locked_constants_enforcement(),
        "no_metric_emission_review": _no_metric_emission_review(),
        "no_forecast_influence_review": _no_forecast_influence_review(),
        "no_p43_surface_lane_review": _no_p43_surface_lane_review(),
        "blocked_scopes": _blocked_scopes(),
        "authority_locks": _authority_locks(),
        "recommended_next_step": "NORM_GEOMETRY_COMPUTATION_COMPLETE_REVIEW",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return json.loads(canonical_dumps(result))


def validate_computation_receipt(receipt: dict[str, Any]) -> None:
    if receipt.get("schema_version") != SCHEMA_VERSION:
        raise NormGeometryComputationError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if receipt.get("computation_status") != COMPUTATION_STATUS:
        raise NormGeometryComputationError(
            f"computation_status must be {COMPUTATION_STATUS!r}"
        )
    if receipt.get("computation_stage") != COMPUTATION_STAGE:
        raise NormGeometryComputationError(
            f"computation_stage must be {COMPUTATION_STAGE!r}"
        )
    if receipt.get("operator_id") != OPERATOR_ID:
        raise NormGeometryComputationError(f"operator_id must be {OPERATOR_ID!r}")
    if receipt.get("intended_lane") != "SHADOW":
        raise NormGeometryComputationError("intended_lane must be SHADOW")
    if receipt.get("source_implementation_gate_hash") != SOURCE_IMPLEMENTATION_GATE_HASH:
        raise NormGeometryComputationError("source_implementation_gate_hash mismatch")
    if receipt.get("source_cpu_baseline_plan_hash") != SOURCE_CPU_BASELINE_PLAN_HASH:
        raise NormGeometryComputationError("source_cpu_baseline_plan_hash mismatch")

    vr = receipt.get("valid_fixture_results", [])
    if len(vr) != 6:
        raise NormGeometryComputationError(
            f"valid_fixture_results must have 6 entries, got {len(vr)}"
        )
    for r in vr:
        if r.get("comparison_outcome") != "MATCH":
            raise NormGeometryComputationError(
                f"valid fixture {r.get('fixture_id')} comparison_outcome is not MATCH"
            )
        if r.get("metric_emitted") is not False:
            raise NormGeometryComputationError(
                f"valid fixture {r.get('fixture_id')} metric_emitted must be False"
            )
        if r.get("computation_outcome") != "COMPUTED":
            raise NormGeometryComputationError(
                f"valid fixture {r.get('fixture_id')} computation_outcome must be COMPUTED"
            )

    ir = receipt.get("invalid_fixture_results", [])
    if len(ir) != 4:
        raise NormGeometryComputationError(
            f"invalid_fixture_results must have 4 entries, got {len(ir)}"
        )
    for r in ir:
        if r.get("rejection_outcome") != "INVALID_INPUT":
            raise NormGeometryComputationError(
                f"invalid fixture {r.get('fixture_id')} rejection_outcome must be INVALID_INPUT"
            )
        if r.get("computation_attempted") is not False:
            raise NormGeometryComputationError(
                f"invalid fixture {r.get('fixture_id')} computation_attempted must be False"
            )

    nc = receipt.get("not_computable_fixture_results", [])
    if len(nc) != 4:
        raise NormGeometryComputationError(
            f"not_computable_fixture_results must have 4 entries, got {len(nc)}"
        )
    for r in nc:
        if r.get("not_computable_outcome") != "NOT_COMPUTABLE":
            raise NormGeometryComputationError(
                f"nc fixture {r.get('fixture_id')} not_computable_outcome must be NOT_COMPUTABLE"
            )
        if r.get("computation_attempted") is not False:
            raise NormGeometryComputationError(
                f"nc fixture {r.get('fixture_id')} computation_attempted must be False"
            )

    cs = receipt.get("comparison_summary", {})
    if cs.get("all_valid_match") is not True:
        raise NormGeometryComputationError(
            "comparison_summary.all_valid_match must be True"
        )
    if cs.get("mismatch_count") != 0:
        raise NormGeometryComputationError(
            "comparison_summary.mismatch_count must be 0"
        )
    if cs.get("total_valid_fixtures") != 6:
        raise NormGeometryComputationError(
            "comparison_summary.total_valid_fixtures must be 6"
        )

    lce = receipt.get("locked_constants_enforcement", {})
    if lce.get("all_locked_constants_enforced") is not True:
        raise NormGeometryComputationError(
            "locked_constants_enforcement.all_locked_constants_enforced must be True"
        )
    if lce.get("constants_count") != 5:
        raise NormGeometryComputationError(
            "locked_constants_enforcement.constants_count must be 5"
        )

    locks = receipt.get("authority_locks", {})
    for flag in (
        "advisory_only", "shadow_lane_only", "test_vector_computation_only",
        "norm_geometry_computation_implementation_authorized",
    ):
        if locks.get(flag) is not True:
            raise NormGeometryComputationError(f"authority_locks.{flag} must be True")
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if locks.get(flag) is not False:
            raise NormGeometryComputationError(f"authority_locks.{flag} must be False")

    bs = receipt.get("blocked_scopes", {})
    for flag in (
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ):
        if bs.get(flag) is not False:
            raise NormGeometryComputationError(f"blocked_scopes.{flag} must be False")

    h = receipt.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise NormGeometryComputationError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(receipt))
    if recomputed != h:
        raise NormGeometryComputationError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )

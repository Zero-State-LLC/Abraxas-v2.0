"""Build and validate TRANSPORT test vector fixture documents.

Produces 15 fixture files: 6 VALID, 4 INVALID, 5 NOT_COMPUTABLE.
No LP solver invocation. No metric values emitted. SHADOW lane only.
"""
from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "TransportTestVectorFixture.v1"
OPERATOR_ID = "TRANSPORT"

SOURCE_FIXTURE_PLAN_HASH = (
    "90183e52f9bc2602df88073f4cdfc1f82d61c764741cc539729ff0bb4001799f"
)
SOURCE_IMPLEMENTATION_GATE_HASH = (
    "a5b9691e0ff410b512c725075cc3108141b941b0f22da58441772589a3467eb0"
)

FIXTURE_BASE_PATH = pathlib.Path("input/fixtures/transport")

FIXTURE_IDS_VALID = (
    "tv-valid-001",
    "tv-valid-002",
    "tv-valid-003",
    "tv-valid-004",
    "tv-valid-005",
    "tv-valid-006",
)
FIXTURE_IDS_INVALID = (
    "tv-invalid-001",
    "tv-invalid-002",
    "tv-invalid-003",
    "tv-invalid-004",
)
FIXTURE_IDS_NC = (
    "tv-nc-001",
    "tv-nc-002",
    "tv-nc-003",
    "tv-nc-004",
    "tv-nc-005",
)
ALL_FIXTURE_IDS = FIXTURE_IDS_VALID + FIXTURE_IDS_INVALID + FIXTURE_IDS_NC

CREATED_AT_UTC = "2026-05-30T00:00:00Z"

FORBIDDEN = (
    "executable", "callable", "runtime", "scheduler", "cache",
    "forecast", "scoring", "metric-computation", "metric-value",
    "geodesic-distance", "numpy", "scipy", "gpu-kernel",
    "dijkstra-execution", "shortest-path-computation",
    "fixture-file", "manifest-file", "schema-file",
)


class TransportFixtureCorpusError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise TransportFixtureCorpusError(
            f"forbidden_token_detected_in_string_value: {v!r}"
        )


def _finalize(raw: dict[str, Any]) -> dict[str, Any]:
    pre = {k: v for k, v in raw.items() if k != "canonical_hash"}
    h = canonical_hash(canonical_dumps(pre))
    return json.loads(canonical_dumps({**pre, "canonical_hash": h}))


def _common(
    fixture_id: str,
    fixture_name: str,
    fixture_type: str,
    fixture_group: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "fixture_id": fixture_id,
        "fixture_name": fixture_name,
        "fixture_type": fixture_type,
        "fixture_group": fixture_group,
        "fixture_creation_authorized": True,
        "intended_lane": "SHADOW",
        "metric_value_emitted": False,
        "source_fixture_plan_hash": SOURCE_FIXTURE_PLAN_HASH,
        "source_implementation_gate_hash": SOURCE_IMPLEMENTATION_GATE_HASH,
        "created_at_utc": CREATED_AT_UTC,
    }


def _build_tv_valid_001() -> dict[str, Any]:
    raw = _common(
        "tv-valid-001",
        "balanced_2x2_diagonal_cost_zero",
        "VALID",
        "BALANCED_2X2_DIAGONAL_COST_ZERO",
    )
    raw["input"] = {
        "supply": [1.0, 1.0],
        "demand": [1.0, 1.0],
        "cost_matrix": [[0.0, 1.0], [1.0, 0.0]],
    }
    raw["expected_transport_distance"] = 0.0
    raw["expected_transport_distance_included"] = True
    raw["expected_value_derivation"] = "closed_form_trivial"
    raw["computation_not_required_for_expected_value"] = True
    return raw


def _build_tv_valid_002() -> dict[str, Any]:
    raw = _common(
        "tv-valid-002",
        "balanced_2x2_off_diagonal_cost_two",
        "VALID",
        "BALANCED_2X2_OFF_DIAGONAL_COST_TWO",
    )
    raw["input"] = {
        "supply": [1.0, 1.0],
        "demand": [1.0, 1.0],
        "cost_matrix": [[1.0, 2.0], [2.0, 1.0]],
    }
    raw["expected_transport_distance"] = 2.0
    raw["expected_transport_distance_included"] = True
    raw["expected_value_derivation"] = "closed_form_trivial"
    raw["computation_not_required_for_expected_value"] = True
    return raw


def _build_tv_valid_003() -> dict[str, Any]:
    raw = _common(
        "tv-valid-003",
        "single_source_1x4_closed_form",
        "VALID",
        "SINGLE_SOURCE_1X4_CLOSED_FORM",
    )
    raw["input"] = {
        "supply": [1.0],
        "demand": [0.25, 0.25, 0.25, 0.25],
        "cost_matrix": [[1.0, 2.0, 3.0, 4.0]],
    }
    raw["expected_transport_distance"] = 2.5
    raw["expected_transport_distance_included"] = True
    raw["expected_value_derivation"] = "closed_form_trivial"
    raw["computation_not_required_for_expected_value"] = True
    return raw


def _build_tv_valid_004() -> dict[str, Any]:
    raw = _common(
        "tv-valid-004",
        "single_target_4x1_closed_form",
        "VALID",
        "SINGLE_TARGET_4X1_CLOSED_FORM",
    )
    raw["input"] = {
        "supply": [0.25, 0.25, 0.25, 0.25],
        "demand": [1.0],
        "cost_matrix": [[1.0], [2.0], [3.0], [4.0]],
    }
    raw["expected_transport_distance"] = 2.5
    raw["expected_transport_distance_included"] = True
    raw["expected_value_derivation"] = "closed_form_trivial"
    raw["computation_not_required_for_expected_value"] = True
    return raw


def _build_tv_valid_005() -> dict[str, Any]:
    raw = _common(
        "tv-valid-005",
        "degenerate_1x1_balanced",
        "VALID",
        "DEGENERATE_1X1_BALANCED",
    )
    raw["input"] = {
        "supply": [1.0],
        "demand": [1.0],
        "cost_matrix": [[3.0]],
    }
    raw["expected_transport_distance"] = 3.0
    raw["expected_transport_distance_included"] = True
    raw["expected_value_derivation"] = "closed_form_trivial"
    raw["computation_not_required_for_expected_value"] = True
    return raw


def _build_tv_valid_006() -> dict[str, Any]:
    raw = _common(
        "tv-valid-006",
        "balanced_3x3_metric_cost_uniform",
        "VALID",
        "BALANCED_3X3_METRIC_COST_UNIFORM",
    )
    raw["input"] = {
        "supply": [1.0, 1.0, 1.0],
        "demand": [1.0, 1.0, 1.0],
        "cost_matrix": [
            [0.0, 1.0, 2.0],
            [1.0, 0.0, 1.0],
            [2.0, 1.0, 0.0],
        ],
    }
    raw["expected_transport_distance"] = 0.0
    raw["expected_transport_distance_included"] = True
    raw["expected_value_derivation"] = "closed_form_trivial"
    raw["computation_not_required_for_expected_value"] = True
    return raw


def _build_tv_invalid_001() -> dict[str, Any]:
    raw = _common(
        "tv-invalid-001",
        "missing_supply_vector",
        "INVALID",
        "MISSING_REQUIRED_FIELD",
    )
    raw["input"] = {
        "demand": [1.0],
        "cost_matrix": [[1.0]],
    }
    raw["expected_transport_distance_included"] = False
    raw["rejection_reason"] = (
        "INVALID_INPUT: supply field absent from input; "
        "required-field contract violated"
    )
    return raw


def _build_tv_invalid_002() -> dict[str, Any]:
    raw = _common(
        "tv-invalid-002",
        "missing_demand_vector",
        "INVALID",
        "MISSING_REQUIRED_FIELD",
    )
    raw["input"] = {
        "supply": [1.0],
        "cost_matrix": [[1.0]],
    }
    raw["expected_transport_distance_included"] = False
    raw["rejection_reason"] = (
        "INVALID_INPUT: demand field absent from input; "
        "required-field contract violated"
    )
    return raw


def _build_tv_invalid_003() -> dict[str, Any]:
    raw = _common(
        "tv-invalid-003",
        "missing_cost_matrix",
        "INVALID",
        "MISSING_REQUIRED_FIELD",
    )
    raw["input"] = {
        "supply": [1.0],
        "demand": [1.0],
    }
    raw["expected_transport_distance_included"] = False
    raw["rejection_reason"] = (
        "INVALID_INPUT: cost_matrix field absent from input; "
        "required-field contract violated"
    )
    return raw


def _build_tv_invalid_004() -> dict[str, Any]:
    raw = _common(
        "tv-invalid-004",
        "cost_matrix_shape_mismatch",
        "INVALID",
        "COST_MATRIX_SHAPE_MISMATCH",
    )
    raw["input"] = {
        "supply": [1.0, 1.0],
        "demand": [1.0, 1.0],
        "cost_matrix": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
    }
    raw["expected_transport_distance_included"] = False
    raw["rejection_reason"] = (
        "INVALID_INPUT: cost_matrix shape 2x3 does not match "
        "len(supply)=2 x len(demand)=2; shape contract violated"
    )
    return raw


def _build_tv_nc_001() -> dict[str, Any]:
    raw = _common(
        "tv-nc-001",
        "unbalanced_supply_demand",
        "NOT_COMPUTABLE",
        "UNBALANCED_SUPPLY_DEMAND",
    )
    raw["not_computable_reason"] = "UNBALANCED_SUPPLY_DEMAND"
    raw["input"] = {
        "supply": [1.0, 2.0],
        "demand": [1.0, 1.0],
        "cost_matrix": [[1.0, 1.0], [1.0, 1.0]],
    }
    raw["expected_transport_distance_included"] = False
    raw["rejection_reason"] = (
        "NOT_COMPUTABLE: unbalanced_supply_demand "
        "sum_supply=3.0 sum_demand=2.0; problem is infeasible"
    )
    return raw


def _build_tv_nc_002() -> dict[str, Any]:
    raw = _common(
        "tv-nc-002",
        "negative_supply_value",
        "NOT_COMPUTABLE",
        "NEGATIVE_SUPPLY_VALUE",
    )
    raw["not_computable_reason"] = "NEGATIVE_SUPPLY_VALUE"
    raw["input"] = {
        "supply": [2.0, -1.0],
        "demand": [1.0],
        "cost_matrix": [[1.0], [1.0]],
    }
    raw["expected_transport_distance_included"] = False
    raw["rejection_reason"] = (
        "NOT_COMPUTABLE: negative_supply_value "
        "supply[1]=-1.0 is negative; physically invalid"
    )
    return raw


def _build_tv_nc_003() -> dict[str, Any]:
    raw = _common(
        "tv-nc-003",
        "negative_cost_value",
        "NOT_COMPUTABLE",
        "NEGATIVE_COST_VALUE",
    )
    raw["not_computable_reason"] = "NEGATIVE_COST_VALUE"
    raw["input"] = {
        "supply": [1.0],
        "demand": [1.0],
        "cost_matrix": [[-1.0]],
    }
    raw["expected_transport_distance_included"] = False
    raw["rejection_reason"] = (
        "NOT_COMPUTABLE: negative_cost_value "
        "cost_matrix[0][0]=-1.0 violates cost bound"
    )
    return raw


def _build_tv_nc_004() -> dict[str, Any]:
    raw = _common(
        "tv-nc-004",
        "empty_supply_vector",
        "NOT_COMPUTABLE",
        "EMPTY_SUPPLY_VECTOR",
    )
    raw["not_computable_reason"] = "EMPTY_SUPPLY_VECTOR"
    raw["input"] = {
        "supply": [],
        "demand": [1.0],
        "cost_matrix": [],
    }
    raw["expected_transport_distance_included"] = False
    raw["rejection_reason"] = (
        "NOT_COMPUTABLE: empty_supply_vector "
        "len(supply)=0; no sources present"
    )
    return raw


def _build_tv_nc_005() -> dict[str, Any]:
    raw = _common(
        "tv-nc-005",
        "non_finite_supply_value",
        "NOT_COMPUTABLE",
        "NON_FINITE_SUPPLY_VALUE",
    )
    raw["not_computable_reason"] = "NON_FINITE_SUPPLY_VALUE"
    raw["non_finite_marker"] = (
        "null_in_supply_represents_non_finite_value_not_expressible_in_json"
    )
    raw["input"] = {
        "supply": [1.0, None],
        "demand": [1.0, 1.0],
        "cost_matrix": [[1.0, 1.0], [1.0, 1.0]],
    }
    raw["expected_transport_distance_included"] = False
    raw["rejection_reason"] = (
        "NOT_COMPUTABLE: non_finite_supply_value "
        "supply[1]=null (non-finite marker); guard branch must intercept"
    )
    return raw


_BUILDERS = {
    "tv-valid-001": _build_tv_valid_001,
    "tv-valid-002": _build_tv_valid_002,
    "tv-valid-003": _build_tv_valid_003,
    "tv-valid-004": _build_tv_valid_004,
    "tv-valid-005": _build_tv_valid_005,
    "tv-valid-006": _build_tv_valid_006,
    "tv-invalid-001": _build_tv_invalid_001,
    "tv-invalid-002": _build_tv_invalid_002,
    "tv-invalid-003": _build_tv_invalid_003,
    "tv-invalid-004": _build_tv_invalid_004,
    "tv-nc-001": _build_tv_nc_001,
    "tv-nc-002": _build_tv_nc_002,
    "tv-nc-003": _build_tv_nc_003,
    "tv-nc-004": _build_tv_nc_004,
    "tv-nc-005": _build_tv_nc_005,
}


def build_single_fixture(fixture_id: str) -> dict[str, Any]:
    if fixture_id not in _BUILDERS:
        raise TransportFixtureCorpusError(f"unknown fixture_id: {fixture_id!r}")
    raw = _BUILDERS[fixture_id]()
    _check_no_forbidden(raw)
    return _finalize(raw)


def build_all_fixtures() -> list[dict[str, Any]]:
    return [build_single_fixture(fid) for fid in ALL_FIXTURE_IDS]


def validate_fixture_document(doc: dict[str, Any]) -> None:
    if doc.get("schema_version") != SCHEMA_VERSION:
        raise TransportFixtureCorpusError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    fixture_id = doc.get("fixture_id", "")
    if fixture_id not in ALL_FIXTURE_IDS:
        raise TransportFixtureCorpusError(
            f"fixture_id {fixture_id!r} not in known fixture set"
        )
    if doc.get("fixture_creation_authorized") is not True:
        raise TransportFixtureCorpusError("fixture_creation_authorized must be True")
    if doc.get("intended_lane") != "SHADOW":
        raise TransportFixtureCorpusError("intended_lane must be SHADOW")
    if doc.get("metric_value_emitted") is not False:
        raise TransportFixtureCorpusError("metric_value_emitted must be False")
    if doc.get("source_fixture_plan_hash") != SOURCE_FIXTURE_PLAN_HASH:
        raise TransportFixtureCorpusError("source_fixture_plan_hash mismatch")
    if doc.get("source_implementation_gate_hash") != SOURCE_IMPLEMENTATION_GATE_HASH:
        raise TransportFixtureCorpusError("source_implementation_gate_hash mismatch")
    h = doc.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise TransportFixtureCorpusError(
            f"canonical_hash must be 64-char hex string, got {h!r}"
        )
    pre = {k: v for k, v in doc.items() if k != "canonical_hash"}
    computed = canonical_hash(canonical_dumps(pre))
    if computed != h:
        raise TransportFixtureCorpusError(
            f"canonical_hash mismatch for {fixture_id}: stored={h!r} computed={computed!r}"
        )
    fixture_type = doc.get("fixture_type")
    if fixture_type == "VALID":
        if doc.get("expected_transport_distance_included") is not True:
            raise TransportFixtureCorpusError(
                f"VALID fixture {fixture_id} must have expected_transport_distance_included=True"
            )
        if not isinstance(doc.get("expected_transport_distance"), (int, float)):
            raise TransportFixtureCorpusError(
                f"VALID fixture {fixture_id} must have numeric expected_transport_distance"
            )
    elif fixture_type in ("INVALID", "NOT_COMPUTABLE"):
        if doc.get("expected_transport_distance_included") is not False:
            raise TransportFixtureCorpusError(
                f"{fixture_type} fixture {fixture_id} must have "
                "expected_transport_distance_included=False"
            )
        if "rejection_reason" not in doc:
            raise TransportFixtureCorpusError(
                f"{fixture_type} fixture {fixture_id} must have rejection_reason"
            )
    else:
        raise TransportFixtureCorpusError(
            f"fixture_type must be VALID, INVALID, or NOT_COMPUTABLE, got {fixture_type!r}"
        )
    _check_no_forbidden(doc)


def validate_all_fixtures(fixtures: list[dict[str, Any]]) -> None:
    if len(fixtures) != 15:
        raise TransportFixtureCorpusError(
            f"expected 15 fixtures, got {len(fixtures)}"
        )
    ids_seen = [f.get("fixture_id") for f in fixtures]
    if tuple(ids_seen) != ALL_FIXTURE_IDS:
        raise TransportFixtureCorpusError(
            f"fixture ordering mismatch: got {ids_seen}"
        )
    for doc in fixtures:
        validate_fixture_document(doc)


def load_fixture_from_disk(fixture_id: str) -> dict[str, Any]:
    path = FIXTURE_BASE_PATH / f"{fixture_id}.json"
    if not path.exists():
        raise TransportFixtureCorpusError(
            f"fixture file not found: {path}"
        )
    doc = json.loads(path.read_text())
    validate_fixture_document(doc)
    return doc


def load_all_fixtures_from_disk() -> list[dict[str, Any]]:
    return [load_fixture_from_disk(fid) for fid in ALL_FIXTURE_IDS]

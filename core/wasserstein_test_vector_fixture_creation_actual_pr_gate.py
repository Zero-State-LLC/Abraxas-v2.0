from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinTestVectorFixtureCreationActualPRGate.v1"
GATE_TYPE = "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_ACTUAL_PR_GATE"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_OPERATOR_DECISION_ID = (
    "WASSERSTEIN_FIXTURE_CREATION_OPERATOR_DECISION_2026_05_29_001"
)
SOURCE_OPERATOR_DECISION_HASH = (
    "4428b519fcd94fea288288ecdbfe1630880058f3496ad6691979b798e0334a04"
)
SOURCE_AUTHORIZATION_REVIEW_HASH = (
    "75dcef855cc0d0235ff42d78711a0fd522843600a64049ce9f294072d26fc9fe"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_GATE_STAGE = (
    "FIXTURE_CREATION_ACTUAL_PR_GATE_ONLY",
    "BLOCKED_PENDING_AUTHORIZATION",
)
ALLOWED_FIXTURE_TYPE = ("VALID", "INVALID", "NOT_COMPUTABLE")
ALLOWED_FIXTURE_STATUS = ("AUTHORIZED", "PLANNED", "BLOCKED", "CREATED")
ALLOWED_BATCH_STATUS = ("AUTHORIZED", "PLANNED", "BLOCKED")

EXPECTED_MANIFEST_ENTRY_COUNT = 14
EXPECTED_VALID_COUNT = 5
EXPECTED_INVALID_COUNT = 5
EXPECTED_NOT_COMPUTABLE_COUNT = 4
EXPECTED_BATCH_COUNT = 3

FORBIDDEN = (
    "runtime",
    "scheduler",
    "cache",
    "forecast",
    "scoring",
    "metric-value",
    "wasserstein-distance",
    "expected-wasserstein",
    "earth-mover",
    "ot-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "sinkhorn-kernel",
    "authority-flag",
)

_BASE_PATH = "input/fixtures/wasserstein"


class WassersteinTestVectorFixtureCreationActualPRGateValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


# ---------------------------------------------------------------------------
# Default sub-structures
# ---------------------------------------------------------------------------


def default_authorized_fixture_manifest() -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": "valid-001",
            "fixture_group": "DISTRIBUTION_PAIR_SCHEMA",
            "fixture_type": "VALID",
            "target_path": f"{_BASE_PATH}/valid/valid_001_distribution_pair.json",
            "creation_authorized": True,
            "status": "AUTHORIZED",
        },
        {
            "fixture_id": "valid-002",
            "fixture_group": "WEIGHTED_HISTOGRAM_SCHEMA",
            "fixture_type": "VALID",
            "target_path": f"{_BASE_PATH}/valid/valid_002_weighted_histogram.json",
            "creation_authorized": True,
            "status": "AUTHORIZED",
        },
        {
            "fixture_id": "valid-003",
            "fixture_group": "REFERENCE_VECTOR_SCHEMA",
            "fixture_type": "VALID",
            "target_path": f"{_BASE_PATH}/valid/valid_003_reference_vector.json",
            "creation_authorized": True,
            "status": "AUTHORIZED",
        },
        {
            "fixture_id": "valid-004",
            "fixture_group": "GROUND_METRIC_SCHEMA",
            "fixture_type": "VALID",
            "target_path": f"{_BASE_PATH}/valid/valid_004_ground_metric.json",
            "creation_authorized": True,
            "status": "AUTHORIZED",
        },
        {
            "fixture_id": "valid-005",
            "fixture_group": "DEGENERATE_DISTRIBUTION_SCHEMA",
            "fixture_type": "VALID",
            "target_path": f"{_BASE_PATH}/valid/valid_005_degenerate_distribution.json",
            "creation_authorized": True,
            "status": "AUTHORIZED",
        },
        {
            "fixture_id": "invalid-001",
            "fixture_group": "MISSING_REQUIRED_FIELD",
            "fixture_type": "INVALID",
            "target_path": (
                f"{_BASE_PATH}/invalid/invalid_001_missing_required_field.json"
            ),
            "creation_authorized": True,
            "status": "AUTHORIZED",
        },
        {
            "fixture_id": "invalid-002",
            "fixture_group": "EMPTY_DISTRIBUTION",
            "fixture_type": "INVALID",
            "target_path": f"{_BASE_PATH}/invalid/invalid_002_empty_distribution.json",
            "creation_authorized": True,
            "status": "AUTHORIZED",
        },
        {
            "fixture_id": "invalid-003",
            "fixture_group": "INVALID_WEIGHT_SUM",
            "fixture_type": "INVALID",
            "target_path": f"{_BASE_PATH}/invalid/invalid_003_invalid_weight_sum.json",
            "creation_authorized": True,
            "status": "AUTHORIZED",
        },
        {
            "fixture_id": "invalid-004",
            "fixture_group": "DIMENSION_MISMATCH",
            "fixture_type": "INVALID",
            "target_path": f"{_BASE_PATH}/invalid/invalid_004_dimension_mismatch.json",
            "creation_authorized": True,
            "status": "AUTHORIZED",
        },
        {
            "fixture_id": "invalid-005",
            "fixture_group": "GROUND_METRIC_UNDECLARED",
            "fixture_type": "INVALID",
            "target_path": (
                f"{_BASE_PATH}/invalid/invalid_005_ground_metric_undeclared.json"
            ),
            "creation_authorized": True,
            "status": "AUTHORIZED",
        },
        {
            "fixture_id": "nc-001",
            "fixture_group": "EMPTY_INPUT",
            "fixture_type": "NOT_COMPUTABLE",
            "target_path": f"{_BASE_PATH}/not_computable/nc_001_empty_input.json",
            "creation_authorized": True,
            "status": "AUTHORIZED",
        },
        {
            "fixture_id": "nc-002",
            "fixture_group": "GROUND_METRIC_UNDECLARED",
            "fixture_type": "NOT_COMPUTABLE",
            "target_path": (
                f"{_BASE_PATH}/not_computable/nc_002_ground_metric_undeclared.json"
            ),
            "creation_authorized": True,
            "status": "AUTHORIZED",
        },
        {
            "fixture_id": "nc-003",
            "fixture_group": "NUMERICAL_POLICY_MISSING",
            "fixture_type": "NOT_COMPUTABLE",
            "target_path": (
                f"{_BASE_PATH}/not_computable/nc_003_numerical_policy_missing.json"
            ),
            "creation_authorized": True,
            "status": "AUTHORIZED",
        },
        {
            "fixture_id": "nc-004",
            "fixture_group": "DIMENSIONALITY_UNDECLARED",
            "fixture_type": "NOT_COMPUTABLE",
            "target_path": (
                f"{_BASE_PATH}/not_computable/nc_004_dimensionality_undeclared.json"
            ),
            "creation_authorized": True,
            "status": "AUTHORIZED",
        },
    ]


def default_authorized_batches() -> list[dict[str, Any]]:
    return [
        {
            "batch_id": "batch-01-valid",
            "batch_label": "VALID_FIXTURES",
            "fixture_ids": [
                "valid-001",
                "valid-002",
                "valid-003",
                "valid-004",
                "valid-005",
            ],
            "fixture_count": 5,
            "creation_authorized": True,
            "batch_status": "AUTHORIZED",
        },
        {
            "batch_id": "batch-02-invalid",
            "batch_label": "INVALID_FIXTURES",
            "fixture_ids": [
                "invalid-001",
                "invalid-002",
                "invalid-003",
                "invalid-004",
                "invalid-005",
            ],
            "fixture_count": 5,
            "creation_authorized": True,
            "batch_status": "AUTHORIZED",
        },
        {
            "batch_id": "batch-03-not-computable",
            "batch_label": "NOT_COMPUTABLE_FIXTURES",
            "fixture_ids": ["nc-001", "nc-002", "nc-003", "nc-004"],
            "fixture_count": 4,
            "creation_authorized": True,
            "batch_status": "AUTHORIZED",
        },
    ]


def default_fixture_creation_constraints() -> dict[str, Any]:
    return {
        "expected_wasserstein_distances_included": False,
        "computed_metric_outputs_included": False,
        "fixture_execution_outputs_included": False,
        "shadow_lane_only": True,
        "fixture_file_creation_only": True,
        "authorized_fixture_count": 14,
        "authorized_batch_count": 3,
    }


def default_blocked_scopes() -> dict[str, bool]:
    return {
        "wasserstein_computation": False,
        "emits_metric_values": False,
        "expected_wasserstein_distances_added": False,
        "forecast_influence": False,
        "p43_surface_lanes": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "fixture_creation_actual_pr_gate_only": True,
        "fixture_files_created": False,
        "fixture_file_creation_authorized": True,
        "wasserstein_computation_authorized": False,
        "emits_metric_values": False,
        "expected_wasserstein_distances_added": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


# ---------------------------------------------------------------------------
# Safety scanner
# ---------------------------------------------------------------------------


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_manifest(manifest: list[dict[str, Any]]) -> None:
    if len(manifest) != EXPECTED_MANIFEST_ENTRY_COUNT:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            f"manifest_entry_count_mismatch:expected={EXPECTED_MANIFEST_ENTRY_COUNT}"
        )
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    valid_count = invalid_count = nc_count = 0
    for entry in manifest:
        fid = entry.get("fixture_id", "")
        if fid in seen_ids:
            raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
                f"duplicate_fixture_id:{fid}"
            )
        seen_ids.add(fid)
        tp = entry.get("target_path", "")
        if tp in seen_paths:
            raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
                f"duplicate_target_path:{tp}"
            )
        seen_paths.add(tp)
        ft = entry.get("fixture_type")
        if ft not in ALLOWED_FIXTURE_TYPE:
            raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
                f"unknown_fixture_type:{ft}"
            )
        if entry.get("creation_authorized") is not True:
            raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
                "fixture_creation_must_be_authorized"
            )
        if entry.get("status") not in ALLOWED_FIXTURE_STATUS:
            raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
                f"unknown_fixture_status:{entry.get('status')}"
            )
        if ft == "VALID":
            valid_count += 1
        elif ft == "INVALID":
            invalid_count += 1
        else:
            nc_count += 1
    if valid_count != EXPECTED_VALID_COUNT:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            f"valid_count_mismatch:expected={EXPECTED_VALID_COUNT}"
        )
    if invalid_count != EXPECTED_INVALID_COUNT:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            f"invalid_count_mismatch:expected={EXPECTED_INVALID_COUNT}"
        )
    if nc_count != EXPECTED_NOT_COMPUTABLE_COUNT:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            f"nc_count_mismatch:expected={EXPECTED_NOT_COMPUTABLE_COUNT}"
        )


def _validate_batches(batches: list[dict[str, Any]]) -> None:
    if len(batches) != EXPECTED_BATCH_COUNT:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            f"batch_count_mismatch:expected={EXPECTED_BATCH_COUNT}"
        )
    for batch in batches:
        if batch.get("creation_authorized") is not True:
            raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
                "batch_creation_must_be_authorized"
            )
        if batch.get("batch_status") not in ALLOWED_BATCH_STATUS:
            raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
                f"unknown_batch_status:{batch.get('batch_status')}"
            )


def validate_wasserstein_test_vector_fixture_creation_actual_pr_gate(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "gate_id",
        "gate_type",
        "operator_id",
        "source_operator_decision_id",
        "source_operator_decision_hash",
        "source_authorization_review_hash",
        "intended_lane",
        "gate_stage",
        "authorized_fixture_manifest",
        "authorized_batches",
        "fixture_creation_constraints",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "invalid_schema_version"
        )
    if packet["gate_type"] != GATE_TYPE:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "invalid_gate_type"
        )
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "unknown_operator_id"
        )
    if packet["source_operator_decision_id"] != SOURCE_OPERATOR_DECISION_ID:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "invalid_source_operator_decision_id"
        )
    if packet["source_operator_decision_hash"] != SOURCE_OPERATOR_DECISION_HASH:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "invalid_source_operator_decision_hash"
        )
    if packet["source_authorization_review_hash"] != SOURCE_AUTHORIZATION_REVIEW_HASH:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "invalid_source_authorization_review_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "unknown_intended_lane"
        )
    if packet["gate_stage"] not in ALLOWED_GATE_STAGE:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "unknown_gate_stage"
        )

    _validate_manifest(packet["authorized_fixture_manifest"])
    _validate_batches(packet["authorized_batches"])

    cc = packet["fixture_creation_constraints"]
    if cc.get("expected_wasserstein_distances_included") is not False:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "expected_distances_must_be_excluded"
        )
    if cc.get("computed_metric_outputs_included") is not False:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "computed_metric_outputs_must_be_excluded"
        )
    if cc.get("fixture_execution_outputs_included") is not False:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "fixture_execution_outputs_must_be_excluded"
        )
    if cc.get("shadow_lane_only") is not True:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "shadow_lane_only_must_be_true"
        )
    if cc.get("fixture_file_creation_only") is not True:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "fixture_file_creation_only_must_be_true"
        )

    al = packet["authority_locks"]
    if al.get("fixture_file_creation_authorized") is not True:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "fixture_file_creation_authorized_must_be_true"
        )
    if al.get("fixture_files_created") is not False:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "fixture_files_created_must_be_false"
        )
    if al.get("wasserstein_computation_authorized") is not False:
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "wasserstein_computation_must_be_unauthorized"
        )

    if packet["authorized_fixture_manifest"] != default_authorized_fixture_manifest():
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "invalid_authorized_fixture_manifest"
        )
    if packet["authorized_batches"] != default_authorized_batches():
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "invalid_authorized_batches"
        )
    if packet["fixture_creation_constraints"] != default_fixture_creation_constraints():
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "invalid_fixture_creation_constraints"
        )
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "invalid_blocked_scopes"
        )
    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinTestVectorFixtureCreationActualPRGateValidationError(
            "invalid_authority_locks"
        )

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hashing / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_test_vector_fixture_creation_actual_pr_gate_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_test_vector_fixture_creation_actual_pr_gate(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_test_vector_fixture_creation_actual_pr_gate(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "gate_type": GATE_TYPE,
        "operator_id": OPERATOR_ID,
        "source_operator_decision_id": SOURCE_OPERATOR_DECISION_ID,
        "source_operator_decision_hash": SOURCE_OPERATOR_DECISION_HASH,
        "source_authorization_review_hash": SOURCE_AUTHORIZATION_REVIEW_HASH,
        "authorized_fixture_manifest": payload.get(
            "authorized_fixture_manifest", default_authorized_fixture_manifest()
        ),
        "authorized_batches": payload.get(
            "authorized_batches", default_authorized_batches()
        ),
        "fixture_creation_constraints": payload.get(
            "fixture_creation_constraints", default_fixture_creation_constraints()
        ),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
    }
    base["canonical_hash"] = (
        compute_wasserstein_test_vector_fixture_creation_actual_pr_gate_hash(base)
    )
    validate_wasserstein_test_vector_fixture_creation_actual_pr_gate(base)
    return _finalize(base)

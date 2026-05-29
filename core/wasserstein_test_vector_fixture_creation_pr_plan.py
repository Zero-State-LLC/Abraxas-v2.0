from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinTestVectorFixtureCreationPRPlan.v1"
PR_PLAN_TYPE = "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_PR_PLAN"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_READINESS_REVIEW_HASH = (
    "1d559371c162d43f0914e651993dfcc3d1f76910f8dced3cf5622072bc84b029"
)
SOURCE_FIXTURE_PLAN_HASH = (
    "21513971f031d40214fb0534c8258f41ebfff0c4d3d5bfaf14005af1719fa049"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_PR_PLAN_STAGE = ("FIXTURE_CREATION_PR_PLAN_ONLY", "BLOCKED_PENDING_AUTHORIZATION")
ALLOWED_FIXTURE_TYPE = ("VALID", "INVALID", "NOT_COMPUTABLE")
ALLOWED_FIXTURE_STATUS = ("PLANNED", "BLOCKED", "AUTHORIZED", "CREATED")
ALLOWED_BATCH_STATUS = ("PLANNED", "BLOCKED", "AUTHORIZED")
ALLOWED_VALIDATION_STATUS = ("PLANNED", "BLOCKED", "AUTHORIZED")
ALLOWED_REVIEW_STATUS = ("REQUIRED", "SATISFIED", "WAIVED")

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

EXPECTED_MANIFEST_ENTRY_COUNT = 14
EXPECTED_VALID_COUNT = 5
EXPECTED_INVALID_COUNT = 5
EXPECTED_NOT_COMPUTABLE_COUNT = 4


class WassersteinTestVectorFixtureCreationPRPlanValidationError(ValueError):
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

_BASE_PATH = "input/fixtures/wasserstein"


def default_proposed_fixture_file_manifest() -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": "valid-001",
            "fixture_group": "DISTRIBUTION_PAIR_SCHEMA",
            "fixture_type": "VALID",
            "target_path": f"{_BASE_PATH}/valid/valid_001_distribution_pair.json",
            "creation_authorized": False,
            "status": "PLANNED",
        },
        {
            "fixture_id": "valid-002",
            "fixture_group": "WEIGHTED_HISTOGRAM_SCHEMA",
            "fixture_type": "VALID",
            "target_path": f"{_BASE_PATH}/valid/valid_002_weighted_histogram.json",
            "creation_authorized": False,
            "status": "PLANNED",
        },
        {
            "fixture_id": "valid-003",
            "fixture_group": "REFERENCE_VECTOR_SCHEMA",
            "fixture_type": "VALID",
            "target_path": f"{_BASE_PATH}/valid/valid_003_reference_vector.json",
            "creation_authorized": False,
            "status": "PLANNED",
        },
        {
            "fixture_id": "valid-004",
            "fixture_group": "GROUND_METRIC_SCHEMA",
            "fixture_type": "VALID",
            "target_path": f"{_BASE_PATH}/valid/valid_004_ground_metric.json",
            "creation_authorized": False,
            "status": "PLANNED",
        },
        {
            "fixture_id": "valid-005",
            "fixture_group": "DEGENERATE_DISTRIBUTION_SCHEMA",
            "fixture_type": "VALID",
            "target_path": f"{_BASE_PATH}/valid/valid_005_degenerate_distribution.json",
            "creation_authorized": False,
            "status": "PLANNED",
        },
        {
            "fixture_id": "invalid-001",
            "fixture_group": "MISSING_REQUIRED_FIELD",
            "fixture_type": "INVALID",
            "target_path": f"{_BASE_PATH}/invalid/invalid_001_missing_required_field.json",
            "creation_authorized": False,
            "status": "PLANNED",
        },
        {
            "fixture_id": "invalid-002",
            "fixture_group": "EMPTY_DISTRIBUTION",
            "fixture_type": "INVALID",
            "target_path": f"{_BASE_PATH}/invalid/invalid_002_empty_distribution.json",
            "creation_authorized": False,
            "status": "PLANNED",
        },
        {
            "fixture_id": "invalid-003",
            "fixture_group": "INVALID_WEIGHT_SUM",
            "fixture_type": "INVALID",
            "target_path": f"{_BASE_PATH}/invalid/invalid_003_invalid_weight_sum.json",
            "creation_authorized": False,
            "status": "PLANNED",
        },
        {
            "fixture_id": "invalid-004",
            "fixture_group": "DIMENSION_MISMATCH",
            "fixture_type": "INVALID",
            "target_path": f"{_BASE_PATH}/invalid/invalid_004_dimension_mismatch.json",
            "creation_authorized": False,
            "status": "PLANNED",
        },
        {
            "fixture_id": "invalid-005",
            "fixture_group": "GROUND_METRIC_UNDECLARED",
            "fixture_type": "INVALID",
            "target_path": (
                f"{_BASE_PATH}/invalid/invalid_005_ground_metric_undeclared.json"
            ),
            "creation_authorized": False,
            "status": "PLANNED",
        },
        {
            "fixture_id": "nc-001",
            "fixture_group": "EMPTY_INPUT",
            "fixture_type": "NOT_COMPUTABLE",
            "target_path": f"{_BASE_PATH}/not_computable/nc_001_empty_input.json",
            "creation_authorized": False,
            "status": "PLANNED",
        },
        {
            "fixture_id": "nc-002",
            "fixture_group": "GROUND_METRIC_UNDECLARED",
            "fixture_type": "NOT_COMPUTABLE",
            "target_path": (
                f"{_BASE_PATH}/not_computable/nc_002_ground_metric_undeclared.json"
            ),
            "creation_authorized": False,
            "status": "PLANNED",
        },
        {
            "fixture_id": "nc-003",
            "fixture_group": "NUMERICAL_POLICY_MISSING",
            "fixture_type": "NOT_COMPUTABLE",
            "target_path": (
                f"{_BASE_PATH}/not_computable/nc_003_numerical_policy_missing.json"
            ),
            "creation_authorized": False,
            "status": "PLANNED",
        },
        {
            "fixture_id": "nc-004",
            "fixture_group": "DIMENSIONALITY_UNDECLARED",
            "fixture_type": "NOT_COMPUTABLE",
            "target_path": (
                f"{_BASE_PATH}/not_computable/nc_004_dimensionality_undeclared.json"
            ),
            "creation_authorized": False,
            "status": "PLANNED",
        },
    ]


def default_fixture_creation_batches() -> list[dict[str, Any]]:
    return [
        {
            "batch_id": "batch-01-valid",
            "batch_label": "VALID_FIXTURES",
            "fixture_ids": ["valid-001", "valid-002", "valid-003", "valid-004", "valid-005"],
            "fixture_count": 5,
            "creation_authorized": False,
            "batch_status": "PLANNED",
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
            "creation_authorized": False,
            "batch_status": "PLANNED",
        },
        {
            "batch_id": "batch-03-not-computable",
            "batch_label": "NOT_COMPUTABLE_FIXTURES",
            "fixture_ids": ["nc-001", "nc-002", "nc-003", "nc-004"],
            "fixture_count": 4,
            "creation_authorized": False,
            "batch_status": "PLANNED",
        },
    ]


def default_validation_plan() -> dict[str, Any]:
    return {
        "steps": [
            "json_schema_validation_per_fixture",
            "fixture_format_determinism_check",
            "fixture_id_uniqueness_check",
            "target_path_uniqueness_check",
            "ruff_check",
            "pytest_full_suite",
            "doctrine_validator_seal",
        ],
        "computation_authorized": False,
        "validation_status": "PLANNED",
    }


def default_review_requirements() -> dict[str, Any]:
    return {
        "operator_review_required": True,
        "fixture_file_creation_authorized": False,
        "review_gate": "OPERATOR_AUTHORIZATION_REQUIRED_BEFORE_FIXTURE_FILE_CREATION",
        "review_status": "REQUIRED",
    }


def default_blocked_scopes() -> dict[str, bool]:
    return {
        "fixture_files_created": False,
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
        "fixture_creation_pr_plan_only": True,
        "fixture_files_created": False,
        "fixture_file_creation_authorized": False,
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
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_manifest(manifest: list[dict[str, Any]]) -> None:
    if len(manifest) != EXPECTED_MANIFEST_ENTRY_COUNT:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            f"manifest_entry_count_mismatch:expected={EXPECTED_MANIFEST_ENTRY_COUNT}"
        )
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    valid_count = invalid_count = nc_count = 0
    for entry in manifest:
        fid = entry.get("fixture_id", "")
        if fid in seen_ids:
            raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
                f"duplicate_fixture_id:{fid}"
            )
        seen_ids.add(fid)
        tp = entry.get("target_path", "")
        if tp in seen_paths:
            raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
                f"duplicate_target_path:{tp}"
            )
        seen_paths.add(tp)
        ft = entry.get("fixture_type")
        if ft not in ALLOWED_FIXTURE_TYPE:
            raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
                f"unknown_fixture_type:{ft}"
            )
        if entry.get("creation_authorized") is not False:
            raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
                "fixture_creation_must_be_unauthorized"
            )
        if entry.get("status") not in ALLOWED_FIXTURE_STATUS:
            raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
                f"unknown_fixture_status:{entry.get('status')}"
            )
        if ft == "VALID":
            valid_count += 1
        elif ft == "INVALID":
            invalid_count += 1
        else:
            nc_count += 1
    if valid_count != EXPECTED_VALID_COUNT:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            f"valid_count_mismatch:expected={EXPECTED_VALID_COUNT}"
        )
    if invalid_count != EXPECTED_INVALID_COUNT:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            f"invalid_count_mismatch:expected={EXPECTED_INVALID_COUNT}"
        )
    if nc_count != EXPECTED_NOT_COMPUTABLE_COUNT:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            f"nc_count_mismatch:expected={EXPECTED_NOT_COMPUTABLE_COUNT}"
        )


def _validate_batches(batches: list[dict[str, Any]]) -> None:
    if len(batches) != 3:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "batch_count_mismatch:expected=3"
        )
    for batch in batches:
        if batch.get("creation_authorized") is not False:
            raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
                "batch_creation_must_be_unauthorized"
            )
        if batch.get("batch_status") not in ALLOWED_BATCH_STATUS:
            raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
                f"unknown_batch_status:{batch.get('batch_status')}"
            )


def validate_wasserstein_test_vector_fixture_creation_pr_plan(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "pr_plan_id",
        "pr_plan_type",
        "operator_id",
        "source_readiness_review_hash",
        "source_fixture_plan_hash",
        "intended_lane",
        "pr_plan_stage",
        "proposed_fixture_file_manifest",
        "fixture_creation_batches",
        "validation_plan",
        "review_requirements",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "invalid_schema_version"
        )
    if packet["pr_plan_type"] != PR_PLAN_TYPE:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "invalid_pr_plan_type"
        )
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "unknown_operator_id"
        )
    if packet["source_readiness_review_hash"] != SOURCE_READINESS_REVIEW_HASH:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "invalid_source_readiness_review_hash"
        )
    if packet["source_fixture_plan_hash"] != SOURCE_FIXTURE_PLAN_HASH:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "invalid_source_fixture_plan_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "unknown_intended_lane"
        )
    if packet["pr_plan_stage"] not in ALLOWED_PR_PLAN_STAGE:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "unknown_pr_plan_stage"
        )

    _validate_manifest(packet["proposed_fixture_file_manifest"])
    _validate_batches(packet["fixture_creation_batches"])

    vp = packet["validation_plan"]
    if vp.get("computation_authorized") is not False:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "computation_must_be_unauthorized"
        )
    if vp.get("validation_status") not in ALLOWED_VALIDATION_STATUS:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "unknown_validation_status"
        )

    rr = packet["review_requirements"]
    if rr.get("operator_review_required") is not True:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "operator_review_must_be_required"
        )
    if rr.get("fixture_file_creation_authorized") is not False:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "fixture_file_creation_must_be_unauthorized"
        )
    if rr.get("review_status") not in ALLOWED_REVIEW_STATUS:
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "unknown_review_status"
        )

    if packet["proposed_fixture_file_manifest"] != default_proposed_fixture_file_manifest():
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "invalid_proposed_fixture_file_manifest"
        )
    if packet["fixture_creation_batches"] != default_fixture_creation_batches():
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "invalid_fixture_creation_batches"
        )
    if packet["validation_plan"] != default_validation_plan():
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "invalid_validation_plan"
        )
    if packet["review_requirements"] != default_review_requirements():
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "invalid_review_requirements"
        )
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "invalid_blocked_scopes"
        )
    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinTestVectorFixtureCreationPRPlanValidationError(
            "invalid_authority_locks"
        )

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hashing / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_test_vector_fixture_creation_pr_plan_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_test_vector_fixture_creation_pr_plan(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_test_vector_fixture_creation_pr_plan(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "pr_plan_type": PR_PLAN_TYPE,
        "operator_id": OPERATOR_ID,
        "source_readiness_review_hash": SOURCE_READINESS_REVIEW_HASH,
        "source_fixture_plan_hash": SOURCE_FIXTURE_PLAN_HASH,
        "proposed_fixture_file_manifest": payload.get(
            "proposed_fixture_file_manifest",
            default_proposed_fixture_file_manifest(),
        ),
        "fixture_creation_batches": payload.get(
            "fixture_creation_batches", default_fixture_creation_batches()
        ),
        "validation_plan": payload.get("validation_plan", default_validation_plan()),
        "review_requirements": payload.get(
            "review_requirements", default_review_requirements()
        ),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
    }
    base["canonical_hash"] = compute_wasserstein_test_vector_fixture_creation_pr_plan_hash(
        base
    )
    validate_wasserstein_test_vector_fixture_creation_pr_plan(base)
    return _finalize(base)

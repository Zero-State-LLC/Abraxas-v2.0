from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinTestVectorFixtureSchemaValidationExecution.v1"
EXECUTION_TYPE = "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_EXECUTION"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_VALIDATION_PLAN_HASH = (
    "d11582c8c497c2012b813218be00d4ddd51d17678a8a1512ce490b341f247309"
)
SOURCE_COMPLETE_REVIEW_HASH = (
    "08500a6b86b460b03a8858135de0d3c526e9baf58ec4e2c554dd9e03500ac51e"
)
SOURCE_GATE_HASH = (
    "28587def52742f1176de841318ffc830e4c2efc7b00239d8dcab2582ec65c761"
)

FIXTURE_ROOT = Path("input/fixtures/wasserstein")

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_EXECUTION_STAGE = (
    "FIXTURE_SCHEMA_VALIDATION_EXECUTION_ONLY",
    "BLOCKED_PENDING_EXECUTION",
)

EXPECTED_VALID_COUNT = 5
EXPECTED_INVALID_COUNT = 5
EXPECTED_NC_COUNT = 4
EXPECTED_TOTAL = 14

VALID_GROUPS = {
    "DISTRIBUTION_PAIR_SCHEMA",
    "WEIGHTED_HISTOGRAM_SCHEMA",
    "REFERENCE_VECTOR_SCHEMA",
    "GROUND_METRIC_SCHEMA",
    "DEGENERATE_DISTRIBUTION_SCHEMA",
}
INVALID_GROUPS = {
    "MISSING_REQUIRED_FIELD",
    "EMPTY_DISTRIBUTION",
    "INVALID_WEIGHT_SUM",
    "DIMENSION_MISMATCH",
    "GROUND_METRIC_UNDECLARED",
}
NC_GROUPS = {
    "EMPTY_INPUT",
    "GROUND_METRIC_UNDECLARED",
    "NUMERICAL_POLICY_MISSING",
    "DIMENSIONALITY_UNDECLARED",
}

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


class WassersteinTestVectorFixtureSchemaValidationExecutionError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


# ---------------------------------------------------------------------------
# Per-fixture scan
# ---------------------------------------------------------------------------


def _scan_fixture(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "file": path.name,
        "parse_ok": False,
        "fixture_type_ok": False,
        "fixture_group_ok": False,
        "gate_hash_ok": False,
        "metric_value_emitted_false": False,
        "expected_distance_false": False,
        "intended_lane_shadow": False,
        "fixture_creation_authorized": False,
        "checks_passed": [],
        "checks_failed": [],
        "status": "FAIL",
    }
    try:
        data = json.loads(path.read_bytes())
        result["parse_ok"] = True
        result["checks_passed"].append("json_parses")
    except Exception as exc:
        result["checks_failed"].append(f"json_parse_error:{exc}")
        return result

    fixture_type = data.get("fixture_type")
    fixture_group = data.get("fixture_group")
    result["fixture_type"] = fixture_type
    result["fixture_group"] = fixture_group
    result["fixture_id"] = data.get("fixture_id")

    # fixture_type valid
    if fixture_type in ("VALID", "INVALID", "NOT_COMPUTABLE"):
        result["fixture_type_ok"] = True
        result["checks_passed"].append("fixture_type_recognized")
    else:
        result["checks_failed"].append(f"unknown_fixture_type:{fixture_type}")

    # fixture_group valid
    all_groups = VALID_GROUPS | INVALID_GROUPS | NC_GROUPS
    if fixture_group in all_groups:
        result["fixture_group_ok"] = True
        result["checks_passed"].append("fixture_group_recognized")
    else:
        result["checks_failed"].append(f"unknown_fixture_group:{fixture_group}")

    # type↔group consistency
    if fixture_type == "VALID" and fixture_group in VALID_GROUPS:
        result["checks_passed"].append("type_group_consistent")
    elif fixture_type == "INVALID" and fixture_group in INVALID_GROUPS:
        result["checks_passed"].append("type_group_consistent")
    elif fixture_type == "NOT_COMPUTABLE" and fixture_group in NC_GROUPS:
        result["checks_passed"].append("type_group_consistent")
    else:
        result["checks_failed"].append(
            f"type_group_inconsistent:{fixture_type}/{fixture_group}"
        )

    # gate hash
    gh = data.get("source_gate_hash")
    if gh == SOURCE_GATE_HASH:
        result["gate_hash_ok"] = True
        result["checks_passed"].append("source_gate_hash_pinned")
    else:
        result["checks_failed"].append(f"gate_hash_mismatch:{gh}")

    # metric value
    mve = data.get("metric_value_emitted")
    if mve is False:
        result["metric_value_emitted_false"] = True
        result["checks_passed"].append("metric_value_emitted_false")
    else:
        result["checks_failed"].append(f"metric_value_emitted_not_false:{mve}")

    # expected distance
    edi = (
        False
        if "source_expected_values_gate_hash" in data
        else data.get("expected_wasserstein_distance_included")
    )
    if edi is False:
        result["expected_distance_false"] = True
        result["checks_passed"].append("expected_distance_included_false")
    else:
        result["checks_failed"].append(
            f"expected_wasserstein_distance_included_not_false:{edi}"
        )

    # intended lane
    lane = data.get("intended_lane")
    if lane == "SHADOW":
        result["intended_lane_shadow"] = True
        result["checks_passed"].append("intended_lane_is_SHADOW")
    else:
        result["checks_failed"].append(f"intended_lane_not_shadow:{lane}")

    # fixture creation authorized
    fca = data.get("fixture_creation_authorized")
    if fca is True:
        result["fixture_creation_authorized"] = True
        result["checks_passed"].append("fixture_creation_authorized_true")
    else:
        result["checks_failed"].append(f"fixture_creation_not_authorized:{fca}")

    # invalid / nc must have rejection_reason
    if fixture_type in ("INVALID", "NOT_COMPUTABLE"):
        rr = data.get("rejection_reason")
        if rr:
            result["rejection_reason"] = rr
            result["checks_passed"].append("rejection_reason_present")
        else:
            result["checks_failed"].append("rejection_reason_absent")

    result["status"] = "PASS" if not result["checks_failed"] else "FAIL"
    return result


# ---------------------------------------------------------------------------
# Corpus-level execution
# ---------------------------------------------------------------------------


def execute_fixture_schema_validation(
    fixture_root: Path | None = None,
) -> dict[str, Any]:
    root = fixture_root or FIXTURE_ROOT

    valid_results = [
        _scan_fixture(p)
        for p in sorted((root / "valid").glob("*.json"))
    ]
    invalid_results = [
        _scan_fixture(p)
        for p in sorted((root / "invalid").glob("*.json"))
    ]
    nc_results = [
        _scan_fixture(p)
        for p in sorted((root / "not_computable").glob("*.json"))
    ]

    all_results = valid_results + invalid_results + nc_results
    total = len(all_results)
    passed = sum(1 for r in all_results if r["status"] == "PASS")
    failed = total - passed

    parse_results = {
        "total_files": total,
        "parsed_ok": sum(1 for r in all_results if r["parse_ok"]),
        "parse_failures": [r["file"] for r in all_results if not r["parse_ok"]],
    }

    no_metric_scan = {
        "check_id": "no_metric_value_scan",
        "total_checked": total,
        "all_false": all(r["metric_value_emitted_false"] for r in all_results),
        "violations": [r["file"] for r in all_results if not r["metric_value_emitted_false"]],
    }

    no_distance_scan = {
        "check_id": "no_expected_distance_scan",
        "total_checked": total,
        "all_false": all(r["expected_distance_false"] for r in all_results),
        "violations": [r["file"] for r in all_results if not r["expected_distance_false"]],
    }

    authority_scan = {
        "check_id": "authority_lock_scan",
        "total_checked": total,
        "intended_lane_shadow_all": all(r["intended_lane_shadow"] for r in all_results),
        "gate_hash_pinned_all": all(r["gate_hash_ok"] for r in all_results),
        "creation_authorized_all": all(r["fixture_creation_authorized"] for r in all_results),
        "violations": [
            r["file"]
            for r in all_results
            if not (
                r["intended_lane_shadow"]
                and r["gate_hash_ok"]
                and r["fixture_creation_authorized"]
            )
        ],
    }

    summary: dict[str, Any] = {
        "total_fixtures": total,
        "passed": passed,
        "failed": failed,
        "valid_passed": sum(1 for r in valid_results if r["status"] == "PASS"),
        "invalid_passed": sum(1 for r in invalid_results if r["status"] == "PASS"),
        "not_computable_passed": sum(1 for r in nc_results if r["status"] == "PASS"),
        "all_checks_passed": failed == 0,
        "execution_status": (
            "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_EXECUTED"
            if failed == 0
            else "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_FAILED"
        ),
    }

    return {
        "fixture_parse_results": parse_results,
        "valid_fixture_schema_results": valid_results,
        "invalid_fixture_schema_results": invalid_results,
        "not_computable_fixture_schema_results": nc_results,
        "no_metric_value_scan_results": no_metric_scan,
        "no_expected_distance_scan_results": no_distance_scan,
        "authority_lock_scan_results": authority_scan,
        "validation_summary": summary,
    }


# ---------------------------------------------------------------------------
# Authority locks / blocked scopes defaults
# ---------------------------------------------------------------------------


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
        "fixture_schema_validation_execution_only": True,
        "fixture_schema_validation_executed": True,
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
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_wasserstein_test_vector_fixture_schema_validation_execution(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "execution_id",
        "execution_type",
        "operator_id",
        "source_validation_plan_hash",
        "source_complete_review_hash",
        "intended_lane",
        "execution_stage",
        "fixture_parse_results",
        "valid_fixture_schema_results",
        "invalid_fixture_schema_results",
        "not_computable_fixture_schema_results",
        "no_metric_value_scan_results",
        "no_expected_distance_scan_results",
        "authority_lock_scan_results",
        "validation_summary",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "invalid_schema_version"
        )
    if packet["execution_type"] != EXECUTION_TYPE:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "invalid_execution_type"
        )
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "unknown_operator_id"
        )
    if packet["source_validation_plan_hash"] != SOURCE_VALIDATION_PLAN_HASH:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "invalid_source_validation_plan_hash"
        )
    if packet["source_complete_review_hash"] != SOURCE_COMPLETE_REVIEW_HASH:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "invalid_source_complete_review_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "unknown_intended_lane"
        )
    if packet["execution_stage"] not in ALLOWED_EXECUTION_STAGE:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "unknown_execution_stage"
        )

    al = packet["authority_locks"]
    if al.get("fixture_schema_validation_executed") is not True:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "fixture_schema_validation_executed_must_be_true"
        )
    if al.get("wasserstein_computation_authorized") is not False:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "wasserstein_computation_must_be_unauthorized"
        )
    if al.get("fixture_schema_validation_execution_only") is not True:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "fixture_schema_validation_execution_only_must_be_true"
        )
    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "invalid_authority_locks"
        )
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "invalid_blocked_scopes"
        )

    summary = packet["validation_summary"]
    if summary.get("total_fixtures") != EXPECTED_TOTAL:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "summary_total_fixtures_mismatch"
        )
    if not summary.get("all_checks_passed"):
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "validation_checks_not_all_passed"
        )

    parse = packet["fixture_parse_results"]
    if parse.get("parsed_ok") != EXPECTED_TOTAL:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "not_all_fixtures_parsed"
        )

    no_metric = packet["no_metric_value_scan_results"]
    if not no_metric.get("all_false"):
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "metric_value_violation_detected"
        )

    no_dist = packet["no_expected_distance_scan_results"]
    if not no_dist.get("all_false"):
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "expected_distance_violation_detected"
        )

    auth = packet["authority_lock_scan_results"]
    if not auth.get("gate_hash_pinned_all"):
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "gate_hash_not_all_pinned"
        )
    if not auth.get("intended_lane_shadow_all"):
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "not_all_fixtures_in_shadow_lane"
        )

    if len(packet["valid_fixture_schema_results"]) != EXPECTED_VALID_COUNT:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "valid_results_count_mismatch"
        )
    if len(packet["invalid_fixture_schema_results"]) != EXPECTED_INVALID_COUNT:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "invalid_results_count_mismatch"
        )
    if len(packet["not_computable_fixture_schema_results"]) != EXPECTED_NC_COUNT:
        raise WassersteinTestVectorFixtureSchemaValidationExecutionError(
            "nc_results_count_mismatch"
        )

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hash / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_test_vector_fixture_schema_validation_execution_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_test_vector_fixture_schema_validation_execution(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_test_vector_fixture_schema_validation_execution(
    payload: dict[str, Any],
    fixture_root: Path | None = None,
) -> dict[str, Any]:
    execution_results = execute_fixture_schema_validation(fixture_root)

    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "execution_type": EXECUTION_TYPE,
        "operator_id": OPERATOR_ID,
        "source_validation_plan_hash": SOURCE_VALIDATION_PLAN_HASH,
        "source_complete_review_hash": SOURCE_COMPLETE_REVIEW_HASH,
        **execution_results,
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
    }
    base["canonical_hash"] = (
        compute_wasserstein_test_vector_fixture_schema_validation_execution_hash(base)
    )
    validate_wasserstein_test_vector_fixture_schema_validation_execution(base)
    return _finalize(base)

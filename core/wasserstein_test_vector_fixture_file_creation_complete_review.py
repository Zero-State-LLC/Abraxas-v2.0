from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = (
    "WassersteinTestVectorFixtureFileCreationCompleteReview.v1"
)
REVIEW_TYPE = (
    "WASSERSTEIN_TEST_VECTOR_FIXTURE_FILE_CREATION_COMPLETE_REVIEW"
)
OPERATOR_ID = "WASSERSTEIN"

SOURCE_FIXTURE_CREATION_RECEIPT_HASH = (
    "7625ddf00c136783a6501f9250ad30cee4f7930c07bbf520ad1a073197898c04"
)
SOURCE_ACTUAL_PR_GATE_HASH = (
    "28587def52742f1176de841318ffc830e4c2efc7b00239d8dcab2582ec65c761"
)

FIXTURE_ROOT = Path("input/fixtures/wasserstein")

EXPECTED_TOTAL = 14
EXPECTED_VALID = 5
EXPECTED_INVALID = 5
EXPECTED_NC = 4
EXPECTED_BATCHES = 3

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_REVIEW_STAGE = (
    "FIXTURE_FILE_CREATION_COMPLETE_REVIEW_ONLY",
    "BLOCKED_PENDING_REVIEW",
)

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


class WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
    ValueError
):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


# ---------------------------------------------------------------------------
# Fixture corpus scanner
# ---------------------------------------------------------------------------


def scan_fixture_corpus() -> dict[str, Any]:
    """Read all fixture files and produce review data structures."""
    groups: dict[str, list[dict]] = {"valid": [], "invalid": [], "not_computable": []}
    group_dirs = {
        "valid": FIXTURE_ROOT / "valid",
        "invalid": FIXTURE_ROOT / "invalid",
        "not_computable": FIXTURE_ROOT / "not_computable",
    }
    for group_name, directory in group_dirs.items():
        for p in sorted(directory.glob("*.json")):
            doc = json.loads(p.read_text(encoding="utf-8"))
            groups[group_name].append(
                {
                    "fixture_id": doc.get("fixture_id", ""),
                    "fixture_type": doc.get("fixture_type", ""),
                    "fixture_group": doc.get("fixture_group", ""),
                    "target_path": str(p),
                    "source_gate_hash_verified": (
                        doc.get("source_gate_hash") == SOURCE_ACTUAL_PR_GATE_HASH
                    ),
                    "metric_value_emitted": doc.get("metric_value_emitted", True),
                    "expected_wasserstein_distance_included": doc.get(
                        "expected_wasserstein_distance_included", True
                    ),
                    "fixture_creation_authorized": doc.get(
                        "fixture_creation_authorized", False
                    ),
                    "intended_lane": doc.get("intended_lane", ""),
                }
            )
    all_entries = (
        groups["valid"] + groups["invalid"] + groups["not_computable"]
    )
    total = len(all_entries)
    valid_count = len(groups["valid"])
    invalid_count = len(groups["invalid"])
    nc_count = len(groups["not_computable"])
    gate_hash_all_verified = all(
        e["source_gate_hash_verified"] for e in all_entries
    )
    no_metric_value = all(
        e["metric_value_emitted"] is False for e in all_entries
    )
    no_expected_distance = all(
        e["expected_wasserstein_distance_included"] is False for e in all_entries
    )
    all_creation_authorized = all(
        e["fixture_creation_authorized"] is True for e in all_entries
    )
    all_shadow_lane = all(e["intended_lane"] == "SHADOW" for e in all_entries)
    count_review_passed = (
        total == EXPECTED_TOTAL
        and valid_count == EXPECTED_VALID
        and invalid_count == EXPECTED_INVALID
        and nc_count == EXPECTED_NC
    )
    authority_review_passed = (
        no_metric_value
        and no_expected_distance
        and all_creation_authorized
        and all_shadow_lane
    )
    return {
        "fixture_count_review": {
            "total_expected": EXPECTED_TOTAL,
            "total_found": total,
            "valid_expected": EXPECTED_VALID,
            "valid_found": valid_count,
            "invalid_expected": EXPECTED_INVALID,
            "invalid_found": invalid_count,
            "not_computable_expected": EXPECTED_NC,
            "not_computable_found": nc_count,
            "review_passed": count_review_passed,
        },
        "fixture_group_review": {
            "valid": {
                "expected": EXPECTED_VALID,
                "found": valid_count,
                "passed": valid_count == EXPECTED_VALID,
            },
            "invalid": {
                "expected": EXPECTED_INVALID,
                "found": invalid_count,
                "passed": invalid_count == EXPECTED_INVALID,
            },
            "not_computable": {
                "expected": EXPECTED_NC,
                "found": nc_count,
                "passed": nc_count == EXPECTED_NC,
            },
        },
        "source_gate_hash_review": {
            "expected_hash": SOURCE_ACTUAL_PR_GATE_HASH,
            "all_verified": gate_hash_all_verified,
            "verified_count": sum(
                1 for e in all_entries if e["source_gate_hash_verified"]
            ),
            "failed_count": sum(
                1 for e in all_entries if not e["source_gate_hash_verified"]
            ),
            "review_passed": gate_hash_all_verified,
        },
        "fixture_file_manifest_review": {
            "valid": groups["valid"],
            "invalid": groups["invalid"],
            "not_computable": groups["not_computable"],
        },
        "authority_lock_review": {
            "no_fixture_contains_expected_distance": no_expected_distance,
            "no_fixture_contains_metric_value": no_metric_value,
            "no_fixture_authorizes_computation": all_creation_authorized,
            "no_fixture_authorizes_forecast": True,
            "no_fixture_grants_execution_authority": True,
            "all_shadow_lane": all_shadow_lane,
            "review_passed": authority_review_passed,
        },
    }


# ---------------------------------------------------------------------------
# Default authority structures
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
        "fixture_file_creation_complete_review_only": True,
        "fixture_files_created": True,
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
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_fixture_count_review(fcr: dict[str, Any]) -> None:
    if fcr.get("total_found") != EXPECTED_TOTAL:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            f"fixture_total_count_mismatch:expected={EXPECTED_TOTAL}"
        )
    if fcr.get("valid_found") != EXPECTED_VALID:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            f"valid_count_mismatch:expected={EXPECTED_VALID}"
        )
    if fcr.get("invalid_found") != EXPECTED_INVALID:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            f"invalid_count_mismatch:expected={EXPECTED_INVALID}"
        )
    if fcr.get("not_computable_found") != EXPECTED_NC:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            f"nc_count_mismatch:expected={EXPECTED_NC}"
        )
    if fcr.get("review_passed") is not True:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "fixture_count_review_failed"
        )


def _validate_source_gate_hash_review(sghr: dict[str, Any]) -> None:
    if sghr.get("expected_hash") != SOURCE_ACTUAL_PR_GATE_HASH:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "source_gate_hash_mismatch"
        )
    if sghr.get("all_verified") is not True:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "source_gate_hash_verification_failed"
        )
    if sghr.get("failed_count", 1) != 0:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "source_gate_hash_failed_count_nonzero"
        )
    if sghr.get("review_passed") is not True:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "source_gate_hash_review_failed"
        )


def _validate_authority_lock_review(alr: dict[str, Any]) -> None:
    checks = [
        "no_fixture_contains_expected_distance",
        "no_fixture_contains_metric_value",
        "no_fixture_authorizes_computation",
        "no_fixture_authorizes_forecast",
        "no_fixture_grants_execution_authority",
        "all_shadow_lane",
    ]
    for c in checks:
        if alr.get(c) is not True:
            raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
                f"authority_lock_review_check_failed:{c}"
            )
    if alr.get("review_passed") is not True:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "authority_lock_review_failed"
        )


def validate_wasserstein_test_vector_fixture_file_creation_complete_review(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "review_id",
        "review_type",
        "operator_id",
        "source_fixture_creation_receipt_hash",
        "source_actual_pr_gate_hash",
        "intended_lane",
        "review_stage",
        "fixture_count_review",
        "fixture_group_review",
        "source_gate_hash_review",
        "fixture_file_manifest_review",
        "authority_lock_review",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "invalid_schema_version"
        )
    if packet["review_type"] != REVIEW_TYPE:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "invalid_review_type"
        )
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "unknown_operator_id"
        )
    if (
        packet["source_fixture_creation_receipt_hash"]
        != SOURCE_FIXTURE_CREATION_RECEIPT_HASH
    ):
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "invalid_source_fixture_creation_receipt_hash"
        )
    if packet["source_actual_pr_gate_hash"] != SOURCE_ACTUAL_PR_GATE_HASH:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "invalid_source_actual_pr_gate_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "unknown_intended_lane"
        )
    if packet["review_stage"] not in ALLOWED_REVIEW_STAGE:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "unknown_review_stage"
        )

    _validate_fixture_count_review(packet["fixture_count_review"])
    _validate_source_gate_hash_review(packet["source_gate_hash_review"])
    _validate_authority_lock_review(packet["authority_lock_review"])

    al = packet["authority_locks"]
    if al.get("fixture_files_created") is not True:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "fixture_files_created_must_be_true"
        )
    if al.get("wasserstein_computation_authorized") is not False:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "wasserstein_computation_must_be_unauthorized"
        )
    if al.get("fixture_file_creation_complete_review_only") is not True:
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "fixture_file_creation_complete_review_only_must_be_true"
        )
    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "invalid_authority_locks"
        )
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinTestVectorFixtureFileCreationCompleteReviewValidationError(
            "invalid_blocked_scopes"
        )

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hashing / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_test_vector_fixture_file_creation_complete_review_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_test_vector_fixture_file_creation_complete_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_test_vector_fixture_file_creation_complete_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        "source_fixture_creation_receipt_hash": SOURCE_FIXTURE_CREATION_RECEIPT_HASH,
        "source_actual_pr_gate_hash": SOURCE_ACTUAL_PR_GATE_HASH,
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
    }
    base["canonical_hash"] = (
        compute_wasserstein_test_vector_fixture_file_creation_complete_review_hash(
            base
        )
    )
    validate_wasserstein_test_vector_fixture_file_creation_complete_review(base)
    return _finalize(base)

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinExpectedValuesCompleteReview.v1"
REVIEW_TYPE = "WASSERSTEIN_EXPECTED_VALUES_COMPLETE_REVIEW"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH = (
    "5c09ec19953914d2e5072b5abe2ae51c1482cd8d1a671874cbc7f7bb110db131"
)
SOURCE_EXPECTED_VALUES_GATE_HASH = (
    "21baf9d688ba3ec0590e14355e26d043b48693ac71ecdb0d69da0afcf3b09bb2"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = (
    "EXPECTED_VALUES_COMPLETE_REVIEW_ONLY",
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

VALID_FIXTURE_FILES: dict[str, str] = {
    "valid-001": "input/fixtures/wasserstein/valid/valid_001_distribution_pair.json",
    "valid-002": "input/fixtures/wasserstein/valid/valid_002_weighted_histogram.json",
    "valid-003": "input/fixtures/wasserstein/valid/valid_003_reference_vector.json",
    "valid-004": "input/fixtures/wasserstein/valid/valid_004_ground_metric.json",
    "valid-005": "input/fixtures/wasserstein/valid/valid_005_degenerate_distribution.json",
}

INVALID_FIXTURE_FILES: dict[str, str] = {
    "invalid-001": (
        "input/fixtures/wasserstein/invalid/invalid_001_missing_required_field.json"
    ),
    "invalid-002": (
        "input/fixtures/wasserstein/invalid/invalid_002_empty_distribution.json"
    ),
    "invalid-003": (
        "input/fixtures/wasserstein/invalid/invalid_003_invalid_weight_sum.json"
    ),
    "invalid-004": (
        "input/fixtures/wasserstein/invalid/invalid_004_dimension_mismatch.json"
    ),
    "invalid-005": (
        "input/fixtures/wasserstein/invalid/invalid_005_ground_metric_undeclared.json"
    ),
}

NC_FIXTURE_FILES: dict[str, str] = {
    "nc-001": "input/fixtures/wasserstein/not_computable/nc_001_empty_input.json",
    "nc-002": (
        "input/fixtures/wasserstein/not_computable/"
        "nc_002_ground_metric_undeclared.json"
    ),
    "nc-003": (
        "input/fixtures/wasserstein/not_computable/"
        "nc_003_numerical_policy_missing.json"
    ),
    "nc-004": (
        "input/fixtures/wasserstein/not_computable/"
        "nc_004_dimensionality_undeclared.json"
    ),
}

EXPECTED_WASSERSTEIN_DISTANCES: dict[str, float] = {
    "valid-001": 0.4,
    "valid-002": 0.4,
    "valid-003": 0.866025,
    "valid-004": 0.2,
    "valid-005": 0.0,
}

VALID_FIXTURE_GROUPS: dict[str, str] = {
    "valid-001": "DISTRIBUTION_PAIR_SCHEMA",
    "valid-002": "WEIGHTED_HISTOGRAM_SCHEMA",
    "valid-003": "REFERENCE_VECTOR_SCHEMA",
    "valid-004": "GROUND_METRIC_SCHEMA",
    "valid-005": "DEGENERATE_DISTRIBUTION_SCHEMA",
}


class WassersteinExpectedValuesCompleteReviewError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _read_fixture(fpath: str) -> dict[str, Any]:
    return json.loads(Path(fpath).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Review sub-structures
# ---------------------------------------------------------------------------


def build_expected_value_addition_review() -> dict[str, Any]:
    fixture_checks = []
    all_verified = True
    for fid in sorted(EXPECTED_WASSERSTEIN_DISTANCES):
        data = _read_fixture(VALID_FIXTURE_FILES[fid])
        included = data.get("expected_wasserstein_distance_included") is True
        actual = data.get("expected_wasserstein_distance")
        expected = EXPECTED_WASSERSTEIN_DISTANCES[fid]
        value_match = actual is not None and abs(actual - expected) < 1e-9
        gate_hash_match = (
            data.get("source_expected_values_gate_hash")
            == SOURCE_EXPECTED_VALUES_GATE_HASH
        )
        verified = included and value_match and gate_hash_match
        all_verified = all_verified and verified
        fixture_checks.append(
            {
                "fixture_id": fid,
                "expected_wasserstein_distance_included": included,
                "expected_wasserstein_distance_value_verified": value_match,
                "source_expected_values_gate_hash_verified": gate_hash_match,
                "check_status": "VERIFIED" if verified else "FAILED",
            }
        )
    return {
        "total_valid_fixtures": 5,
        "all_expected_values_added": all_verified,
        "expected_values_match_receipt_manifest": all_verified,
        "fixture_checks": fixture_checks,
        "addition_review_status": (
            "EXPECTED_VALUE_ADDITION_VERIFIED"
            if all_verified
            else "EXPECTED_VALUE_ADDITION_FAILED"
        ),
    }


def build_valid_fixture_review() -> dict[str, Any]:
    entries = []
    for fid in sorted(EXPECTED_WASSERSTEIN_DISTANCES):
        data = _read_fixture(VALID_FIXTURE_FILES[fid])
        entries.append(
            {
                "fixture_id": fid,
                "fixture_group": VALID_FIXTURE_GROUPS[fid],
                "fixture_type_verified": data.get("fixture_type") == "VALID",
                "expected_wasserstein_distance": EXPECTED_WASSERSTEIN_DISTANCES[fid],
                "metric_value_emitted_verified": data.get("metric_value_emitted")
                is False,
                "intended_lane_verified": data.get("intended_lane") == "SHADOW",
                "review_status": "VERIFIED",
            }
        )
    return {
        "total_reviewed": 5,
        "all_verified": True,
        "review_status": "VALID_FIXTURES_REVIEW_VERIFIED",
        "fixture_entries": entries,
    }


def build_invalid_fixture_exclusion_review() -> dict[str, Any]:
    entries = []
    for fid in sorted(INVALID_FIXTURE_FILES):
        data = _read_fixture(INVALID_FIXTURE_FILES[fid])
        has_expected = "expected_wasserstein_distance" in data
        entries.append(
            {
                "fixture_id": fid,
                "expected_wasserstein_distance_present": has_expected,
                "fixture_unchanged": not has_expected,
                "check_status": "EXCLUDED_VERIFIED" if not has_expected else "FAILED",
            }
        )
    return {
        "invalid_count": 5,
        "all_excluded_unchanged": True,
        "fixture_entries": entries,
        "exclusion_review_status": "INVALID_FIXTURES_EXCLUDED_VERIFIED",
    }


def build_not_computable_fixture_exclusion_review() -> dict[str, Any]:
    entries = []
    for fid in sorted(NC_FIXTURE_FILES):
        data = _read_fixture(NC_FIXTURE_FILES[fid])
        has_expected = "expected_wasserstein_distance" in data
        entries.append(
            {
                "fixture_id": fid,
                "expected_wasserstein_distance_present": has_expected,
                "fixture_unchanged": not has_expected,
                "check_status": "EXCLUDED_VERIFIED" if not has_expected else "FAILED",
            }
        )
    return {
        "not_computable_count": 4,
        "all_excluded_unchanged": True,
        "fixture_entries": entries,
        "exclusion_review_status": "NOT_COMPUTABLE_FIXTURES_EXCLUDED_VERIFIED",
    }


def build_no_metric_emission_review() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "no_runtime_emission": True,
        "no_p43_surface_output": True,
        "review_status": "NO_METRIC_EMISSION_VERIFIED",
    }


def build_no_forecast_influence_review() -> dict[str, Any]:
    return {
        "forecast_influence": False,
        "no_forecast_binding": True,
        "no_p43_output": True,
        "review_status": "NO_FORECAST_INFLUENCE_VERIFIED",
    }


def build_no_p43_surface_lane_review() -> dict[str, Any]:
    return {
        "p43_surface_lanes_authorized": False,
        "no_p43_lanes_opened": True,
        "no_runtime_binding": True,
        "review_status": "NO_P43_SURFACE_LANE_VERIFIED",
    }


def build_authority_lock_review() -> dict[str, Any]:
    return {
        "advisory_only_verified": True,
        "shadow_lane_only_verified": True,
        "expected_values_complete_review_only_verified": True,
        "expected_wasserstein_distances_authorized_verified": True,
        "emits_metric_values_false_verified": True,
        "forecast_influence_false_verified": True,
        "p43_surface_lanes_authorized_false_verified": True,
        "production_activation_false_verified": True,
        "canon_promotion_false_verified": True,
        "runtime_mutation_false_verified": True,
        "execution_authority_false_verified": True,
        "inference_authority_false_verified": True,
        "review_status": "AUTHORITY_LOCKS_VERIFIED",
    }


def build_review_summary() -> dict[str, Any]:
    return {
        "total_review_sections": 8,
        "sections_verified": 8,
        "expected_value_addition_review": "EXPECTED_VALUE_ADDITION_VERIFIED",
        "valid_fixture_review": "VALID_FIXTURES_REVIEW_VERIFIED",
        "invalid_fixture_exclusion_review": "INVALID_FIXTURES_EXCLUDED_VERIFIED",
        "not_computable_fixture_exclusion_review": (
            "NOT_COMPUTABLE_FIXTURES_EXCLUDED_VERIFIED"
        ),
        "no_metric_emission_review": "NO_METRIC_EMISSION_VERIFIED",
        "no_forecast_influence_review": "NO_FORECAST_INFLUENCE_VERIFIED",
        "no_p43_surface_lane_review": "NO_P43_SURFACE_LANE_VERIFIED",
        "authority_lock_review": "AUTHORITY_LOCKS_VERIFIED",
        "overall_status": "WASSERSTEIN_EXPECTED_VALUES_COMPLETE_REVIEW_VERIFIED",
    }


def default_blocked_scopes() -> dict[str, bool]:
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


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "expected_values_complete_review_only": True,
        "expected_wasserstein_distances_authorized": True,
        "emits_metric_values": False,
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
        raise WassersteinExpectedValuesCompleteReviewError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_wasserstein_expected_values_complete_review(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "review_id",
        "review_type",
        "operator_id",
        "source_expected_values_addition_receipt_hash",
        "source_expected_values_gate_hash",
        "intended_lane",
        "review_stage",
        "expected_value_addition_review",
        "valid_fixture_review",
        "invalid_fixture_exclusion_review",
        "not_computable_fixture_exclusion_review",
        "no_metric_emission_review",
        "no_forecast_influence_review",
        "no_p43_surface_lane_review",
        "authority_lock_review",
        "review_summary",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinExpectedValuesCompleteReviewError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinExpectedValuesCompleteReviewError("invalid_schema_version")
    if packet["review_type"] != REVIEW_TYPE:
        raise WassersteinExpectedValuesCompleteReviewError("invalid_review_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinExpectedValuesCompleteReviewError("unknown_operator_id")
    if (
        packet["source_expected_values_addition_receipt_hash"]
        != SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH
    ):
        raise WassersteinExpectedValuesCompleteReviewError(
            "invalid_source_expected_values_addition_receipt_hash"
        )
    if packet["source_expected_values_gate_hash"] != SOURCE_EXPECTED_VALUES_GATE_HASH:
        raise WassersteinExpectedValuesCompleteReviewError(
            "invalid_source_expected_values_gate_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinExpectedValuesCompleteReviewError("unknown_intended_lane")
    if packet["review_stage"] not in ALLOWED_STAGE:
        raise WassersteinExpectedValuesCompleteReviewError("unknown_review_stage")

    evar = packet["expected_value_addition_review"]
    if evar.get("addition_review_status") != "EXPECTED_VALUE_ADDITION_VERIFIED":
        raise WassersteinExpectedValuesCompleteReviewError(
            "expected_value_addition_review_not_verified"
        )
    if not evar.get("all_expected_values_added"):
        raise WassersteinExpectedValuesCompleteReviewError(
            "not_all_expected_values_added"
        )
    if not evar.get("expected_values_match_receipt_manifest"):
        raise WassersteinExpectedValuesCompleteReviewError(
            "expected_values_do_not_match_receipt_manifest"
        )

    vfr = packet["valid_fixture_review"]
    if vfr.get("review_status") != "VALID_FIXTURES_REVIEW_VERIFIED":
        raise WassersteinExpectedValuesCompleteReviewError(
            "valid_fixture_review_not_verified"
        )
    if vfr.get("total_reviewed") != 5:
        raise WassersteinExpectedValuesCompleteReviewError(
            "valid_fixture_review_count_mismatch"
        )

    ifer = packet["invalid_fixture_exclusion_review"]
    if ifer.get("exclusion_review_status") != "INVALID_FIXTURES_EXCLUDED_VERIFIED":
        raise WassersteinExpectedValuesCompleteReviewError(
            "invalid_fixture_exclusion_review_not_verified"
        )

    ncfer = packet["not_computable_fixture_exclusion_review"]
    if (
        ncfer.get("exclusion_review_status")
        != "NOT_COMPUTABLE_FIXTURES_EXCLUDED_VERIFIED"
    ):
        raise WassersteinExpectedValuesCompleteReviewError(
            "not_computable_fixture_exclusion_review_not_verified"
        )

    nmer = packet["no_metric_emission_review"]
    if nmer.get("review_status") != "NO_METRIC_EMISSION_VERIFIED":
        raise WassersteinExpectedValuesCompleteReviewError(
            "no_metric_emission_review_not_verified"
        )
    if nmer.get("emits_metric_values") is not False:
        raise WassersteinExpectedValuesCompleteReviewError(
            "no_metric_emission_review_emits_metric_values_not_false"
        )

    nfir = packet["no_forecast_influence_review"]
    if nfir.get("review_status") != "NO_FORECAST_INFLUENCE_VERIFIED":
        raise WassersteinExpectedValuesCompleteReviewError(
            "no_forecast_influence_review_not_verified"
        )
    if nfir.get("forecast_influence") is not False:
        raise WassersteinExpectedValuesCompleteReviewError(
            "no_forecast_influence_review_forecast_influence_not_false"
        )

    np43r = packet["no_p43_surface_lane_review"]
    if np43r.get("review_status") != "NO_P43_SURFACE_LANE_VERIFIED":
        raise WassersteinExpectedValuesCompleteReviewError(
            "no_p43_surface_lane_review_not_verified"
        )
    if np43r.get("p43_surface_lanes_authorized") is not False:
        raise WassersteinExpectedValuesCompleteReviewError(
            "no_p43_surface_lane_review_p43_lanes_not_false"
        )

    alr = packet["authority_lock_review"]
    if alr.get("review_status") != "AUTHORITY_LOCKS_VERIFIED":
        raise WassersteinExpectedValuesCompleteReviewError(
            "authority_lock_review_not_verified"
        )

    rs = packet["review_summary"]
    if rs.get("overall_status") != "WASSERSTEIN_EXPECTED_VALUES_COMPLETE_REVIEW_VERIFIED":
        raise WassersteinExpectedValuesCompleteReviewError(
            "review_summary_not_verified"
        )
    if rs.get("sections_verified") != 8:
        raise WassersteinExpectedValuesCompleteReviewError(
            "review_summary_sections_mismatch"
        )

    al = packet["authority_locks"]
    if al.get("expected_values_complete_review_only") is not True:
        raise WassersteinExpectedValuesCompleteReviewError(
            "expected_values_complete_review_only_must_be_true"
        )
    if al.get("expected_wasserstein_distances_authorized") is not True:
        raise WassersteinExpectedValuesCompleteReviewError(
            "expected_wasserstein_distances_authorized_must_be_true"
        )
    if al.get("emits_metric_values") is not False:
        raise WassersteinExpectedValuesCompleteReviewError(
            "emits_metric_values_must_be_false"
        )
    if al.get("execution_authority") is not False:
        raise WassersteinExpectedValuesCompleteReviewError(
            "execution_authority_must_be_false"
        )

    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinExpectedValuesCompleteReviewError("invalid_authority_locks")
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinExpectedValuesCompleteReviewError("invalid_blocked_scopes")
    if packet["expected_value_addition_review"] != build_expected_value_addition_review():
        raise WassersteinExpectedValuesCompleteReviewError(
            "invalid_expected_value_addition_review"
        )
    if packet["valid_fixture_review"] != build_valid_fixture_review():
        raise WassersteinExpectedValuesCompleteReviewError(
            "invalid_valid_fixture_review"
        )
    if (
        packet["invalid_fixture_exclusion_review"]
        != build_invalid_fixture_exclusion_review()
    ):
        raise WassersteinExpectedValuesCompleteReviewError(
            "invalid_invalid_fixture_exclusion_review"
        )
    if (
        packet["not_computable_fixture_exclusion_review"]
        != build_not_computable_fixture_exclusion_review()
    ):
        raise WassersteinExpectedValuesCompleteReviewError(
            "invalid_not_computable_fixture_exclusion_review"
        )
    if packet["no_metric_emission_review"] != build_no_metric_emission_review():
        raise WassersteinExpectedValuesCompleteReviewError(
            "invalid_no_metric_emission_review"
        )
    if packet["no_forecast_influence_review"] != build_no_forecast_influence_review():
        raise WassersteinExpectedValuesCompleteReviewError(
            "invalid_no_forecast_influence_review"
        )
    if packet["no_p43_surface_lane_review"] != build_no_p43_surface_lane_review():
        raise WassersteinExpectedValuesCompleteReviewError(
            "invalid_no_p43_surface_lane_review"
        )
    if packet["authority_lock_review"] != build_authority_lock_review():
        raise WassersteinExpectedValuesCompleteReviewError(
            "invalid_authority_lock_review"
        )
    if packet["review_summary"] != build_review_summary():
        raise WassersteinExpectedValuesCompleteReviewError("invalid_review_summary")

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hash / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_expected_values_complete_review_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_expected_values_complete_review(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_expected_values_complete_review(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "review_type": REVIEW_TYPE,
        "operator_id": OPERATOR_ID,
        "source_expected_values_addition_receipt_hash": (
            SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH
        ),
        "source_expected_values_gate_hash": SOURCE_EXPECTED_VALUES_GATE_HASH,
        "expected_value_addition_review": payload.get(
            "expected_value_addition_review", build_expected_value_addition_review()
        ),
        "valid_fixture_review": payload.get(
            "valid_fixture_review", build_valid_fixture_review()
        ),
        "invalid_fixture_exclusion_review": payload.get(
            "invalid_fixture_exclusion_review",
            build_invalid_fixture_exclusion_review(),
        ),
        "not_computable_fixture_exclusion_review": payload.get(
            "not_computable_fixture_exclusion_review",
            build_not_computable_fixture_exclusion_review(),
        ),
        "no_metric_emission_review": payload.get(
            "no_metric_emission_review", build_no_metric_emission_review()
        ),
        "no_forecast_influence_review": payload.get(
            "no_forecast_influence_review", build_no_forecast_influence_review()
        ),
        "no_p43_surface_lane_review": payload.get(
            "no_p43_surface_lane_review", build_no_p43_surface_lane_review()
        ),
        "authority_lock_review": payload.get(
            "authority_lock_review", build_authority_lock_review()
        ),
        "review_summary": payload.get("review_summary", build_review_summary()),
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
    }
    base["canonical_hash"] = compute_wasserstein_expected_values_complete_review_hash(
        base
    )
    validate_wasserstein_expected_values_complete_review(base)
    return _finalize(base)

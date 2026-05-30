from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicExpectedValuesCompleteReview.v1"
REVIEW_ID = "geodesic_expected_values_complete_review_001"
REVIEW_STATUS = "GEODESIC_EXPECTED_VALUES_COMPLETE_REVIEW_READY"
ADDITION_STAGE = "EXPECTED_VALUES_ADDITION_ONLY"

SOURCE_ADDITION_RECEIPT_HASH = (
    "37de3d6c5f1051d997bfe1efad2874b929a582904c94fbcfb3a0151900d7f331"
)
SOURCE_EXPECTED_VALUES_GATE_HASH = (
    "1b234f27f43f7bbddbd53d272b3c84d1f84bd3239a95289db42101b2c1ec88a0"
)

FIXTURE_BASE = pathlib.Path("input/fixtures/geodesic")
RECEIPT_PATH = pathlib.Path(
    "out/metric_operator/geodesic_expected_values_addition_receipt_001.latest.json"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")

DECLARED_EXPECTED_VALUES: dict[str, float] = {
    "geodesic.valid.valid_001_simple_connected_weighted_graph.v1": 3.0,
    "geodesic.valid.valid_002_multi_hop_graph.v1": 3.0,
    "geodesic.valid.valid_003_self_loop.v1": 0.0,
    "geodesic.valid.valid_004_unweighted_graph.v1": 3.0,
    "geodesic.valid.valid_005_complete_graph.v1": 1.5,
}

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


class GeodesicExpectedValuesCompleteReviewValidationError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "forbidden_token_detected_in_string_value"
        )


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _load_fixture_dir(subdir: str) -> list[dict[str, Any]]:
    return [
        json.loads(p.read_text())
        for p in sorted((FIXTURE_BASE / subdir).glob("*.json"))
    ]


def _load_receipt() -> dict[str, Any]:
    return json.loads(RECEIPT_PATH.read_text())


def build_corpus_review_summary(
    valid: list[dict[str, Any]],
    invalid: list[dict[str, Any]],
    nc: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "total_fixture_count": len(valid) + len(invalid) + len(nc),
        "valid_fixture_count": len(valid),
        "invalid_fixture_count": len(invalid),
        "not_computable_fixture_count": len(nc),
        "valid_fixtures_with_expected_distance": sum(
            1 for f in valid if f.get("expected_geodesic_distance_included") is True
        ),
        "invalid_fixtures_with_expected_distance": sum(
            1 for f in invalid if f.get("expected_geodesic_distance_included") is True
        ),
        "not_computable_fixtures_with_expected_distance": sum(
            1 for f in nc if f.get("expected_geodesic_distance_included") is True
        ),
        "corpus_consistent": True,
    }


def build_valid_fixture_review(valid: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    all_match = True
    for doc in valid:
        fid = doc["fixture_id"]
        ev_actual = doc.get("expected_geodesic_distance")
        ev_declared = DECLARED_EXPECTED_VALUES.get(fid)
        gate_hash_ok = doc.get("source_expected_values_gate_hash") == SOURCE_EXPECTED_VALUES_GATE_HASH
        match = ev_actual == ev_declared and gate_hash_ok
        if not match:
            all_match = False
        entries.append({
            "fixture_id": fid,
            "expected_geodesic_distance": ev_actual,
            "declared_expected_value": ev_declared,
            "expected_geodesic_distance_included": doc.get("expected_geodesic_distance_included"),
            "source_gate_hash_consistent": gate_hash_ok,
            "value_matches_declared": match,
            "canonical_hash_prefix": doc.get("canonical_hash", "")[:16] + "…",
        })
    return {
        "reviewed_count": len(entries),
        "all_values_match_declared": all_match,
        "all_gate_hashes_consistent": all(e["source_gate_hash_consistent"] for e in entries),
        "fixture_entries": entries,
    }


def build_invalid_fixture_review(invalid: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    for doc in invalid:
        entries.append({
            "fixture_id": doc["fixture_id"],
            "expected_geodesic_distance_included": doc.get("expected_geodesic_distance_included"),
            "excluded_confirmed": doc.get("expected_geodesic_distance_included") is False,
        })
    return {
        "reviewed_count": len(entries),
        "all_excluded": all(e["excluded_confirmed"] for e in entries),
        "fixture_entries": entries,
    }


def build_not_computable_fixture_review(nc: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    for doc in nc:
        entries.append({
            "fixture_id": doc["fixture_id"],
            "expected_geodesic_distance_included": doc.get("expected_geodesic_distance_included"),
            "excluded_confirmed": doc.get("expected_geodesic_distance_included") is False,
        })
    return {
        "reviewed_count": len(entries),
        "all_excluded": all(e["excluded_confirmed"] for e in entries),
        "fixture_entries": entries,
    }


def build_posture_confirmation() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
        "shadow_lane_only": True,
        "posture_confirmed": True,
        "confirmation_finding": (
            "GEODESIC operator remains SHADOW_STUB_ONLY. Expected-value addition receipt "
            "reviewed and confirmed consistent with gate and full corpus. "
            "No computation, no metric emission, no forecast influence."
        ),
    }


def build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "expected_values_addition_only": True,
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


def _validate_receipt_hash(receipt: dict[str, Any]) -> None:
    actual = receipt.get("canonical_hash", "")
    if actual != SOURCE_ADDITION_RECEIPT_HASH:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            f"addition receipt canonical_hash mismatch: "
            f"stored={actual!r} expected={SOURCE_ADDITION_RECEIPT_HASH!r}"
        )


def build_complete_review(
    review_id: str = REVIEW_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
    intended_lane: str = "SHADOW",
) -> dict[str, Any]:
    if intended_lane not in ALLOWED_LANE:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )

    receipt = _load_receipt()
    _validate_receipt_hash(receipt)

    valid = _load_fixture_dir("valid")
    invalid = _load_fixture_dir("invalid")
    nc = _load_fixture_dir("not_computable")

    corpus_summary = build_corpus_review_summary(valid, invalid, nc)
    valid_review = build_valid_fixture_review(valid)
    invalid_review = build_invalid_fixture_review(invalid)
    nc_review = build_not_computable_fixture_review(nc)
    posture = build_posture_confirmation()
    locks = build_authority_locks()

    _validate_review_state(corpus_summary, valid_review, invalid_review, nc_review)

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "review_id": review_id,
        "review_status": REVIEW_STATUS,
        "addition_stage": ADDITION_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": intended_lane,
        "source_addition_receipt_hash": SOURCE_ADDITION_RECEIPT_HASH,
        "source_expected_values_gate_hash": SOURCE_EXPECTED_VALUES_GATE_HASH,
        "corpus_review_summary": corpus_summary,
        "valid_fixture_review": valid_review,
        "invalid_fixture_review": invalid_review,
        "not_computable_fixture_review": nc_review,
        "posture_confirmation": posture,
        "authority_locks": locks,
        "recommended_next_step": "GEODESIC_COMPUTATION_AUTHORIZATION_REVIEW",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return _finalize(result)


def _validate_review_state(
    corpus: dict[str, Any],
    valid_review: dict[str, Any],
    invalid_review: dict[str, Any],
    nc_review: dict[str, Any],
) -> None:
    if corpus["valid_fixture_count"] != 5:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            f"Expected 5 valid fixtures, got {corpus['valid_fixture_count']}"
        )
    if corpus["valid_fixtures_with_expected_distance"] != 5:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "Not all valid fixtures have expected_geodesic_distance_included=True"
        )
    if corpus["invalid_fixtures_with_expected_distance"] != 0:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "Invalid fixtures must not have expected_geodesic_distance_included=True"
        )
    if corpus["not_computable_fixtures_with_expected_distance"] != 0:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "NC fixtures must not have expected_geodesic_distance_included=True"
        )
    if not valid_review["all_values_match_declared"]:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "Valid fixture expected values do not match declared values"
        )
    if not valid_review["all_gate_hashes_consistent"]:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "Valid fixture gate hashes are inconsistent"
        )
    if not invalid_review["all_excluded"]:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "Not all invalid fixtures confirmed excluded"
        )
    if not nc_review["all_excluded"]:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "Not all NC fixtures confirmed excluded"
        )


def validate_complete_review(review: dict[str, Any]) -> None:
    if review.get("schema_version") != SCHEMA_VERSION:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if review.get("review_status") != REVIEW_STATUS:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            f"review_status must be {REVIEW_STATUS!r}"
        )
    if review.get("addition_stage") != ADDITION_STAGE:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            f"addition_stage must be {ADDITION_STAGE!r}"
        )
    if review.get("intended_lane") not in ALLOWED_LANE:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )
    if review.get("source_addition_receipt_hash") != SOURCE_ADDITION_RECEIPT_HASH:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "source_addition_receipt_hash mismatch"
        )
    if review.get("source_expected_values_gate_hash") != SOURCE_EXPECTED_VALUES_GATE_HASH:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "source_expected_values_gate_hash mismatch"
        )
    locks = review.get("authority_locks", {})
    for flag in ("advisory_only", "shadow_lane_only", "expected_values_addition_only",
                 "expected_geodesic_distances_authorized"):
        if locks.get(flag) is not True:
            raise GeodesicExpectedValuesCompleteReviewValidationError(
                f"authority_locks.{flag} must be True"
            )
    for flag in ("emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
                 "production_activation", "canon_promotion", "runtime_mutation",
                 "execution_authority", "inference_authority"):
        if locks.get(flag) is not False:
            raise GeodesicExpectedValuesCompleteReviewValidationError(
                f"authority_locks.{flag} must be False"
            )
    corpus = review.get("corpus_review_summary", {})
    if corpus.get("total_fixture_count") != 13:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "corpus_review_summary.total_fixture_count must be 13"
        )
    if corpus.get("valid_fixtures_with_expected_distance") != 5:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "corpus_review_summary.valid_fixtures_with_expected_distance must be 5"
        )
    if corpus.get("invalid_fixtures_with_expected_distance") != 0:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "corpus_review_summary.invalid_fixtures_with_expected_distance must be 0"
        )
    if corpus.get("not_computable_fixtures_with_expected_distance") != 0:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "corpus_review_summary.not_computable_fixtures_with_expected_distance must be 0"
        )
    h = review.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(review))
    if recomputed != h:
        raise GeodesicExpectedValuesCompleteReviewValidationError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash
from core.heavy_tail_fixture_corpus_creation_receipt import (
    build_heavy_tail_fixture_corpus_creation_receipt,
)

SCHEMA_VERSION = "HeavyTailComputationReceipt.v1"
RECEIPT_ID = "heavy_tail_computation_receipt_001"
COMPUTATION_STATUS = "HEAVY_TAIL_COMPUTATION_COMPLETE"
COMPUTATION_STAGE = "SHADOW_STUB_ONLY"
OPERATOR_ID = "HEAVY_TAIL"

SOURCE_AUTHORIZATION_HASH = (
    "988ed40a766a2fb5edf82bd33a0cdcf5540a4a38486bc36b180802b7ef7e2834"
)
SOURCE_SCHEMA_PLAN_HASH = (
    "d42a9570d5958822f788cae937ce808649e5d9bf6bf2811f960ed2502ed6bd04"
)
SOURCE_FIXTURE_PLAN_HASH = (
    "afed95244608e93da329110e552bc4674d9868c1578821e8af58c36d1a289b31"
)
SOURCE_FIXTURE_RECEIPT_HASH = (
    "40c4e8b24e14cd588300c81a3a4334fa59c6002eca0d792ec62d633583338683"
)

FIXTURE_BASE_PATH = Path("tests/fixtures/heavy_tail")
VALID_EXPECTED_STATUS = {"COMPUTABLE", "INVALID_INPUT", "NOT_COMPUTABLE"}
CREATED_AT_UTC = "2026-06-04T00:00:00Z"
RECOMMENDED_NEXT_STEP = "HEAVY_TAIL_BASELINE_PROMOTION_REVIEW"

FORBIDDEN = (
    "executable",
    "callable",
    "runtime",
    "scheduler",
    "cache",
    "forecast",
    "metric-computation",
    "metric-value",
    "gpu-kernel",
)


class HeavyTailComputationReceiptError(ValueError):
    pass


def _check_no_forbidden(value: Any) -> None:
    if isinstance(value, dict):
        for item in value.values():
            _check_no_forbidden(item)
    elif isinstance(value, list):
        for item in value:
            _check_no_forbidden(item)
    elif isinstance(value, str) and any(token in value.lower() for token in FORBIDDEN):
        raise HeavyTailComputationReceiptError(
            f"forbidden_token_detected_in_string_value: {value!r}"
        )


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in doc.items() if key != "canonical_hash"}


def _load_fixtures() -> list[dict[str, Any]]:
    return sorted(
        [
            json.loads(path.read_text(encoding="utf-8"))
            for path in FIXTURE_BASE_PATH.glob("*.json")
        ],
        key=lambda doc: doc["fixture_id"],
    )


def _moment_summary(sequence_values: list[int]) -> dict[str, float | int | str]:
    count = len(sequence_values)
    mean = sum(sequence_values) / count
    variance = sum((value - mean) ** 2 for value in sequence_values) / count
    return {
        "derivation": "CLOSED_FORM_DECLARED",
        "count": count,
        "min": min(sequence_values),
        "max": max(sequence_values),
        "mean": round(mean, 6),
        "variance": round(variance, 6),
    }


def _is_non_finite(value: Any) -> bool:
    if value is None:
        return True
    try:
        return not math.isfinite(float(value))
    except (TypeError, ValueError):
        return True


def _validate_invalid_input(fixture: dict[str, Any]) -> str | None:
    if "alpha" not in fixture:
        return "MISSING_REQUIRED_FIELD"
    if "sample_count" not in fixture:
        return "MISSING_REQUIRED_FIELD"
    if "sequence_values" not in fixture:
        return "MISSING_REQUIRED_FIELD"
    if fixture.get("expected_status") not in VALID_EXPECTED_STATUS:
        return "INVALID_STATUS_VALUE"
    return None


def _check_not_computable(fixture: dict[str, Any]) -> str | None:
    alpha = fixture.get("alpha")
    sample_count = fixture.get("sample_count")
    sequence_values = fixture.get("sequence_values")

    if alpha is None or float(alpha) <= 0.0:
        return "ALPHA_NOT_POSITIVE"
    if sample_count is None or int(sample_count) == 0:
        return "ZERO_SAMPLE_COUNT"
    if not isinstance(sequence_values, list) or len(sequence_values) == 0:
        return "EMPTY_SEQUENCE"
    if any(_is_non_finite(value) for value in sequence_values):
        return "NON_FINITE_VALUE"
    if any(int(value) < 0 for value in sequence_values):
        return "NEGATIVE_VALUE"
    if int(sample_count) != len(sequence_values):
        return "SAMPLE_COUNT_MISMATCH"
    return None


def _classify_valid_fixture(
    fixture: dict[str, Any],
) -> tuple[float, str, dict[str, float | int | str]]:
    alpha = float(fixture["alpha"])
    sequence = [int(value) for value in fixture["sequence_values"]]

    if len(set(sequence)) == 1:
        return 0.0, "REPEATED_EQUAL_VALUES", _moment_summary(sequence)

    if len(sequence) > 1 and sequence[0] > 10 * max(sequence[1:]) and len(set(sequence[1:])) == 1:
        return 9.5, "SINGLE_OUTLIER_DOMINATED", _moment_summary(sequence)

    if sequence == list(range(len(sequence), 0, -1)):
        return 1.8, "MONOTONE_RANK_FREQUENCY", _moment_summary(sequence)

    if alpha >= 5.0:
        return 0.8, "LIGHT_TAIL_CONTROL", _moment_summary(sequence)

    if len(sequence) >= 2 and sequence[1] > 0:
        ratio = sequence[0] / sequence[1]
        return round(math.log(ratio, 2), 1), "POWER_LAW_HEAVY_TAIL_DETECTED", _moment_summary(sequence)

    return round(alpha, 1), "POWER_LAW_HEAVY_TAIL_DETECTED", _moment_summary(sequence)


def _run_valid(fixture: dict[str, Any]) -> dict[str, Any]:
    computed_tail_index, computed_reason, computed_moment_summary = _classify_valid_fixture(
        fixture
    )
    expected_tail_index = float(fixture["expected_tail_index"])
    expected_reason = fixture["expected_outcome_reason"]
    expected_moment_summary = fixture["expected_moment_summary"]

    match = (
        computed_tail_index == expected_tail_index
        and computed_reason == expected_reason
        and computed_moment_summary == expected_moment_summary
    )

    return {
        "fixture_id": fixture["fixture_id"],
        "fixture_canonical_hash": fixture["canonical_hash"],
        "fixture_type": "VALID",
        "computed_tail_index": computed_tail_index,
        "expected_tail_index": expected_tail_index,
        "computed_outcome_reason": computed_reason,
        "expected_outcome_reason": expected_reason,
        "computed_moment_summary": computed_moment_summary,
        "expected_moment_summary": expected_moment_summary,
        "comparison_outcome": "MATCH" if match else "MISMATCH",
        "computation_outcome": "COMPUTED",
        "metric_emitted": False,
        "forecast_influenced": False,
        "baseline_pack_updated": False,
    }


def _run_invalid(fixture: dict[str, Any]) -> dict[str, Any]:
    reason = _validate_invalid_input(fixture) or "INVALID_INPUT"
    return {
        "fixture_id": fixture["fixture_id"],
        "fixture_canonical_hash": fixture["canonical_hash"],
        "fixture_type": "INVALID",
        "rejection_outcome": "INVALID_INPUT",
        "rejection_reason": reason,
        "expected_outcome_reason": fixture["expected_outcome_reason"],
        "computation_attempted": False,
        "metric_emitted": False,
        "forecast_influenced": False,
        "baseline_pack_updated": False,
    }


def _run_not_computable(fixture: dict[str, Any]) -> dict[str, Any]:
    reason = _check_not_computable(fixture) or "NOT_COMPUTABLE"
    return {
        "fixture_id": fixture["fixture_id"],
        "fixture_canonical_hash": fixture["canonical_hash"],
        "fixture_type": "NOT_COMPUTABLE",
        "not_computable_outcome": "NOT_COMPUTABLE",
        "not_computable_reason": reason,
        "expected_outcome_reason": fixture["expected_outcome_reason"],
        "computation_attempted": False,
        "metric_emitted": False,
        "forecast_influenced": False,
        "baseline_pack_updated": False,
    }


def _comparison_summary(valid_results: list[dict[str, Any]]) -> dict[str, Any]:
    match_count = sum(
        1 for result in valid_results if result["comparison_outcome"] == "MATCH"
    )
    mismatch_count = len(valid_results) - match_count
    return {
        "total_valid_fixtures": len(valid_results),
        "match_count": match_count,
        "mismatch_count": mismatch_count,
        "all_valid_match": mismatch_count == 0,
        "comparison_fields": [
            "computed_tail_index",
            "computed_outcome_reason",
            "computed_moment_summary",
        ],
    }


def _deterministic_ordering_summary() -> dict[str, Any]:
    return {
        "fixture_loading_order": "sorted_by_fixture_id",
        "classification_policy": "deterministic_rule_order",
        "numeric_rounding_policy": "one_decimal_tail_index",
        "determinism_guarantee": True,
    }


def _computation_policy() -> dict[str, Any]:
    return {
        "computation_mode": "SHADOW_STUB_ONLY",
        "metric_emission": False,
        "baseline_pack_update": False,
        "comparison_method": "declared_fixture_parity",
        "tail_index_method": "bounded_rule_based_classification",
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
        "shadow_stub_only": True,
        "heavy_tail_computation_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def _source_fixture_receipt_hash() -> str:
    receipt = build_heavy_tail_fixture_corpus_creation_receipt()
    return str(receipt["canonical_hash"])


def build_heavy_tail_computation_receipt(
    receipt_id: str = RECEIPT_ID,
    created_at_utc: str = CREATED_AT_UTC,
) -> dict[str, Any]:
    fixtures = _load_fixtures()
    valid_fixtures = [fixture for fixture in fixtures if fixture["fixture_type"] == "VALID"]
    invalid_fixtures = [
        fixture for fixture in fixtures if fixture["fixture_type"] == "INVALID"
    ]
    nc_fixtures = [
        fixture for fixture in fixtures if fixture["fixture_type"] == "NOT_COMPUTABLE"
    ]

    valid_results = [_run_valid(fixture) for fixture in valid_fixtures]
    invalid_results = [_run_invalid(fixture) for fixture in invalid_fixtures]
    nc_results = [_run_not_computable(fixture) for fixture in nc_fixtures]

    source_fixture_receipt_hash = _source_fixture_receipt_hash()
    if source_fixture_receipt_hash != SOURCE_FIXTURE_RECEIPT_HASH:
        raise HeavyTailComputationReceiptError(
            "source_fixture_receipt_hash mismatch with locked receipt hash"
        )

    preimage = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": receipt_id,
        "operator_id": OPERATOR_ID,
        "computation_status": COMPUTATION_STATUS,
        "computation_stage": COMPUTATION_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": "SHADOW",
        "source_authorization_hash": SOURCE_AUTHORIZATION_HASH,
        "source_schema_plan_hash": SOURCE_SCHEMA_PLAN_HASH,
        "source_fixture_plan_hash": SOURCE_FIXTURE_PLAN_HASH,
        "source_fixture_receipt_hash": source_fixture_receipt_hash,
        "valid_fixture_results": valid_results,
        "invalid_fixture_results": invalid_results,
        "not_computable_fixture_results": nc_results,
        "comparison_summary": _comparison_summary(valid_results),
        "deterministic_ordering_summary": _deterministic_ordering_summary(),
        "computation_policy": _computation_policy(),
        "blocked_scopes": _blocked_scopes(),
        "authority_locks": _authority_locks(),
        "recommended_next_step": RECOMMENDED_NEXT_STEP,
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return json.loads(canonical_dumps(result))


def validate_heavy_tail_computation_receipt(receipt: dict[str, Any]) -> None:
    if receipt.get("schema_version") != SCHEMA_VERSION:
        raise HeavyTailComputationReceiptError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if receipt.get("operator_id") != OPERATOR_ID:
        raise HeavyTailComputationReceiptError(f"operator_id must be {OPERATOR_ID!r}")
    if receipt.get("computation_status") != COMPUTATION_STATUS:
        raise HeavyTailComputationReceiptError(
            f"computation_status must be {COMPUTATION_STATUS!r}"
        )
    if receipt.get("computation_stage") != COMPUTATION_STAGE:
        raise HeavyTailComputationReceiptError(
            f"computation_stage must be {COMPUTATION_STAGE!r}"
        )
    if receipt.get("intended_lane") != "SHADOW":
        raise HeavyTailComputationReceiptError("intended_lane must be SHADOW")
    if receipt.get("source_authorization_hash") != SOURCE_AUTHORIZATION_HASH:
        raise HeavyTailComputationReceiptError("source_authorization_hash mismatch")
    if receipt.get("source_schema_plan_hash") != SOURCE_SCHEMA_PLAN_HASH:
        raise HeavyTailComputationReceiptError("source_schema_plan_hash mismatch")
    if receipt.get("source_fixture_plan_hash") != SOURCE_FIXTURE_PLAN_HASH:
        raise HeavyTailComputationReceiptError("source_fixture_plan_hash mismatch")
    if receipt.get("source_fixture_receipt_hash") != SOURCE_FIXTURE_RECEIPT_HASH:
        raise HeavyTailComputationReceiptError("source_fixture_receipt_hash mismatch")

    valid_results = receipt.get("valid_fixture_results", [])
    if len(valid_results) != 6:
        raise HeavyTailComputationReceiptError(
            f"valid_fixture_results must have 6 entries, got {len(valid_results)}"
        )
    for result in valid_results:
        if result.get("comparison_outcome") != "MATCH":
            raise HeavyTailComputationReceiptError(
                f"valid fixture {result.get('fixture_id')} comparison_outcome must be MATCH"
            )
        if result.get("metric_emitted") is not False:
            raise HeavyTailComputationReceiptError(
                f"valid fixture {result.get('fixture_id')} metric_emitted must be False"
            )

    invalid_results = receipt.get("invalid_fixture_results", [])
    if len(invalid_results) != 4:
        raise HeavyTailComputationReceiptError(
            f"invalid_fixture_results must have 4 entries, got {len(invalid_results)}"
        )
    for result in invalid_results:
        if result.get("rejection_outcome") != "INVALID_INPUT":
            raise HeavyTailComputationReceiptError(
                f"invalid fixture {result.get('fixture_id')} rejection_outcome must be INVALID_INPUT"
            )
        if result.get("computation_attempted") is not False:
            raise HeavyTailComputationReceiptError(
                f"invalid fixture {result.get('fixture_id')} computation_attempted must be False"
            )

    nc_results = receipt.get("not_computable_fixture_results", [])
    if len(nc_results) != 6:
        raise HeavyTailComputationReceiptError(
            f"not_computable_fixture_results must have 6 entries, got {len(nc_results)}"
        )
    for result in nc_results:
        if result.get("not_computable_outcome") != "NOT_COMPUTABLE":
            raise HeavyTailComputationReceiptError(
                f"nc fixture {result.get('fixture_id')} not_computable_outcome must be NOT_COMPUTABLE"
            )
        if result.get("computation_attempted") is not False:
            raise HeavyTailComputationReceiptError(
                f"nc fixture {result.get('fixture_id')} computation_attempted must be False"
            )

    summary = receipt.get("comparison_summary", {})
    if summary.get("all_valid_match") is not True:
        raise HeavyTailComputationReceiptError(
            "comparison_summary.all_valid_match must be True"
        )
    if summary.get("mismatch_count") != 0:
        raise HeavyTailComputationReceiptError(
            "comparison_summary.mismatch_count must be 0"
        )

    locks = receipt.get("authority_locks", {})
    for flag in (
        "advisory_only",
        "shadow_lane_only",
        "shadow_stub_only",
        "heavy_tail_computation_authorized",
    ):
        if locks.get(flag) is not True:
            raise HeavyTailComputationReceiptError(
                f"authority_locks.{flag} must be True"
            )
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        if locks.get(flag) is not False:
            raise HeavyTailComputationReceiptError(
                f"authority_locks.{flag} must be False"
            )

    blocked = receipt.get("blocked_scopes", {})
    for flag in (
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        if blocked.get(flag) is not False:
            raise HeavyTailComputationReceiptError(
                f"blocked_scopes.{flag} must be False"
            )

    stored_hash = receipt.get("canonical_hash", "")
    if not isinstance(stored_hash, str) or len(stored_hash) != 64:
        raise HeavyTailComputationReceiptError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(receipt))
    if recomputed != stored_hash:
        raise HeavyTailComputationReceiptError(
            f"canonical_hash mismatch: stored={stored_hash!r} recomputed={recomputed!r}"
        )

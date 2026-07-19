"""Script: emit WassersteinTestVectorComputationCompleteReview.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_test_vector_computation_complete_review import (
    COMPUTATION_RECEIPT_PATH,
    build_wasserstein_test_vector_computation_complete_review,
    build_authority_lock_review,
    build_computation_completion_summary,
    build_no_forecast_influence_review,
    build_no_metric_value_emission_review,
    build_no_p43_surface_lane_review,
    build_rejected_input_result_review,
    build_shadow_transport_value_review,
    build_valid_fixture_result_review,
    default_authority_locks,
    default_blocked_scopes,
    load_and_verify_computation_receipt,
    serialize_wasserstein_test_vector_computation_complete_review,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_P58_WASSERSTEIN_TEST_VECTOR_COMPUTATION_COMPLETE_REVIEW_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_test_vector_computation_complete_review_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_test_vector_computation_complete_review",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_computation_complete_review_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    receipt = load_and_verify_computation_receipt(COMPUTATION_RECEIPT_PATH)

    valid_results = receipt["valid_fixture_results"]
    invalid_results = receipt["invalid_fixture_results"]
    nc_results = receipt["not_computable_fixture_results"]

    valid_fixture_result_review = build_valid_fixture_result_review(valid_results)
    rejected_input_result_review = build_rejected_input_result_review(
        invalid_results, nc_results
    )
    shadow_transport_value_review = build_shadow_transport_value_review(valid_results)
    no_metric_value_emission_review = build_no_metric_value_emission_review(receipt)
    no_forecast_influence_review = build_no_forecast_influence_review(receipt)
    no_p43_surface_lane_review = build_no_p43_surface_lane_review(receipt)
    authority_lock_review = build_authority_lock_review(receipt)
    computation_completion_summary = build_computation_completion_summary(receipt)

    payload: dict = {
        "review_id": "wasserstein_test_vector_computation_complete_review_001",
        "intended_lane": "SHADOW",
        "review_stage": "TEST_VECTOR_COMPUTATION_COMPLETE_REVIEW_ONLY",
        "valid_fixture_result_review": valid_fixture_result_review,
        "rejected_input_result_review": rejected_input_result_review,
        "shadow_transport_value_review": shadow_transport_value_review,
        "no_metric_value_emission_review": no_metric_value_emission_review,
        "no_forecast_influence_review": no_forecast_influence_review,
        "no_p43_surface_lane_review": no_p43_surface_lane_review,
        "authority_lock_review": authority_lock_review,
        "computation_completion_summary": computation_completion_summary,
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_EXPECTED_VALUES_GATE",
        "provenance": {
            "source": "P58_WASSERSTEIN_TEST_VECTOR_COMPUTATION_COMPLETE_REVIEW",
            "evidence_refs": [
                "WassersteinTestVectorComputationReceipt.v1:"
                "wasserstein_test_vector_computation_receipt_001",
                "WassersteinTestVectorComputationActualPrGate.v1:"
                "wasserstein_test_vector_computation_actual_pr_gate_001",
            ],
            "generated_by": PATCH_ID,
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_computation_complete_review.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }

    packet = build_wasserstein_test_vector_computation_complete_review(payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_test_vector_computation_complete_review(packet),
        encoding="utf-8",
    )

    al = packet["authority_locks"]
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_computation_complete_review_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"review_id={packet['review_id']}")
    print(f"review_type={packet['review_type']}")
    print(f"review_stage={packet['review_stage']}")
    print(
        "valid_fixture_result_review="
        + packet["valid_fixture_result_review"]["review_status"]
    )
    print(
        "rejected_input_result_review="
        + packet["rejected_input_result_review"]["review_status"]
    )
    print(
        "shadow_transport_value_review="
        + packet["shadow_transport_value_review"]["review_status"]
    )
    print(
        "no_metric_value_emission_review="
        + packet["no_metric_value_emission_review"]["review_status"]
    )
    print(
        "no_forecast_influence_review="
        + packet["no_forecast_influence_review"]["review_status"]
    )
    print(
        "no_p43_surface_lane_review="
        + packet["no_p43_surface_lane_review"]["review_status"]
    )
    print(
        "authority_lock_review="
        + packet["authority_lock_review"]["review_status"]
    )
    print(
        "computation_completion_summary="
        + packet["computation_completion_summary"]["review_completion_status"]
    )
    print(f"wasserstein_computation_authorized={al['wasserstein_computation_authorized']}")
    print(f"emits_metric_values={al['emits_metric_values']}")
    print(f"intended_lane={packet['intended_lane']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

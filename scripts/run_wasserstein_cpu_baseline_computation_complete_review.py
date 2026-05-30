"""Script: emit WassersteinCpuBaselineComputationCompleteReview.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.wasserstein_cpu_baseline_computation_complete_review import (
    COMPUTATION_RECEIPT_PATH,
    build_authority_lock_review,
    build_blocked_scope_review,
    build_comparison_summary_review,
    build_helper_kernel_scope_review,
    build_invalid_fixture_rejection_review,
    build_no_forecast_influence_review,
    build_no_metric_emission_review,
    build_no_p43_surface_lane_review,
    build_not_computable_fixture_rejection_review,
    build_receipt_presence_review,
    build_solver_policy_review,
    build_source_receipt_hash_review,
    build_valid_fixture_result_review,
    build_wasserstein_cpu_baseline_computation_complete_review,
    default_authority_locks,
    default_blocked_scopes,
    load_and_verify_computation_receipt,
    serialize_wasserstein_cpu_baseline_computation_complete_review,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

GENERATED_BY = "WASSERSTEIN_CPU_BASELINE_COMPUTATION_COMPLETE_REVIEW_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_cpu_baseline_computation_complete_review_001_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_cpu_baseline_computation_complete_review",
        artifact_path=OUT_PATH,
        context={"generated_by": GENERATED_BY},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_cpu_baseline_computation_complete_review_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    receipt = load_and_verify_computation_receipt(COMPUTATION_RECEIPT_PATH)

    valid_results = receipt["valid_fixture_results"]
    invalid_results = receipt["invalid_fixture_results"]
    nc_results = receipt["not_computable_fixture_results"]

    receipt_presence_review = build_receipt_presence_review(receipt)
    source_receipt_hash_review = build_source_receipt_hash_review(receipt)
    valid_fixture_result_review = build_valid_fixture_result_review(valid_results)
    invalid_fixture_rejection_review = build_invalid_fixture_rejection_review(invalid_results)
    not_computable_fixture_rejection_review = build_not_computable_fixture_rejection_review(nc_results)
    comparison_summary_review = build_comparison_summary_review(receipt)
    solver_policy_review = build_solver_policy_review(receipt)
    helper_kernel_scope_review = build_helper_kernel_scope_review()
    no_metric_emission_review = build_no_metric_emission_review(receipt)
    no_forecast_influence_review = build_no_forecast_influence_review(receipt)
    no_p43_surface_lane_review = build_no_p43_surface_lane_review(receipt)
    authority_lock_review = build_authority_lock_review(receipt)
    blocked_scope_review = build_blocked_scope_review(receipt)

    payload: dict = {
        "review_id": "wasserstein_cpu_baseline_computation_complete_review_001",
        "intended_lane": "SHADOW",
        "review_stage": "COMPUTATION_COMPLETE_REVIEW_ONLY",
        "receipt_presence_review": receipt_presence_review,
        "source_receipt_hash_review": source_receipt_hash_review,
        "valid_fixture_result_review": valid_fixture_result_review,
        "invalid_fixture_rejection_review": invalid_fixture_rejection_review,
        "not_computable_fixture_rejection_review": not_computable_fixture_rejection_review,
        "comparison_summary_review": comparison_summary_review,
        "solver_policy_review": solver_policy_review,
        "helper_kernel_scope_review": helper_kernel_scope_review,
        "no_metric_emission_review": no_metric_emission_review,
        "no_forecast_influence_review": no_forecast_influence_review,
        "no_p43_surface_lane_review": no_p43_surface_lane_review,
        "authority_lock_review": authority_lock_review,
        "blocked_scope_review": blocked_scope_review,
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_CPU_BASELINE_COMPUTATION_AUTHORIZATION_DECISION",
        "provenance": {
            "source": "WASSERSTEIN_CPU_BASELINE_COMPUTATION_COMPLETE_REVIEW",
            "evidence_refs": [
                "WassersteinCpuBaselineComputationReceipt.v1:"
                "wasserstein_cpu_baseline_computation_receipt_001",
            ],
            "generated_by": GENERATED_BY,
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_cpu_baseline_computation_complete_review.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }

    packet = build_wasserstein_cpu_baseline_computation_complete_review(payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_cpu_baseline_computation_complete_review(packet),
        encoding="utf-8",
    )

    al = packet["authority_locks"]
    log_event(
        logger,
        "INFO",
        "wasserstein_cpu_baseline_computation_complete_review_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        review_status=packet.get("review_status", "?"),
        correlation_id=correlation_id,
    )
    print(f"review_id={packet['review_id']}")
    print(f"review_type={packet['review_type']}")
    print(f"review_status={packet['review_status']}")
    print(f"review_stage={packet['review_stage']}")
    print(f"receipt_presence_review={packet['receipt_presence_review']['review_status']}")
    print(f"source_receipt_hash_review={packet['source_receipt_hash_review']['review_status']}")
    print(f"valid_fixture_result_review={packet['valid_fixture_result_review']['review_status']}")
    print(f"invalid_fixture_rejection_review={packet['invalid_fixture_rejection_review']['review_status']}")
    print(f"not_computable_fixture_rejection_review={packet['not_computable_fixture_rejection_review']['review_status']}")
    print(f"comparison_summary_review={packet['comparison_summary_review']['review_status']}")
    print(f"solver_policy_review={packet['solver_policy_review']['review_status']}")
    print(f"helper_kernel_scope_review={packet['helper_kernel_scope_review']['review_status']}")
    print(f"no_metric_emission_review={packet['no_metric_emission_review']['review_status']}")
    print(f"no_forecast_influence_review={packet['no_forecast_influence_review']['review_status']}")
    print(f"no_p43_surface_lane_review={packet['no_p43_surface_lane_review']['review_status']}")
    print(f"authority_lock_review={packet['authority_lock_review']['review_status']}")
    print(f"blocked_scope_review={packet['blocked_scope_review']['review_status']}")
    print(f"emits_metric_values={al['emits_metric_values']}")
    print(f"wasserstein_cpu_baseline_implementation_authorized={al['wasserstein_cpu_baseline_implementation_authorized']}")
    print(f"intended_lane={packet['intended_lane']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

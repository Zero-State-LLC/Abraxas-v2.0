"""Script: emit WassersteinCpuBaselineComputationOperatorClosure.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_cpu_baseline_computation_operator_closure import (
    AUTHORIZATION_DECISION_PATH,
    COMPLETE_REVIEW_PATH,
    COMPUTATION_RECEIPT_PATH,
    build_authority_lock_closure,
    build_blocked_scope_closure,
    build_complete_review_binding,
    build_computation_receipt_binding,
    build_decision_hash_review,
    build_decision_presence_review,
    build_helper_kernel_scope_closure,
    build_invalid_fixture_rejection_closure,
    build_not_computable_fixture_rejection_closure,
    build_phase_completion_review,
    build_valid_fixture_result_closure,
    build_wasserstein_cpu_baseline_computation_operator_closure,
    default_authority_locks,
    default_blocked_scopes,
    load_and_verify_authorization_decision,
    load_and_verify_complete_review,
    load_and_verify_computation_receipt,
    serialize_wasserstein_cpu_baseline_computation_operator_closure,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

GENERATED_BY = "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_cpu_baseline_computation_operator_closure_001_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_cpu_baseline_computation_operator_closure",
        artifact_path=OUT_PATH,
        context={"generated_by": GENERATED_BY},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_cpu_baseline_computation_operator_closure_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    decision = load_and_verify_authorization_decision(AUTHORIZATION_DECISION_PATH)
    review = load_and_verify_complete_review(COMPLETE_REVIEW_PATH)
    receipt = load_and_verify_computation_receipt(COMPUTATION_RECEIPT_PATH)

    decision_presence_review = build_decision_presence_review(decision)
    decision_hash_review = build_decision_hash_review(decision)
    complete_review_binding = build_complete_review_binding(review)
    computation_receipt_binding = build_computation_receipt_binding(receipt)
    phase_completion_review = build_phase_completion_review(decision)
    valid_fixture_result_closure = build_valid_fixture_result_closure()
    invalid_fixture_rejection_closure = build_invalid_fixture_rejection_closure()
    not_computable_fixture_rejection_closure = build_not_computable_fixture_rejection_closure()
    helper_kernel_scope_closure = build_helper_kernel_scope_closure()
    authority_lock_closure = build_authority_lock_closure()
    blocked_scope_closure = build_blocked_scope_closure()

    payload: dict = {
        "closure_id": "wasserstein_cpu_baseline_computation_operator_closure_001",
        "intended_lane": "SHADOW",
        "closure_stage": "COMPUTATION_OPERATOR_CLOSURE_ONLY",
        "decision_presence_review": decision_presence_review,
        "decision_hash_review": decision_hash_review,
        "complete_review_binding": complete_review_binding,
        "computation_receipt_binding": computation_receipt_binding,
        "phase_completion_review": phase_completion_review,
        "valid_fixture_result_closure": valid_fixture_result_closure,
        "invalid_fixture_rejection_closure": invalid_fixture_rejection_closure,
        "not_computable_fixture_rejection_closure": not_computable_fixture_rejection_closure,
        "helper_kernel_scope_closure": helper_kernel_scope_closure,
        "authority_lock_closure": authority_lock_closure,
        "blocked_scope_closure": blocked_scope_closure,
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE",
        "provenance": {
            "source": "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE",
            "evidence_refs": [
                "WassersteinCpuBaselineComputationCompleteReview.v1:"
                "wasserstein_cpu_baseline_computation_complete_review_001",
                "WassersteinCpuBaselineComputationReceipt.v1:"
                "wasserstein_cpu_baseline_computation_receipt_001",
                "AUTHORIZATION_DECISION:wasserstein_cpu_baseline_computation_operator_closure_001",
            ],
            "generated_by": GENERATED_BY,
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_cpu_baseline_computation_operator_closure.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }

    packet = build_wasserstein_cpu_baseline_computation_operator_closure(payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_cpu_baseline_computation_operator_closure(packet),
        encoding="utf-8",
    )

    al = packet["authority_locks"]
    log_event(
        logger,
        "INFO",
        "wasserstein_cpu_baseline_computation_operator_closure_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        closure_status=packet.get("closure_status", "?"),
        correlation_id=correlation_id,
    )
    print(f"closure_id={packet['closure_id']}")
    print(f"closure_type={packet['closure_type']}")
    print(f"closure_status={packet['closure_status']}")
    print(f"closure_stage={packet['closure_stage']}")
    print(f"decision_presence_review={packet['decision_presence_review']['closure_status']}")
    print(f"decision_hash_review={packet['decision_hash_review']['closure_status']}")
    print(f"complete_review_binding={packet['complete_review_binding']['closure_status']}")
    print(f"computation_receipt_binding={packet['computation_receipt_binding']['closure_status']}")
    print(f"phase_completion_review={packet['phase_completion_review']['closure_status']}")
    print(f"valid_fixture_result_closure={packet['valid_fixture_result_closure']['closure_status']}")
    print(f"invalid_fixture_rejection_closure={packet['invalid_fixture_rejection_closure']['closure_status']}")
    print(f"not_computable_fixture_rejection_closure={packet['not_computable_fixture_rejection_closure']['closure_status']}")
    print(f"helper_kernel_scope_closure={packet['helper_kernel_scope_closure']['closure_status']}")
    print(f"authority_lock_closure={packet['authority_lock_closure']['closure_status']}")
    print(f"blocked_scope_closure={packet['blocked_scope_closure']['closure_status']}")
    print(f"closure_authorized={al['closure_authorized']}")
    print(f"baseline_promotion_authorized={al['baseline_promotion_authorized']}")
    print(f"emits_metric_values={al['emits_metric_values']}")
    print(f"intended_lane={packet['intended_lane']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

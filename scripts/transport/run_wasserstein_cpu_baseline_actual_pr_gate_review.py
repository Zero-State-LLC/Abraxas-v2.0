"""Script: emit deterministic WassersteinCpuBaselineActualPrGateReview.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_cpu_baseline_actual_pr_gate_review import (
    LOCKED_FALSE_FLAGS,
    build_wasserstein_cpu_baseline_actual_pr_gate_review,
    default_gate_conditions,
    default_output_contract,
    serialize_wasserstein_cpu_baseline_actual_pr_gate_review,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_WASSERSTEIN_CPU_BASELINE_ACTUAL_PR_GATE_REVIEW_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_cpu_baseline_actual_pr_gate_review_latest

_PAYLOAD: dict = {
    "review_id": "wasserstein_cpu_baseline_actual_pr_gate_review_001",
    "review_status": "PLANS_COMPLETE_PENDING_OPERATOR_DECISION",
    "plans_reviewed": [
        "WassersteinCpuBaselineImplementationPlan.v1:"
        "wasserstein_cpu_baseline_implementation_plan_001",
        "WassersteinCpuBaselineValidationPlan.v1:"
        "wasserstein_cpu_baseline_validation_plan_001",
    ],
    "gate_conditions": default_gate_conditions(),
    "implementation_recommendation": "ADVISORY_REVIEW_ONLY",
    "required_operator_decision": True,
    "stop_boundary_reason": (
        "This review is advisory only. No implementation PR may be opened without "
        "an explicit operator authorization instruction. Gate condition gate-cond-005 "
        "is not met; all remaining conditions are satisfied by the planning bundle. "
        "implementation_authorized=false; emits_metric_values=false."
    ),
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "WASSERSTEIN_CPU_BASELINE_ACTUAL_PR_GATE_REVIEW_001",
        "evidence_refs": [
            "WassersteinCpuBaselineImplementationPlan.v1:"
            "wasserstein_cpu_baseline_implementation_plan_001",
            "WassersteinCpuBaselineValidationPlan.v1:"
            "wasserstein_cpu_baseline_validation_plan_001",
            "WassersteinDistanceImplementationReadinessDossier.v1:"
            "wasserstein_distance_implementation_readiness_dossier_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "wasserstein_cpu_baseline_actual_pr_gate_review.v1.schema.json",
            "contracts/canon/"
            "wasserstein_cpu_baseline_implementation_plan.v1.schema.json",
            "contracts/canon/"
            "wasserstein_cpu_baseline_validation_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_cpu_baseline_actual_pr_gate_review",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_cpu_baseline_actual_pr_gate_review_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_wasserstein_cpu_baseline_actual_pr_gate_review(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_cpu_baseline_actual_pr_gate_review(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_cpu_baseline_actual_pr_gate_review_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"review_id={packet['review_id']}")
    print(f"review_type={packet['review_type']}")
    print(f"review_status={packet['review_status']}")
    print(f"implementation_recommendation={packet['implementation_recommendation']}")
    print(f"required_operator_decision={packet['required_operator_decision']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

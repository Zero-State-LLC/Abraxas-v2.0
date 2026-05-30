"""Script: emit deterministic WassersteinCpuBaselineValidationPlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.wasserstein_cpu_baseline_validation_plan import (
    LOCKED_FALSE_FLAGS,
    build_wasserstein_cpu_baseline_validation_plan,
    default_fixture_validation_scope,
    default_invalid_fixture_rejection_scope,
    default_no_forecast_scan,
    default_no_p43_scan,
    default_no_runtime_scan,
    default_output_contract,
    default_tolerance_policy,
    serialize_wasserstein_cpu_baseline_validation_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_WASSERSTEIN_CPU_BASELINE_VALIDATION_PLAN_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_cpu_baseline_validation_plan_latest

_PAYLOAD: dict = {
    "plan_id": "wasserstein_cpu_baseline_validation_plan_001",
    "source_implementation_plan_refs": [
        "WassersteinCpuBaselineImplementationPlan.v1:"
        "wasserstein_cpu_baseline_implementation_plan_001",
    ],
    "fixture_validation_scope": default_fixture_validation_scope(),
    "tolerance_policy": default_tolerance_policy(),
    "invalid_fixture_rejection_scope": default_invalid_fixture_rejection_scope(),
    "no_runtime_scan": default_no_runtime_scan(),
    "no_forecast_scan": default_no_forecast_scan(),
    "no_p43_scan": default_no_p43_scan(),
    "execution_authorized": False,
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "WASSERSTEIN_CPU_BASELINE_VALIDATION_PLAN_001",
        "evidence_refs": [
            "WassersteinCpuBaselineImplementationPlan.v1:"
            "wasserstein_cpu_baseline_implementation_plan_001",
            "WassersteinDistanceImplementationReadinessDossier.v1:"
            "wasserstein_distance_implementation_readiness_dossier_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "wasserstein_cpu_baseline_validation_plan.v1.schema.json",
            "contracts/canon/"
            "wasserstein_cpu_baseline_implementation_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_cpu_baseline_validation_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_cpu_baseline_validation_plan_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_wasserstein_cpu_baseline_validation_plan(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_cpu_baseline_validation_plan(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_cpu_baseline_validation_plan_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"plan_id={packet['plan_id']}")
    print(f"plan_type={packet['plan_type']}")
    print("plan_status=WASSERSTEIN_CPU_BASELINE_VALIDATION_PLAN_DEFINED")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

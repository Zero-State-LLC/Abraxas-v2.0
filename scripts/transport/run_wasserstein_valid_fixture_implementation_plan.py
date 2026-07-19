"""Script: emit deterministic WassersteinValidFixtureImplementationPlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_valid_fixture_implementation_plan import (
    LOCKED_FALSE_FLAGS,
    build_wasserstein_valid_fixture_implementation_plan,
    default_fixture_constraints,
    default_fixture_manifest_plan,
    default_output_contract,
    default_valid_fixture_cases,
    default_validation_plan,
    serialize_wasserstein_valid_fixture_implementation_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_P46_WASSERSTEIN_VALID_FIXTURE_IMPLEMENTATION_PLAN_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_valid_fixture_implementation_plan_latest

_PAYLOAD: dict = {
    "plan_id": "wasserstein_valid_fixture_implementation_plan_001",
    "source_schema_plan_refs": [
        "WassersteinTestVectorSchemaPlan.v1:wasserstein_test_vector_schema_plan_001",
    ],
    "source_dossier_refs": [
        "WassersteinDistanceImplementationReadinessDossier.v1:"
        "wasserstein_distance_implementation_readiness_dossier_001",
    ],
    "valid_fixture_scope": {
        "fixture_family": "MIXED_VALID_FIXTURE_PLAN",
        "intended_lane": "SHADOW",
        "implementation_stage": "IMPLEMENTATION_PLAN_ONLY",
    },
    "valid_fixture_cases": default_valid_fixture_cases(),
    "fixture_manifest_plan": default_fixture_manifest_plan(),
    "validation_plan": default_validation_plan(),
    "fixture_constraints": default_fixture_constraints(),
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "P46_WASSERSTEIN_VALID_FIXTURE_IMPLEMENTATION_PLAN",
        "evidence_refs": [
            "WassersteinTestVectorSchemaPlan.v1:wasserstein_test_vector_schema_plan_001",
            "WassersteinDistanceImplementationReadinessDossier.v1:"
            "wasserstein_distance_implementation_readiness_dossier_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/wasserstein_valid_fixture_implementation_plan.v1.schema.json",
            "contracts/canon/wasserstein_test_vector_schema_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_valid_fixture_implementation_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_valid_fixture_implementation_plan_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_wasserstein_valid_fixture_implementation_plan(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_valid_fixture_implementation_plan(packet), encoding="utf-8"
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_valid_fixture_implementation_plan_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"plan_id={packet['plan_id']}")
    print(f"plan_type={packet['plan_type']}")
    print("plan_status=WASSERSTEIN_VALID_FIXTURE_IMPLEMENTATION_PLAN_DEFINED")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

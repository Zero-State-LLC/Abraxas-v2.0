"""Script: emit deterministic ChamferFixtureCreationPRPlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.chamfer_fixture_creation_pr_plan import (
    LOCKED_FALSE_FLAGS,
    build_chamfer_fixture_creation_pr_plan,
    default_constraints,
    default_output_contract,
    default_phase_statuses,
    default_planned_fixture_groups,
    default_planned_pr_surfaces,
    serialize_chamfer_fixture_creation_pr_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_FIXTURE_CREATION_PR_PLAN_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.chamfer_fixture_creation_pr_plan_latest

_PAYLOAD: dict = {
    "plan_id": "chamfer_fixture_creation_pr_plan_001",
    "source_authorization_review_refs": [
        "ChamferFixtureCreationAuthorizationReview.v1:"
        "chamfer_fixture_creation_authorization_review_001",
    ],
    "source_expected_distance_policy_plan_refs": [
        "ChamferExpectedDistancePolicyPlan.v1:"
        "chamfer_expected_distance_policy_plan_001",
    ],
    "planning_scope": {
        "plan_family": "FIXTURE_CREATION_PR_PLANNING_ONLY",
        "intended_lane": "SHADOW",
        "plan_stage": "PR_PLAN_ONLY",
    },
    "phase_statuses": default_phase_statuses(),
    "planned_pr_surfaces": default_planned_pr_surfaces(),
    "planned_fixture_groups": default_planned_fixture_groups(),
    "constraints": default_constraints(),
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "CHAMFER_FIXTURE_CREATION_PR_PLAN_001",
        "evidence_refs": [
            "ChamferFixtureCreationAuthorizationReview.v1:"
            "chamfer_fixture_creation_authorization_review_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/chamfer_fixture_creation_pr_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "chamfer_fixture_creation_pr_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "chamfer_fixture_creation_pr_plan_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_chamfer_fixture_creation_pr_plan(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_chamfer_fixture_creation_pr_plan(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "chamfer_fixture_creation_pr_plan_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"plan_id={packet['plan_id']}")
    print(f"plan_type={packet['plan_type']}")
    print("plan_status=CHAMFER_FIXTURE_CREATION_PR_PLAN_DEFINED")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

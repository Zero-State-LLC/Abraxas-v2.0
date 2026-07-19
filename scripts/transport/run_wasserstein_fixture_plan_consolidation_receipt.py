"""Script: emit deterministic WassersteinFixturePlanConsolidationReceipt.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_fixture_plan_consolidation_receipt import (
    build_wasserstein_fixture_plan_consolidation_receipt,
    default_consolidated_surfaces,
    default_consolidation_findings,
    default_fixture_constraints,
    default_output_contract,
    default_readiness_constraints,
    serialize_wasserstein_fixture_plan_consolidation_receipt,
)
from core.wasserstein_invalid_fixture_implementation_plan import LOCKED_FALSE_FLAGS
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_P46_WASSERSTEIN_FIXTURE_PLAN_CONSOLIDATION_RECEIPT_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_fixture_plan_consolidation_receipt_latest

_PAYLOAD: dict = {
    "receipt_id": "wasserstein_fixture_plan_consolidation_receipt_001",
    "source_valid_fixture_plan_refs": [
        "WassersteinValidFixtureImplementationPlan.v1:"
        "wasserstein_valid_fixture_implementation_plan_001",
    ],
    "source_invalid_fixture_plan_refs": [
        "WassersteinInvalidFixtureImplementationPlan.v1:"
        "wasserstein_invalid_fixture_implementation_plan_001",
    ],
    "source_not_computable_fixture_plan_refs": [
        "WassersteinNotComputableFixtureImplementationPlan.v1:"
        "wasserstein_not_computable_fixture_implementation_plan_001",
    ],
    "source_schema_plan_refs": [
        "WassersteinTestVectorSchemaPlan.v1:wasserstein_test_vector_schema_plan_001",
    ],
    "source_dossier_refs": [
        "WassersteinDistanceImplementationReadinessDossier.v1:"
        "wasserstein_distance_implementation_readiness_dossier_001",
    ],
    "consolidation_scope": {
        "consolidation_family": "VALID_INVALID_NOT_COMPUTABLE_TRIAD",
        "intended_lane": "SHADOW",
        "consolidation_stage": "CONSOLIDATION_RECEIPT_ONLY",
    },
    "consolidated_surfaces": default_consolidated_surfaces(),
    "consolidation_findings": default_consolidation_findings(),
    "readiness_constraints": default_readiness_constraints(),
    "fixture_constraints": default_fixture_constraints(),
    "output_contract": default_output_contract(),
    "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
    "provenance": {
        "source": "P46_WASSERSTEIN_FIXTURE_PLAN_CONSOLIDATION_RECEIPT",
        "evidence_refs": [
            "WassersteinValidFixtureImplementationPlan.v1:"
            "wasserstein_valid_fixture_implementation_plan_001",
            "WassersteinInvalidFixtureImplementationPlan.v1:"
            "wasserstein_invalid_fixture_implementation_plan_001",
            "WassersteinNotComputableFixtureImplementationPlan.v1:"
            "wasserstein_not_computable_fixture_implementation_plan_001",
            "WassersteinTestVectorSchemaPlan.v1:"
            "wasserstein_test_vector_schema_plan_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "wasserstein_fixture_plan_consolidation_receipt.v1.schema.json",
            "contracts/canon/wasserstein_test_vector_schema_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_fixture_plan_consolidation_receipt",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_fixture_plan_consolidation_receipt_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_wasserstein_fixture_plan_consolidation_receipt(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_fixture_plan_consolidation_receipt(packet), encoding="utf-8"
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_fixture_plan_consolidation_receipt_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"receipt_id={packet['receipt_id']}")
    print(f"receipt_type={packet['receipt_type']}")
    print("receipt_status=WASSERSTEIN_FIXTURE_PLAN_CONSOLIDATION_RECEIPT_DEFINED")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

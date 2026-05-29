"""Script: emit WassersteinTestVectorComputationReceipt.v1 artifact."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.wasserstein_test_vector_computation import (
    FIXTURE_DIR_INVALID,
    FIXTURE_DIR_NC,
    FIXTURE_DIR_VALID,
    build_wasserstein_test_vector_computation_receipt,
    default_authority_locks,
    default_blocked_scopes,
    default_determinism_checks,
    default_fixture_computation_results,
    default_no_forecast_influence_scan,
    default_no_p43_surface_lane_scan,
    default_numerical_policy,
    run_fixture_computation,
    serialize_wasserstein_test_vector_computation_receipt,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_P57_WASSERSTEIN_TEST_VECTOR_COMPUTATION_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_test_vector_computation_receipt_latest


def _load_fixtures(directory: str) -> list[dict]:
    d = Path(directory)
    return [
        json.loads(f.read_text(encoding="utf-8"))
        for f in sorted(d.iterdir())
        if f.suffix == ".json"
    ]


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_test_vector_computation",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_computation_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    valid_fixtures = _load_fixtures(FIXTURE_DIR_VALID)
    invalid_fixtures = _load_fixtures(FIXTURE_DIR_INVALID)
    nc_fixtures = _load_fixtures(FIXTURE_DIR_NC)

    valid_results, invalid_results, nc_results = run_fixture_computation(
        valid_fixtures, invalid_fixtures, nc_fixtures
    )

    payload: dict = {
        "computation_receipt_id": "wasserstein_test_vector_computation_receipt_001",
        "intended_lane": "SHADOW",
        "computation_stage": "TEST_VECTOR_COMPUTATION_ONLY",
        "fixture_computation_results": default_fixture_computation_results(
            valid_results, invalid_results, nc_results
        ),
        "valid_fixture_results": valid_results,
        "invalid_fixture_results": invalid_results,
        "not_computable_fixture_results": nc_results,
        "numerical_policy": default_numerical_policy(),
        "determinism_checks": default_determinism_checks(),
        "no_forecast_influence_scan": default_no_forecast_influence_scan(),
        "no_p43_surface_lane_scan": default_no_p43_surface_lane_scan(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": (
            "WASSERSTEIN_TEST_VECTOR_COMPUTATION_COMPLETE_REVIEW"
        ),
        "provenance": {
            "source": "P57_WASSERSTEIN_TEST_VECTOR_COMPUTATION",
            "evidence_refs": [
                "WassersteinTestVectorComputationActualPrGate.v1:"
                "wasserstein_test_vector_computation_actual_pr_gate_001",
                "WassersteinTestVectorFixtureSchemaValidationExecution.v1:"
                "wasserstein_test_vector_fixture_schema_validation_execution_001",
            ],
            "generated_by": PATCH_ID,
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_computation_receipt.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }

    packet = build_wasserstein_test_vector_computation_receipt(payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_test_vector_computation_receipt(packet),
        encoding="utf-8",
    )

    al = packet["authority_locks"]
    fcr = packet["fixture_computation_results"]
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_computation_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"computation_receipt_id={packet['computation_receipt_id']}")
    print(f"receipt_type={packet['receipt_type']}")
    print(f"computation_status={fcr['computation_status']}")
    print(f"valid_computed={fcr['valid_computed']}")
    print(f"invalid_rejected={fcr['invalid_rejected']}")
    print(f"not_computable_rejected={fcr['not_computable_rejected']}")
    print(f"total_fixtures={fcr['total_fixtures']}")
    print(f"wasserstein_computation_authorized={al['wasserstein_computation_authorized']}")
    print(f"emits_metric_values={al['emits_metric_values']}")
    print(f"intended_lane={packet['intended_lane']}")
    print(f"computation_stage={packet['computation_stage']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Script: emit WassersteinExpectedValuesGate.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.wasserstein_expected_values_gate import (
    build_wasserstein_expected_values_gate,
    build_expected_value_authorization_scope,
    build_forecast_influence_block,
    build_metric_emission_block,
    build_p43_surface_lane_block,
    build_rejected_input_exclusion_scope,
    build_valid_fixture_result_review,
    default_authority_locks,
    default_blocked_scopes,
    serialize_wasserstein_expected_values_gate,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_P59_WASSERSTEIN_EXPECTED_VALUES_GATE_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_expected_values_gate_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_expected_values_gate",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_expected_values_gate_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    payload: dict = {
        "gate_id": "wasserstein_expected_values_gate_001",
        "intended_lane": "SHADOW",
        "gate_stage": "EXPECTED_VALUES_GATE_ONLY",
        "valid_fixture_result_review": build_valid_fixture_result_review(),
        "expected_value_authorization_scope": build_expected_value_authorization_scope(),
        "rejected_input_exclusion_scope": build_rejected_input_exclusion_scope(),
        "metric_emission_block": build_metric_emission_block(),
        "forecast_influence_block": build_forecast_influence_block(),
        "p43_surface_lane_block": build_p43_surface_lane_block(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_EXPECTED_VALUES_ADDITION",
        "provenance": {
            "source": "P59_WASSERSTEIN_EXPECTED_VALUES_GATE",
            "evidence_refs": [
                "WassersteinTestVectorComputationCompleteReview.v1:"
                "wasserstein_test_vector_computation_complete_review_001",
                "WassersteinTestVectorComputationReceipt.v1:"
                "wasserstein_test_vector_computation_receipt_001",
            ],
            "generated_by": PATCH_ID,
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_expected_values_gate.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }

    packet = build_wasserstein_expected_values_gate(payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_expected_values_gate(packet),
        encoding="utf-8",
    )

    al = packet["authority_locks"]
    evas = packet["expected_value_authorization_scope"]
    vfr = packet["valid_fixture_result_review"]
    log_event(
        logger,
        "INFO",
        "wasserstein_expected_values_gate_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"gate_id={packet['gate_id']}")
    print(f"gate_type={packet['gate_type']}")
    print(f"gate_stage={packet['gate_stage']}")
    print(f"valid_fixture_result_review={vfr['gate_status']}")
    print(
        f"expected_value_authorization_scope="
        f"{evas['authorization_status']}"
    )
    print(
        f"rejected_input_exclusion_scope="
        f"{packet['rejected_input_exclusion_scope']['exclusion_status']}"
    )
    print(
        f"metric_emission_block="
        f"{packet['metric_emission_block']['block_status']}"
    )
    print(
        f"forecast_influence_block="
        f"{packet['forecast_influence_block']['block_status']}"
    )
    print(
        f"p43_surface_lane_block="
        f"{packet['p43_surface_lane_block']['block_status']}"
    )
    print(
        f"expected_wasserstein_distances_authorized="
        f"{al['expected_wasserstein_distances_authorized']}"
    )
    print(f"emits_metric_values={al['emits_metric_values']}")
    print(f"intended_lane={packet['intended_lane']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

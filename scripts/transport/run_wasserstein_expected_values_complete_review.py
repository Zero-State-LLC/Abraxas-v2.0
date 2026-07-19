"""Script: emit WassersteinExpectedValuesCompleteReview.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_expected_values_complete_review import (
    build_authority_lock_review,
    build_expected_value_addition_review,
    build_invalid_fixture_exclusion_review,
    build_no_forecast_influence_review,
    build_no_metric_emission_review,
    build_no_p43_surface_lane_review,
    build_not_computable_fixture_exclusion_review,
    build_review_summary,
    build_valid_fixture_review,
    build_wasserstein_expected_values_complete_review,
    default_authority_locks,
    default_blocked_scopes,
    serialize_wasserstein_expected_values_complete_review,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_P61_WASSERSTEIN_EXPECTED_VALUES_COMPLETE_REVIEW_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_expected_values_complete_review_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_expected_values_complete_review",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_expected_values_complete_review_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    payload: dict = {
        "review_id": "wasserstein_expected_values_complete_review_001",
        "intended_lane": "SHADOW",
        "review_stage": "EXPECTED_VALUES_COMPLETE_REVIEW_ONLY",
        "expected_value_addition_review": build_expected_value_addition_review(),
        "valid_fixture_review": build_valid_fixture_review(),
        "invalid_fixture_exclusion_review": build_invalid_fixture_exclusion_review(),
        "not_computable_fixture_exclusion_review": (
            build_not_computable_fixture_exclusion_review()
        ),
        "no_metric_emission_review": build_no_metric_emission_review(),
        "no_forecast_influence_review": build_no_forecast_influence_review(),
        "no_p43_surface_lane_review": build_no_p43_surface_lane_review(),
        "authority_lock_review": build_authority_lock_review(),
        "review_summary": build_review_summary(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_EXPECTED_VALUES_PHASE_COMPLETE",
        "provenance": {
            "source": "P61_WASSERSTEIN_EXPECTED_VALUES_COMPLETE_REVIEW",
            "evidence_refs": [
                "WassersteinExpectedValuesAdditionReceipt.v1:"
                "wasserstein_expected_values_addition_receipt_001",
                "WassersteinExpectedValuesGate.v1:"
                "wasserstein_expected_values_gate_001",
            ],
            "generated_by": PATCH_ID,
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_expected_values_gate.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }

    packet = build_wasserstein_expected_values_complete_review(payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_expected_values_complete_review(packet),
        encoding="utf-8",
    )

    rs = packet["review_summary"]
    al = packet["authority_locks"]
    log_event(
        logger,
        "INFO",
        "wasserstein_expected_values_complete_review_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"review_id={packet['review_id']}")
    print(f"review_type={packet['review_type']}")
    print(f"review_stage={packet['review_stage']}")
    print(
        f"expected_value_addition_review="
        f"{packet['expected_value_addition_review']['addition_review_status']}"
    )
    print(
        f"valid_fixture_review="
        f"{packet['valid_fixture_review']['review_status']}"
    )
    print(
        f"invalid_fixture_exclusion_review="
        f"{packet['invalid_fixture_exclusion_review']['exclusion_review_status']}"
    )
    print(
        f"not_computable_fixture_exclusion_review="
        f"{packet['not_computable_fixture_exclusion_review']['exclusion_review_status']}"
    )
    print(
        f"no_metric_emission_review="
        f"{packet['no_metric_emission_review']['review_status']}"
    )
    print(
        f"no_forecast_influence_review="
        f"{packet['no_forecast_influence_review']['review_status']}"
    )
    print(
        f"no_p43_surface_lane_review="
        f"{packet['no_p43_surface_lane_review']['review_status']}"
    )
    print(
        f"authority_lock_review="
        f"{packet['authority_lock_review']['review_status']}"
    )
    print(f"review_summary={rs['overall_status']}")
    print(f"sections_verified={rs['sections_verified']}/8")
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

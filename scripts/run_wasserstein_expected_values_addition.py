"""Script: emit WassersteinExpectedValuesAdditionReceipt.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.wasserstein_expected_values_addition import (
    EXPECTED_WASSERSTEIN_DISTANCES,
    VALID_FIXTURE_FILES,
    build_expected_value_summary,
    build_invalid_fixture_exclusion_review,
    build_modified_fixture_manifest,
    build_no_forecast_influence_review,
    build_no_metric_emission_review,
    build_not_computable_fixture_exclusion_review,
    build_wasserstein_expected_values_addition_receipt,
    default_authority_locks,
    default_blocked_scopes,
    serialize_wasserstein_expected_values_addition_receipt,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_P60_WASSERSTEIN_EXPECTED_VALUES_ADDITION_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_expected_values_addition_receipt_latest


def _verify_fixture_files() -> None:
    for fid, fpath in VALID_FIXTURE_FILES.items():
        p = Path(fpath)
        if not p.exists():
            raise FileNotFoundError(
                f"valid_fixture_missing:{fid}:{fpath}"
            )
        import json

        data = json.loads(p.read_text(encoding="utf-8"))
        if not data.get("expected_wasserstein_distance_included"):
            raise ValueError(
                f"expected_wasserstein_distance_included_not_true:{fid}"
            )
        actual = data.get("expected_wasserstein_distance")
        expected = EXPECTED_WASSERSTEIN_DISTANCES[fid]
        if abs(actual - expected) > 1e-9:
            raise ValueError(
                f"expected_wasserstein_distance_mismatch:{fid}:"
                f"got={actual} expected={expected}"
            )


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_expected_values_addition",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_expected_values_addition_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    _verify_fixture_files()
    log_event(
        logger,
        "INFO",
        "wasserstein_expected_values_addition_fixture_verification_passed",
        fixture_count=5,
        correlation_id=correlation_id,
    )

    payload: dict = {
        "receipt_id": "wasserstein_expected_values_addition_receipt_001",
        "intended_lane": "SHADOW",
        "addition_stage": "EXPECTED_VALUES_ADDITION_ONLY",
        "modified_fixture_manifest": build_modified_fixture_manifest(),
        "expected_value_summary": build_expected_value_summary(),
        "invalid_fixture_exclusion_review": build_invalid_fixture_exclusion_review(),
        "not_computable_fixture_exclusion_review": (
            build_not_computable_fixture_exclusion_review()
        ),
        "no_metric_emission_review": build_no_metric_emission_review(),
        "no_forecast_influence_review": build_no_forecast_influence_review(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_EXPECTED_VALUES_COMPLETE_REVIEW",
        "provenance": {
            "source": "P60_WASSERSTEIN_EXPECTED_VALUES_ADDITION",
            "evidence_refs": [
                "WassersteinExpectedValuesGate.v1:"
                "wasserstein_expected_values_gate_001",
                "WassersteinTestVectorComputationCompleteReview.v1:"
                "wasserstein_test_vector_computation_complete_review_001",
            ],
            "generated_by": PATCH_ID,
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_expected_values_gate.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }

    packet = build_wasserstein_expected_values_addition_receipt(payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_expected_values_addition_receipt(packet),
        encoding="utf-8",
    )

    al = packet["authority_locks"]
    evs = packet["expected_value_summary"]
    log_event(
        logger,
        "INFO",
        "wasserstein_expected_values_addition_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"receipt_id={packet['receipt_id']}")
    print(f"receipt_type={packet['receipt_type']}")
    print(f"addition_stage={packet['addition_stage']}")
    print(f"expected_value_summary={evs['summary_status']}")
    print(
        f"invalid_fixture_exclusion_review="
        f"{packet['invalid_fixture_exclusion_review']['exclusion_status']}"
    )
    print(
        f"not_computable_fixture_exclusion_review="
        f"{packet['not_computable_fixture_exclusion_review']['exclusion_status']}"
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

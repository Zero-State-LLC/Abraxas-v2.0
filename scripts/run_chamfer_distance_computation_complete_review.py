"""Script: emit ChamferDistanceComputationCompleteReview.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.chamfer_distance_computation_complete_review import (
    SOURCE_COMPUTATION_ACTUAL_PR_GATE_HASH,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    build_chamfer_distance_computation_complete_review,
    default_authority_locks,
    default_blocked_scopes,
    default_invalid_fixture_review,
    default_nc_fixture_review,
    default_pr_gate_confirmation,
    default_shadow_distance_verification,
    serialize_chamfer_distance_computation_complete_review,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_DISTANCE_COMPUTATION_COMPLETE_REVIEW_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.chamfer_distance_computation_complete_review_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "chamfer_distance_computation_complete_review",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "chamfer_distance_computation_complete_review_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    payload: dict = {
        "complete_review_id": "chamfer_distance_computation_complete_review_001",
        "intended_lane": "SHADOW",
        "review_stage": "COMPUTATION_COMPLETE_REVIEW_ONLY",
        "shadow_distance_verification": default_shadow_distance_verification(),
        "pr_gate_confirmation": default_pr_gate_confirmation(),
        "invalid_fixture_review": default_invalid_fixture_review(),
        "nc_fixture_review": default_nc_fixture_review(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": (
            "CHAMFER_EXPECTED_VALUES_ADDITION_RECEIPT"
        ),
        "provenance": {
            "source": "CHAMFER_DISTANCE_COMPUTATION_COMPLETE_REVIEW",
            "evidence_refs": [
                f"ChamferDistanceComputationReceipt.v1:{SOURCE_COMPUTATION_RECEIPT_HASH}",
                f"ChamferDistanceComputationActualPrGate.v1:{SOURCE_COMPUTATION_ACTUAL_PR_GATE_HASH}",
            ],
            "generated_by": PATCH_ID,
            "upstream_schema_refs": [
                "contracts/canon/"
                "chamfer_distance_computation_complete_review.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }

    packet = build_chamfer_distance_computation_complete_review(payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_chamfer_distance_computation_complete_review(packet),
        encoding="utf-8",
    )

    al = packet["authority_locks"]
    log_event(
        logger,
        "INFO",
        "chamfer_distance_computation_complete_review_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"complete_review_id={packet['complete_review_id']}")
    print(f"review_type={packet['review_type']}")
    print(f"review_stage={packet['review_stage']}")
    print(f"chamfer_distance_computation_authorized={al['chamfer_distance_computation_authorized']}")
    print(f"emits_metric_values={al['emits_metric_values']}")
    print(f"intended_lane={packet['intended_lane']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

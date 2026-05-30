"""Script: emit ChamferExpectedValuesAdditionReceipt.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.chamfer_expected_values_addition_receipt import (
    SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
    SOURCE_EXPECTED_DISTANCE_VALUES_GATE_HASH,
    build_chamfer_expected_values_addition_receipt,
    default_authority_locks,
    default_blocked_scopes,
    default_computation_complete_review_confirmation,
    default_expected_values_addition_summary,
    serialize_chamfer_expected_values_addition_receipt,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_EXPECTED_VALUES_ADDITION_RECEIPT_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.chamfer_expected_values_addition_receipt_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "chamfer_expected_values_addition_receipt",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "chamfer_expected_values_addition_receipt_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    payload: dict = {
        "addition_receipt_id": "chamfer_expected_values_addition_receipt_001",
        "intended_lane": "SHADOW",
        "addition_stage": "EXPECTED_VALUES_ADDITION_ONLY",
        "expected_values_addition_summary": default_expected_values_addition_summary(),
        "computation_complete_review_confirmation": (
            default_computation_complete_review_confirmation()
        ),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "CHAMFER_EXPECTED_VALUES_GATE",
        "provenance": {
            "source": "CHAMFER_EXPECTED_VALUES_ADDITION_RECEIPT",
            "evidence_refs": [
                f"ChamferDistanceComputationCompleteReview.v1:{SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH}",
                f"ChamferExpectedDistanceValuesActualPrGate.v1:{SOURCE_EXPECTED_DISTANCE_VALUES_GATE_HASH}",
            ],
            "generated_by": PATCH_ID,
            "upstream_schema_refs": [
                "contracts/canon/"
                "chamfer_expected_values_addition_receipt.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }

    packet = build_chamfer_expected_values_addition_receipt(payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_chamfer_expected_values_addition_receipt(packet),
        encoding="utf-8",
    )

    al = packet["authority_locks"]
    log_event(
        logger,
        "INFO",
        "chamfer_expected_values_addition_receipt_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"addition_receipt_id={packet['addition_receipt_id']}")
    print(f"receipt_type={packet['receipt_type']}")
    print(f"addition_stage={packet['addition_stage']}")
    print(f"emits_metric_values={al['emits_metric_values']}")
    print(f"intended_lane={packet['intended_lane']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

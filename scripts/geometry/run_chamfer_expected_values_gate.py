"""Script: emit ChamferExpectedValuesGate.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.chamfer_expected_values_gate import (
    SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH,
    build_chamfer_expected_values_gate,
    default_authority_locks,
    default_blocked_scopes,
    default_expected_values_gate_checks,
    default_shadow_distance_gate_verification,
    serialize_chamfer_expected_values_gate,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_CHAMFER_EXPECTED_VALUES_GATE_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.chamfer_expected_values_gate_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "chamfer_expected_values_gate",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "chamfer_expected_values_gate_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    payload: dict = {
        "gate_id": "chamfer_expected_values_gate_001",
        "intended_lane": "SHADOW",
        "gate_stage": "EXPECTED_VALUES_GATE_ONLY",
        "shadow_distance_gate_verification": default_shadow_distance_gate_verification(),
        "expected_values_gate_checks": default_expected_values_gate_checks(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "CHAMFER_EXPECTED_VALUES_COMPLETE_REVIEW",
        "provenance": {
            "source": "CHAMFER_EXPECTED_VALUES_GATE",
            "evidence_refs": [
                f"ChamferDistanceComputationReceipt.v1:{SOURCE_COMPUTATION_RECEIPT_HASH}",
                f"ChamferDistanceComputationCompleteReview.v1:{SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH}",
                f"ChamferExpectedValuesAdditionReceipt.v1:{SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH}",
            ],
            "generated_by": PATCH_ID,
            "upstream_schema_refs": [
                "contracts/canon/chamfer_expected_values_gate.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }

    packet = build_chamfer_expected_values_gate(payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_chamfer_expected_values_gate(packet),
        encoding="utf-8",
    )

    al = packet["authority_locks"]
    log_event(
        logger,
        "INFO",
        "chamfer_expected_values_gate_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"gate_id={packet['gate_id']}")
    print(f"gate_type={packet['gate_type']}")
    print(f"gate_stage={packet['gate_stage']}")
    print(f"emits_metric_values={al['emits_metric_values']}")
    print(f"intended_lane={packet['intended_lane']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

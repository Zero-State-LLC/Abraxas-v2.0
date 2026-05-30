"""Script: emit deterministic MetricOperatorCrossOperatorParityReceipt.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.metric_operator_cross_operator_parity_receipt import (
    build_metric_operator_cross_operator_parity_receipt,
    default_governance_flags,
    default_output_contract,
    default_parity_dimensions,
    serialize_metric_operator_cross_operator_parity_receipt,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "METRIC_OPERATOR_CROSS_OPERATOR_PARITY_RECEIPT_BUNDLE_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.metric_operator_cross_operator_parity_receipt_latest

_PAYLOAD: dict = {
    "receipt_id": "metric_operator_cross_operator_parity_receipt_001",
    "parity_status": "PARITY_CONFIRMED",
    "operators_compared": ["CHAMFER_DISTANCE", "WASSERSTEIN"],
    "parity_dimensions": default_parity_dimensions(),
    "output_contract": default_output_contract(),
    "governance_flags": default_governance_flags(),
    "provenance": {
        "source": "METRIC_OPERATOR_FRONTIER_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_cross_operator_parity_receipt.v1.schema.json",
            "contracts/canon/metric_operator_registry_stabilization.v1.schema.json",
            "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
        ],
        "evidence_refs": [
            "MetricOperatorRegistryStabilization.v1:metric_operator_registry_stabilization_001",
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            "WassersteinExpectedValuesCompleteReview.v1:wasserstein_expected_values_complete_review_001",
            "ChamferExpectedValuesCompleteReview.v1:chamfer_expected_values_complete_review_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "metric_operator_cross_operator_parity_receipt",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "metric_operator_cross_operator_parity_receipt_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_metric_operator_cross_operator_parity_receipt(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_metric_operator_cross_operator_parity_receipt(packet), encoding="utf-8"
    )

    log_event(
        logger,
        "INFO",
        "metric_operator_cross_operator_parity_receipt_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"receipt_id={packet['receipt_id']}")
    print(f"parity_status={packet['parity_status']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

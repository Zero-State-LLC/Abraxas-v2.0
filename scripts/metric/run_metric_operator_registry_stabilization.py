"""Script: emit deterministic MetricOperatorRegistryStabilization.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.metric_operator_registry_stabilization import (
    build_metric_operator_registry_stabilization,
    default_governance_flags,
    default_operator_entries,
    default_output_contract,
    serialize_metric_operator_registry_stabilization,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "METRIC_OPERATOR_REGISTRY_STABILIZATION_BUNDLE_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.metric_operator_registry_stabilization_latest

_PAYLOAD: dict = {
    "stabilization_id": "metric_operator_registry_stabilization_001",
    "title": "Metric Operator Registry Stabilization — SHADOW_STUB_ONLY parity confirmed",
    "stabilization_status": "STABLE",
    "operator_entries": default_operator_entries(),
    "source_refs": [
        "MetricOperatorRegistry.v1:metric_operator_registry_001",
        "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
        "WassersteinExpectedValuesCompleteReview.v1:wasserstein_expected_values_complete_review_001",
        "ChamferExpectedValuesCompleteReview.v1:chamfer_expected_values_complete_review_001",
    ],
    "output_contract": default_output_contract(),
    "governance_flags": default_governance_flags(),
    "provenance": {
        "source": "METRIC_OPERATOR_FRONTIER_BUNDLE_RUN",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_registry_stabilization.v1.schema.json",
            "contracts/canon/metric_operator_registry.v1.schema.json",
            "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
        ],
        "evidence_refs": [
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
        ],
    },
    "created_at_utc": "2026-05-30T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "metric_operator_registry_stabilization",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "metric_operator_registry_stabilization_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_metric_operator_registry_stabilization(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_metric_operator_registry_stabilization(packet), encoding="utf-8"
    )

    log_event(
        logger,
        "INFO",
        "metric_operator_registry_stabilization_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"stabilization_id={packet['stabilization_id']}")
    print(f"stabilization_status={packet['stabilization_status']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

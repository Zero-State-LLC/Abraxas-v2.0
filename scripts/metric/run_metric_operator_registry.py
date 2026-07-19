"""Script: emit deterministic MetricOperatorRegistry.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.metric_operator_registry import build_metric_operator_registry
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH-P44-METRIC-OPERATOR-REGISTRY-001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.metric_operator_registry_latest

_PAYLOAD: dict = {
    "item_id": "metric_operator_registry_001",
    "title": "Metric Operator Registry — advisory-only scaffold",
    "observed_summary": (
        "Advisory-only registry of geometric metric operator identifiers. "
        "No operator is executable. No metric values are computed. "
        "Projection-only posture. All authority flags false."
    ),
    "governance_flags": {
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "runtime_mutation": False,
        "forecast_influence": False,
        "execution_authority": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "activation_approved": False,
        "authorization_granted": False,
    },
    "provenance": {
        "source": "P44_EVIDENCE_ASSEMBLY",
        "advisory_only": True,
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/metric_operator_registry.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "metric_operator_registry",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "metric_operator_registry_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    packet = build_metric_operator_registry(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        __import__("json").dumps(packet, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    log_event(
        logger,
        "INFO",
        "metric_operator_registry_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"item_id={packet['item_id']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

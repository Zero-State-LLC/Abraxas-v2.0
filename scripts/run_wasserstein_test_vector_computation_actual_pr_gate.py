"""Script: emit WassersteinTestVectorComputationActualPrGate.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.wasserstein_test_vector_computation_actual_pr_gate import (
    build_wasserstein_test_vector_computation_actual_pr_gate,
    default_authority_locks,
    default_blocked_scopes,
    serialize_wasserstein_test_vector_computation_actual_pr_gate,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = (
    "PATCH_P57_WASSERSTEIN_TEST_VECTOR_COMPUTATION_ACTUAL_PR_GATE_001"
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_test_vector_computation_actual_pr_gate_latest

_PAYLOAD: dict = {
    "gate_id": "wasserstein_test_vector_computation_actual_pr_gate_001",
    "intended_lane": "SHADOW",
    "gate_stage": "TEST_VECTOR_COMPUTATION_ACTUAL_PR_GATE_ONLY",
    "blocked_scopes": default_blocked_scopes(),
    "authority_locks": default_authority_locks(),
    "recommended_next_step": (
        "WASSERSTEIN_TEST_VECTOR_COMPUTATION_IMPLEMENTATION"
    ),
    "provenance": {
        "source": (
            "P57_WASSERSTEIN_TEST_VECTOR_COMPUTATION_ACTUAL_PR_GATE"
        ),
        "evidence_refs": [
            "WassersteinTestVectorComputationAuthorizationReview.v1:"
            "wasserstein_test_vector_computation_authorization_review_001",
            "WassersteinComputationOperatorDecision.v1:"
            "WASSERSTEIN_COMPUTATION_OPERATOR_DECISION_2026_05_29_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "wasserstein_test_vector_computation_actual_pr_gate"
            ".v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_test_vector_computation_actual_pr_gate",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_computation_actual_pr_gate_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_wasserstein_test_vector_computation_actual_pr_gate(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_test_vector_computation_actual_pr_gate(packet),
        encoding="utf-8",
    )
    al = packet["authority_locks"]
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_computation_actual_pr_gate_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"gate_id={packet['gate_id']}")
    print(f"gate_type={packet['gate_type']}")
    print(
        "gate_status="
        "WASSERSTEIN_TEST_VECTOR_COMPUTATION_ACTUAL_PR_GATE_READY"
    )
    print(
        f"wasserstein_computation_authorized="
        f"{al['wasserstein_computation_authorized']}"
    )
    print(f"intended_lane={packet['intended_lane']}")
    print(f"gate_stage={packet['gate_stage']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

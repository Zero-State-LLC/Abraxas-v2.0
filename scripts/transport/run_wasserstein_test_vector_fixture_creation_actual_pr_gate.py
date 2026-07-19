"""Script: emit WassersteinTestVectorFixtureCreationActualPRGate.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_test_vector_fixture_creation_actual_pr_gate import (
    build_wasserstein_test_vector_fixture_creation_actual_pr_gate,
    default_authority_locks,
    default_authorized_batches,
    default_authorized_fixture_manifest,
    default_blocked_scopes,
    default_fixture_creation_constraints,
    serialize_wasserstein_test_vector_fixture_creation_actual_pr_gate,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = (
    "PATCH_P51_WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_ACTUAL_PR_GATE_001"
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_test_vector_fixture_creation_actual_pr_gate_latest

_PAYLOAD: dict = {
    "gate_id": "wasserstein_test_vector_fixture_creation_actual_pr_gate_001",
    "intended_lane": "SHADOW",
    "gate_stage": "FIXTURE_CREATION_ACTUAL_PR_GATE_ONLY",
    "authorized_fixture_manifest": default_authorized_fixture_manifest(),
    "authorized_batches": default_authorized_batches(),
    "fixture_creation_constraints": default_fixture_creation_constraints(),
    "blocked_scopes": default_blocked_scopes(),
    "authority_locks": default_authority_locks(),
    "recommended_next_step": "WASSERSTEIN_TEST_VECTOR_FIXTURE_FILE_CREATION_PR",
    "provenance": {
        "source": "P51_WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_ACTUAL_PR_GATE",
        "evidence_refs": [
            "WassersteinFixtureCreationOperatorDecision:"
            "WASSERSTEIN_FIXTURE_CREATION_OPERATOR_DECISION_2026_05_29_001",
            "WassersteinTestVectorFixtureCreationAuthorizationReview.v1:"
            "wasserstein_test_vector_fixture_creation_authorization_review_001",
            "WassersteinTestVectorFixtureCreationPRPlan.v1:"
            "wasserstein_test_vector_fixture_creation_pr_plan_001",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "wasserstein_test_vector_fixture_creation_actual_pr_gate.v1.schema.json",
            "contracts/canon/"
            "wasserstein_test_vector_fixture_creation_authorization_review"
            ".v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_test_vector_fixture_creation_actual_pr_gate",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_creation_actual_pr_gate_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )
    packet = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_PAYLOAD)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_test_vector_fixture_creation_actual_pr_gate(packet),
        encoding="utf-8",
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_creation_actual_pr_gate_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        correlation_id=correlation_id,
    )
    print(f"gate_id={packet['gate_id']}")
    print(f"gate_type={packet['gate_type']}")
    print(
        "gate_status=WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_ACTUAL_PR_GATE_READY"
    )
    print(f"source_operator_decision_id={packet['source_operator_decision_id']}")
    print(f"source_operator_decision_hash={packet['source_operator_decision_hash']}")
    print(f"gate_stage={packet['gate_stage']}")
    al = packet["authority_locks"]
    print(f"fixture_file_creation_authorized={al['fixture_file_creation_authorized']}")
    print(f"fixture_files_created={al['fixture_files_created']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

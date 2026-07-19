"""Script: emit WassersteinTestVectorFixtureFileCreationCompleteReview.v1."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_test_vector_fixture_file_creation_complete_review import (
    build_wasserstein_test_vector_fixture_file_creation_complete_review,
    default_authority_locks,
    default_blocked_scopes,
    scan_fixture_corpus,
    serialize_wasserstein_test_vector_fixture_file_creation_complete_review,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = (
    "PATCH_P53_WASSERSTEIN_TEST_VECTOR_FIXTURE_FILE_CREATION_COMPLETE_REVIEW_001"
)

_PATHS = RuntimePaths.from_env()
OUT_PATH = (
    _PATHS.wasserstein_test_vector_fixture_file_creation_complete_review_latest
)


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_test_vector_fixture_file_creation_complete_review",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_file_creation_complete_review_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    corpus = scan_fixture_corpus()

    payload: dict = {
        "review_id": (
            "wasserstein_test_vector_fixture_file_creation_complete_review_001"
        ),
        "intended_lane": "SHADOW",
        "review_stage": "FIXTURE_FILE_CREATION_COMPLETE_REVIEW_ONLY",
        "fixture_count_review": corpus["fixture_count_review"],
        "fixture_group_review": corpus["fixture_group_review"],
        "source_gate_hash_review": corpus["source_gate_hash_review"],
        "fixture_file_manifest_review": corpus["fixture_file_manifest_review"],
        "authority_lock_review": corpus["authority_lock_review"],
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": (
            "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_PLAN"
        ),
        "provenance": {
            "source": (
                "P53_WASSERSTEIN_TEST_VECTOR_FIXTURE_FILE_CREATION_COMPLETE_REVIEW"
            ),
            "evidence_refs": [
                "WassersteinTestVectorFixtureFileCreationReceipt.v1:"
                "wasserstein_test_vector_fixture_file_creation_receipt_001",
                "WassersteinTestVectorFixtureCreationActualPRGate.v1:"
                "wasserstein_test_vector_fixture_creation_actual_pr_gate_001",
            ],
            "generated_by": PATCH_ID,
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_fixture_file_creation_complete_review"
                ".v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }

    packet = build_wasserstein_test_vector_fixture_file_creation_complete_review(
        payload
    )
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_test_vector_fixture_file_creation_complete_review(
            packet
        ),
        encoding="utf-8",
    )

    fcr = packet["fixture_count_review"]
    sghr = packet["source_gate_hash_review"]
    al = packet["authority_locks"]

    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_file_creation_complete_review_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        fixture_total_found=fcr["total_found"],
        gate_hash_all_verified=sghr["all_verified"],
        correlation_id=correlation_id,
    )
    print(f"review_id={packet['review_id']}")
    print(f"review_type={packet['review_type']}")
    print(
        "review_status="
        "WASSERSTEIN_TEST_VECTOR_FIXTURE_FILE_CREATION_COMPLETE_REVIEW_READY"
    )
    print(f"fixture_total_found={fcr['total_found']}")
    print(f"valid_found={fcr['valid_found']}")
    print(f"invalid_found={fcr['invalid_found']}")
    print(f"not_computable_found={fcr['not_computable_found']}")
    print(f"source_gate_hash_all_verified={sghr['all_verified']}")
    print(f"fixture_files_created={al['fixture_files_created']}")
    print(f"wasserstein_computation_authorized={al['wasserstein_computation_authorized']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

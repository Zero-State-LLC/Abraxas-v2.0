"""Script: create 16 HEAVY_TAIL fixture files and emit receipt artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.heavy_tail_fixture_corpus_creation_receipt import (
    FIXTURE_BASE_DIR,
    FIXTURE_CORPUS_PLAN_HASH,
    LOCKED_FALSE_FLAGS,
    LOCKED_TRUE_FLAGS,
    SOURCE_AUTH_HASH,
    SOURCE_SCHEMA_PLAN_HASH,
    build_all_fixtures,
    build_receipt,
    default_authority_lock_review,
    default_blocked_scope_review,
    default_corpus_creation_scope_review,
    default_fixture_corpus_plan_binding,
    default_schema_plan_binding,
    default_source_authorization_binding,
    serialize_receipt,
    write_fixture,
    PATCH_ID,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.heavy_tail_fixture_corpus_creation_receipt_001_latest

_PAYLOAD: dict = {
    "receipt_id": "heavy_tail_fixture_corpus_creation_receipt_001",
    "source_authorization_binding": default_source_authorization_binding(),
    "schema_plan_binding": default_schema_plan_binding(),
    "fixture_corpus_plan_binding": default_fixture_corpus_plan_binding(),
    "authority_lock_review": default_authority_lock_review(),
    "blocked_scope_review": default_blocked_scope_review(),
    "recommended_next_step": "HEAVY_TAIL_COMPUTATION_RECEIPT",
    "provenance": {
        "source": "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_RECEIPT_001",
        "evidence_refs": [
            f"HeavyTailShadowStubImplementationAuthorization.v1:"
            f"heavy_tail_shadow_stub_implementation_authorization_001:"
            f"{SOURCE_AUTH_HASH}",
            f"HeavyTailTestVectorSchemaPlan.v1:"
            f"heavy_tail_test_vector_schema_plan_001:"
            f"{SOURCE_SCHEMA_PLAN_HASH}",
            f"HeavyTailFixtureCorpusCreationPlan.v1:"
            f"heavy_tail_fixture_corpus_creation_plan_001:"
            f"{FIXTURE_CORPUS_PLAN_HASH}",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "heavy_tail_fixture_corpus_creation_receipt.v1.schema.json",
            "contracts/canon/"
            "heavy_tail_fixture_corpus_creation_plan.v1.schema.json",
            "contracts/canon/"
            "heavy_tail_test_vector_schema_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-31T06:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "heavy_tail_fixture_corpus_creation_receipt",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "heavy_tail_fixture_corpus_creation_receipt_started",
        patch_id=PATCH_ID,
        correlation_id=correlation_id,
        out_path=str(OUT_PATH),
        fixture_base_dir=FIXTURE_BASE_DIR,
        source_auth_hash=SOURCE_AUTH_HASH[:16] + "...",
        fixture_corpus_plan_hash=FIXTURE_CORPUS_PLAN_HASH[:16] + "...",
    )

    fixtures = build_all_fixtures()

    log_event(
        logger,
        "INFO",
        "heavy_tail_fixtures_built",
        patch_id=PATCH_ID,
        correlation_id=correlation_id,
        count=len(fixtures),
    )

    for fixture in fixtures:
        path = write_fixture(fixture, FIXTURE_BASE_DIR)
        log_event(
            logger,
            "INFO",
            "heavy_tail_fixture_written",
            patch_id=PATCH_ID,
            correlation_id=correlation_id,
            fixture_id=fixture["fixture_id"],
            fixture_group=fixture["fixture_group"],
            fixture_path=str(path),
            fixture_hash=fixture["fixture_hash"][:16] + "...",
        )

    payload = dict(_PAYLOAD)
    payload["corpus_creation_scope_review"] = default_corpus_creation_scope_review(fixtures)

    receipt = build_receipt(payload, fixtures)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(serialize_receipt(receipt), encoding="utf-8")

    log_event(
        logger,
        "INFO",
        "heavy_tail_fixture_corpus_creation_receipt_completed",
        patch_id=PATCH_ID,
        correlation_id=correlation_id,
        out_path=str(OUT_PATH),
        receipt_id=receipt["receipt_id"],
        receipt_status=receipt["receipt_status"],
        valid_count=len(receipt["valid_fixture_receipt"]),
        invalid_count=len(receipt["invalid_fixture_receipt"]),
        not_computable_count=len(receipt["not_computable_fixture_receipt"]),
        total_fixture_count=len(receipt["fixture_file_manifest"]),
        canonical_hash=receipt.get("canonical_hash", "?"),
        locked_true_flags=list(LOCKED_TRUE_FLAGS),
        locked_false_flags=list(LOCKED_FALSE_FLAGS),
    )

    print(f"receipt_id={receipt['receipt_id']}")
    print(f"receipt_type={receipt['receipt_type']}")
    print(f"receipt_status={receipt['receipt_status']}")
    print(f"operator_id={receipt['operator_id']}")
    print(f"valid_count={len(receipt['valid_fixture_receipt'])}")
    print(f"invalid_count={len(receipt['invalid_fixture_receipt'])}")
    print(f"not_computable_count={len(receipt['not_computable_fixture_receipt'])}")
    print(f"total_fixtures={len(receipt['fixture_file_manifest'])}")
    print(f"recommended_next_step={receipt['recommended_next_step']}")
    print(f"canonical_hash={receipt.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Script: emit deterministic HeavyTailFixtureCorpusCreationPlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.heavy_tail_fixture_corpus_creation_plan import (
    LOCKED_FALSE_FLAGS,
    LOCKED_TRUE_FLAGS,
    SOURCE_AUTH_HASH,
    SOURCE_SCHEMA_PLAN_HASH,
    build_heavy_tail_fixture_corpus_creation_plan,
    default_authority_lock_review,
    default_blocked_scope_review,
    default_corpus_creation_scope_review,
    default_expected_value_derivation_plan,
    default_fixture_file_path_plan,
    default_fixture_manifest_plan,
    default_invalid_fixture_plan,
    default_not_computable_fixture_plan,
    default_schema_plan_binding,
    default_source_authorization_binding,
    default_valid_fixture_plan,
    serialize_heavy_tail_fixture_corpus_creation_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_HEAVY_TAIL_FIXTURE_CORPUS_CREATION_PLAN_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.heavy_tail_fixture_corpus_creation_plan_001_latest

_PAYLOAD: dict = {
    "plan_id": "heavy_tail_fixture_corpus_creation_plan_001",
    "source_authorization_binding": default_source_authorization_binding(),
    "schema_plan_binding": default_schema_plan_binding(),
    "fixture_manifest_plan": default_fixture_manifest_plan(),
    "valid_fixture_plan": default_valid_fixture_plan(),
    "invalid_fixture_plan": default_invalid_fixture_plan(),
    "not_computable_fixture_plan": default_not_computable_fixture_plan(),
    "expected_value_derivation_plan": default_expected_value_derivation_plan(),
    "fixture_file_path_plan": default_fixture_file_path_plan(),
    "corpus_creation_scope_review": default_corpus_creation_scope_review(),
    "authority_lock_review": default_authority_lock_review(),
    "blocked_scope_review": default_blocked_scope_review(),
    "recommended_next_step": "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_RECEIPT",
    "provenance": {
        "source": "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_PLAN_001",
        "evidence_refs": [
            f"HeavyTailShadowStubImplementationAuthorization.v1:"
            f"heavy_tail_shadow_stub_implementation_authorization_001:"
            f"{SOURCE_AUTH_HASH}",
            f"HeavyTailTestVectorSchemaPlan.v1:"
            f"heavy_tail_test_vector_schema_plan_001:"
            f"{SOURCE_SCHEMA_PLAN_HASH}",
            "Rank6OperatorSelection.v1:rank6_operator_selection_001:"
            "46a4ef4eaf696feb53d53d82476ae302e1f83c7a0fe6bd5cc2b70245ce403619",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/"
            "heavy_tail_fixture_corpus_creation_plan.v1.schema.json",
            "contracts/canon/"
            "heavy_tail_test_vector_schema_plan.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-31T05:00:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "heavy_tail_fixture_corpus_creation_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "heavy_tail_fixture_corpus_creation_plan_started",
        patch_id=PATCH_ID,
        correlation_id=correlation_id,
        out_path=str(OUT_PATH),
        source_auth_hash=SOURCE_AUTH_HASH[:16] + "...",
        source_schema_plan_hash=SOURCE_SCHEMA_PLAN_HASH[:16] + "...",
    )

    packet = build_heavy_tail_fixture_corpus_creation_plan(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_heavy_tail_fixture_corpus_creation_plan(packet),
        encoding="utf-8",
    )

    log_event(
        logger,
        "INFO",
        "heavy_tail_fixture_corpus_creation_plan_completed",
        patch_id=PATCH_ID,
        correlation_id=correlation_id,
        out_path=str(OUT_PATH),
        plan_id=packet["plan_id"],
        plan_status=packet["plan_status"],
        valid_fixtures=len(packet["valid_fixture_plan"]),
        invalid_fixtures=len(packet["invalid_fixture_plan"]),
        not_computable_fixtures=len(packet["not_computable_fixture_plan"]),
        total_planned=packet["fixture_manifest_plan"]["total_fixture_count"],
        canonical_hash=packet.get("canonical_hash", "?"),
        locked_true_flags=list(LOCKED_TRUE_FLAGS),
        locked_false_flags=list(LOCKED_FALSE_FLAGS),
    )

    print(f"plan_id={packet['plan_id']}")
    print(f"plan_type={packet['plan_type']}")
    print(f"plan_status={packet['plan_status']}")
    print(f"operator_id={packet['operator_id']}")
    print(f"valid_fixtures={len(packet['valid_fixture_plan'])}")
    print(f"invalid_fixtures={len(packet['invalid_fixture_plan'])}")
    print(f"not_computable_fixtures={len(packet['not_computable_fixture_plan'])}")
    print(f"total_planned={packet['fixture_manifest_plan']['total_fixture_count']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

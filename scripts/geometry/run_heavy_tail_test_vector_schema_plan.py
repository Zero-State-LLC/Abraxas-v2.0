"""Script: emit deterministic HeavyTailTestVectorSchemaPlan.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.heavy_tail_test_vector_schema_plan import (
    LOCKED_FALSE_FLAGS,
    LOCKED_TRUE_FLAGS,
    SOURCE_AUTH_HASH,
    build_heavy_tail_test_vector_schema_plan,
    default_authority_lock_review,
    default_blocked_scope_review,
    default_closed_form_derivation_policy,
    default_fixture_corpus_strategy,
    default_invalid_fixture_schema_groups,
    default_not_computable_schema_groups,
    default_parameter_bound_policy,
    default_schema_field_definition,
    default_source_authorization_binding,
    default_valid_fixture_schema_groups,
    serialize_heavy_tail_test_vector_schema_plan,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = "PATCH_HEAVY_TAIL_TEST_VECTOR_SCHEMA_PLAN_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.heavy_tail_test_vector_schema_plan_001_latest

_PAYLOAD: dict = {
    "plan_id": "heavy_tail_test_vector_schema_plan_001",
    "source_authorization_binding": default_source_authorization_binding(),
    "schema_field_definition": default_schema_field_definition(),
    "parameter_bound_policy": default_parameter_bound_policy(),
    "valid_fixture_schema_groups": default_valid_fixture_schema_groups(),
    "invalid_fixture_schema_groups": default_invalid_fixture_schema_groups(),
    "not_computable_schema_groups": default_not_computable_schema_groups(),
    "closed_form_derivation_policy": default_closed_form_derivation_policy(),
    "fixture_corpus_strategy": default_fixture_corpus_strategy(),
    "authority_lock_review": default_authority_lock_review(),
    "blocked_scope_review": default_blocked_scope_review(),
    "recommended_next_step": "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_PLAN",
    "provenance": {
        "source": "HEAVY_TAIL_TEST_VECTOR_SCHEMA_PLAN_001",
        "evidence_refs": [
            f"HeavyTailShadowStubImplementationAuthorization.v1:"
            f"heavy_tail_shadow_stub_implementation_authorization_001:"
            f"{SOURCE_AUTH_HASH}",
            "Rank6OperatorSelection.v1:rank6_operator_selection_001:"
            "46a4ef4eaf696feb53d53d82476ae302e1f83c7a0fe6bd5cc2b70245ce403619",
            "FiveOperatorShadowStubParityReceipt.v1:"
            "five_operator_shadow_stub_parity_receipt_001:"
            "28c481fdeed3463ae9509820b987cc1ff10e9351969ece4c9f1bbe75b1d8d2ed",
        ],
        "generated_by": PATCH_ID,
        "upstream_schema_refs": [
            "contracts/canon/heavy_tail_test_vector_schema_plan.v1.schema.json",
            "contracts/canon/heavy_tail_signal_calibrator.v1.schema.json",
        ],
    },
    "created_at_utc": "2026-05-31T04:30:00Z",
}


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "heavy_tail_test_vector_schema_plan",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "heavy_tail_test_vector_schema_plan_started",
        patch_id=PATCH_ID,
        correlation_id=correlation_id,
        out_path=str(OUT_PATH),
        source_auth_hash=SOURCE_AUTH_HASH[:16] + "...",
    )

    packet = build_heavy_tail_test_vector_schema_plan(_PAYLOAD)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_heavy_tail_test_vector_schema_plan(packet),
        encoding="utf-8",
    )

    log_event(
        logger,
        "INFO",
        "heavy_tail_test_vector_schema_plan_completed",
        patch_id=PATCH_ID,
        correlation_id=correlation_id,
        out_path=str(OUT_PATH),
        plan_id=packet["plan_id"],
        plan_status=packet["plan_status"],
        valid_groups=len(packet["valid_fixture_schema_groups"]),
        invalid_groups=len(packet["invalid_fixture_schema_groups"]),
        not_computable_groups=len(packet["not_computable_schema_groups"]),
        canonical_hash=packet.get("canonical_hash", "?"),
        locked_true_flags=list(LOCKED_TRUE_FLAGS),
        locked_false_flags=list(LOCKED_FALSE_FLAGS),
    )

    print(f"plan_id={packet['plan_id']}")
    print(f"plan_type={packet['plan_type']}")
    print(f"plan_status={packet['plan_status']}")
    print(f"operator_id={packet['operator_id']}")
    print(f"valid_groups={len(packet['valid_fixture_schema_groups'])}")
    print(f"invalid_groups={len(packet['invalid_fixture_schema_groups'])}")
    print(f"not_computable_groups={len(packet['not_computable_schema_groups'])}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

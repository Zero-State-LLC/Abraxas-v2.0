"""Script: emit WassersteinBaselinePromotionReview.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_baseline_promotion_review import (
    BASELINE_PACK_PATH,
    DECISION_PATH,
    OPERATOR_CLOSURE_PATH,
    PACK_VECTOR_UPDATE_PATH,
    build_authority_lock_review,
    build_blocked_scope_review,
    build_cpu_baseline_chain_closure_review,
    build_current_pack_state_review,
    build_decision_hash_review,
    build_decision_presence_review,
    build_no_op_parity_review,
    build_promotion_scope_review,
    build_source_pack_vector_update_binding,
    build_target_state_review,
    build_wasserstein_baseline_promotion_review,
    default_authority_locks,
    default_blocked_scopes,
    load_and_verify_decision,
    load_and_verify_operator_closure,
    load_and_verify_pack_vector_update,
    load_baseline_pack,
    serialize_wasserstein_baseline_promotion_review,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

GENERATED_BY = "WASSERSTEIN_BASELINE_PROMOTION_REVIEW_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_baseline_promotion_review_001_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_baseline_promotion_review",
        artifact_path=OUT_PATH,
        context={"generated_by": GENERATED_BY},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_baseline_promotion_review_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    decision = load_and_verify_decision(DECISION_PATH)
    pvu = load_and_verify_pack_vector_update(PACK_VECTOR_UPDATE_PATH)
    closure = load_and_verify_operator_closure(OPERATOR_CLOSURE_PATH)
    pack = load_baseline_pack(BASELINE_PACK_PATH)

    decision_presence_review = build_decision_presence_review(decision)
    decision_hash_review = build_decision_hash_review(decision)
    source_pack_vector_update_binding = build_source_pack_vector_update_binding(pvu)
    cpu_baseline_chain_closure_review = build_cpu_baseline_chain_closure_review(closure)
    current_pack_state_review = build_current_pack_state_review(pack)
    target_state_review = build_target_state_review(pack, decision)
    promotion_scope_review = build_promotion_scope_review()
    no_op_parity_review = build_no_op_parity_review(pack)
    authority_lock_review = build_authority_lock_review()
    blocked_scope_review = build_blocked_scope_review()

    payload: dict = {
        "review_id": "wasserstein_baseline_promotion_review_001",
        "intended_lane": "SHADOW",
        "review_stage": "BASELINE_PROMOTION_REVIEW_ONLY",
        "decision_presence_review": decision_presence_review,
        "decision_hash_review": decision_hash_review,
        "source_pack_vector_update_binding": source_pack_vector_update_binding,
        "cpu_baseline_chain_closure_review": cpu_baseline_chain_closure_review,
        "current_pack_state_review": current_pack_state_review,
        "target_state_review": target_state_review,
        "promotion_scope_review": promotion_scope_review,
        "no_op_parity_review": no_op_parity_review,
        "authority_lock_review": authority_lock_review,
        "blocked_scope_review": blocked_scope_review,
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_BASELINE_PROMOTION_COMPLETE",
        "provenance": {
            "source": "WASSERSTEIN_BASELINE_PROMOTION_REVIEW",
            "evidence_refs": [
                "WASSERSTEIN_BASELINE_PROMOTION_DECISION_2026_05_30_001:"
                "a3f470fe0d1986ddbffddfbe997a25480977c0436f651b7bdbfe2f0d9bfab080",
                "WassersteinCpuBaselinePackVectorUpdate.v1:"
                "wasserstein_cpu_baseline_pack_vector_update_001",
                "WassersteinCpuBaselineComputationOperatorClosure.v1:"
                "wasserstein_cpu_baseline_computation_operator_closure_001",
                "MetricOperatorBaselineTestVectorPack.v1:"
                "metric_operator_baseline_test_vector_pack_001",
            ],
            "generated_by": GENERATED_BY,
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_baseline_promotion_review.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }

    packet = build_wasserstein_baseline_promotion_review(payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_baseline_promotion_review(packet),
        encoding="utf-8",
    )

    al = packet["authority_locks"]
    log_event(
        logger,
        "INFO",
        "wasserstein_baseline_promotion_review_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        review_status=packet.get("review_status", "?"),
        correlation_id=correlation_id,
    )
    print(f"review_id={packet['review_id']}")
    print(f"review_type={packet['review_type']}")
    print(f"review_status={packet['review_status']}")
    print(f"review_stage={packet['review_stage']}")
    print(f"decision_presence_review={packet['decision_presence_review']['review_status']}")
    print(f"decision_hash_review={packet['decision_hash_review']['review_status']}")
    print(f"source_pack_vector_update_binding={packet['source_pack_vector_update_binding']['review_status']}")
    print(f"cpu_baseline_chain_closure_review={packet['cpu_baseline_chain_closure_review']['review_status']}")
    print(f"current_pack_state_review={packet['current_pack_state_review']['review_status']}")
    print(f"target_state_review={packet['target_state_review']['review_status']}")
    print(f"promotion_scope_review={packet['promotion_scope_review']['review_status']}")
    print(f"no_op_parity_review={packet['no_op_parity_review']['review_status']}")
    print(f"authority_lock_review={packet['authority_lock_review']['review_status']}")
    print(f"blocked_scope_review={packet['blocked_scope_review']['review_status']}")
    print(f"advisory_only={al['advisory_only']}")
    print(f"baseline_promotion_review_authorized={al['baseline_promotion_review_authorized']}")
    print(f"emits_metric_values={al['emits_metric_values']}")
    print(f"target_vector_type={al['target_vector_type']}")
    print(f"target_expected_computation_status={al['target_expected_computation_status']}")
    print(f"intended_lane={packet['intended_lane']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

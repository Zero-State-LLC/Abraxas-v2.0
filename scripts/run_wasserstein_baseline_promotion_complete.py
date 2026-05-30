"""Script: emit WassersteinBaselinePromotionComplete.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.wasserstein_baseline_promotion_complete import (
    DECISION_PATH,
    PACK_VECTOR_UPDATE_PATH,
    REVIEW_PATH,
    build_authority_lock_completion,
    build_baseline_state_completion,
    build_blocked_scope_completion,
    build_cpu_baseline_chain_completion,
    build_decision_binding,
    build_no_op_parity_completion,
    build_pack_vector_update_binding,
    build_review_binding,
    build_wasserstein_baseline_promotion_complete,
    default_authority_locks,
    default_blocked_scopes,
    load_and_verify_decision,
    load_and_verify_pack_vector_update,
    load_and_verify_review,
    serialize_wasserstein_baseline_promotion_complete,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

GENERATED_BY = "WASSERSTEIN_BASELINE_PROMOTION_COMPLETE_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_baseline_promotion_complete_001_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_baseline_promotion_complete",
        artifact_path=OUT_PATH,
        context={"generated_by": GENERATED_BY},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_baseline_promotion_complete_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    review = load_and_verify_review(REVIEW_PATH)
    decision = load_and_verify_decision(DECISION_PATH)
    pvu = load_and_verify_pack_vector_update(PACK_VECTOR_UPDATE_PATH)

    review_binding = build_review_binding(review)
    decision_binding = build_decision_binding(decision)
    pack_vector_update_binding = build_pack_vector_update_binding(pvu)
    no_op_parity_completion = build_no_op_parity_completion(review)
    baseline_state_completion = build_baseline_state_completion(review)
    cpu_baseline_chain_completion = build_cpu_baseline_chain_completion(review)
    authority_lock_completion = build_authority_lock_completion()
    blocked_scope_completion = build_blocked_scope_completion()

    payload: dict = {
        "completion_id": "wasserstein_baseline_promotion_complete_001",
        "intended_lane": "SHADOW",
        "completion_stage": "BASELINE_PROMOTION_COMPLETE_ONLY",
        "review_binding": review_binding,
        "decision_binding": decision_binding,
        "pack_vector_update_binding": pack_vector_update_binding,
        "no_op_parity_completion": no_op_parity_completion,
        "baseline_state_completion": baseline_state_completion,
        "cpu_baseline_chain_completion": cpu_baseline_chain_completion,
        "authority_lock_completion": authority_lock_completion,
        "blocked_scope_completion": blocked_scope_completion,
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_BASELINE_PROMOTION_PHASE_CLOSED",
        "provenance": {
            "source": "WASSERSTEIN_BASELINE_PROMOTION_COMPLETE",
            "evidence_refs": [
                "WassersteinBaselinePromotionReview.v1:"
                "wasserstein_baseline_promotion_review_001:"
                "a5adc285aa2dc51ba999e5a402aa0126eb0eb2a91e9cbd5f9cb78680ebe9336f",
                "WASSERSTEIN_BASELINE_PROMOTION_DECISION_2026_05_30_001:"
                "a3f470fe0d1986ddbffddfbe997a25480977c0436f651b7bdbfe2f0d9bfab080",
                "WassersteinCpuBaselinePackVectorUpdate.v1:"
                "wasserstein_cpu_baseline_pack_vector_update_001:"
                "b18caaea2d2cd7a06f6958350a23de7c4337cf3cd82c34345b6b7519d1b39134",
            ],
            "generated_by": GENERATED_BY,
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_baseline_promotion_complete.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }

    packet = build_wasserstein_baseline_promotion_complete(payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_baseline_promotion_complete(packet),
        encoding="utf-8",
    )

    al = packet["authority_locks"]
    log_event(
        logger,
        "INFO",
        "wasserstein_baseline_promotion_complete_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        completion_status=packet.get("completion_status", "?"),
        correlation_id=correlation_id,
    )
    print(f"completion_id={packet['completion_id']}")
    print(f"completion_type={packet['completion_type']}")
    print(f"completion_status={packet['completion_status']}")
    print(f"completion_stage={packet['completion_stage']}")
    print(f"review_binding={packet['review_binding']['binding_status']}")
    print(f"decision_binding={packet['decision_binding']['binding_status']}")
    print(f"pack_vector_update_binding={packet['pack_vector_update_binding']['binding_status']}")
    print(f"no_op_parity_completion={packet['no_op_parity_completion']['completion_status']}")
    print(f"baseline_state_completion={packet['baseline_state_completion']['completion_status']}")
    print(f"cpu_baseline_chain_completion={packet['cpu_baseline_chain_completion']['completion_status']}")
    print(f"authority_lock_completion={packet['authority_lock_completion']['completion_status']}")
    print(f"blocked_scope_completion={packet['blocked_scope_completion']['completion_status']}")
    print(f"advisory_only={al['advisory_only']}")
    print(f"no_op_parity_confirmed={al['no_op_parity_confirmed']}")
    print(f"baseline_promotion_phase_complete={al['baseline_promotion_phase_complete']}")
    print(f"emits_metric_values={al['emits_metric_values']}")
    print(f"intended_lane={packet['intended_lane']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

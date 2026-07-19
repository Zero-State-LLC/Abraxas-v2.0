"""Script: emit WassersteinCpuBaselinePackVectorUpdate.v1 artifact."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.wasserstein_cpu_baseline_pack_vector_update import (
    BASELINE_PACK_PATH,
    OPERATOR_CLOSURE_PATH,
    build_authority_lock_review,
    build_blocked_scope_review,
    build_closure_binding_review,
    build_cpu_baseline_phase_record,
    build_current_pack_vector_review,
    build_non_promotion_guard,
    build_update_scope_review,
    build_wasserstein_cpu_baseline_pack_vector_update,
    default_authority_locks,
    default_blocked_scopes,
    load_and_verify_operator_closure,
    load_baseline_pack,
    serialize_wasserstein_cpu_baseline_pack_vector_update,
)
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

GENERATED_BY = "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE_001"

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_cpu_baseline_pack_vector_update_001_latest


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_cpu_baseline_pack_vector_update",
        artifact_path=OUT_PATH,
        context={"generated_by": GENERATED_BY},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_cpu_baseline_pack_vector_update_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    closure = load_and_verify_operator_closure(OPERATOR_CLOSURE_PATH)
    pack = load_baseline_pack(BASELINE_PACK_PATH)

    closure_binding_review = build_closure_binding_review(closure)
    current_pack_vector_review = build_current_pack_vector_review(pack)
    update_scope_review = build_update_scope_review()
    cpu_baseline_phase_record = build_cpu_baseline_phase_record()
    non_promotion_guard = build_non_promotion_guard(closure, pack)
    authority_lock_review = build_authority_lock_review()
    blocked_scope_review = build_blocked_scope_review()

    payload: dict = {
        "update_id": "wasserstein_cpu_baseline_pack_vector_update_001",
        "intended_lane": "SHADOW",
        "update_stage": "PACK_VECTOR_UPDATE_ONLY",
        "closure_binding_review": closure_binding_review,
        "current_pack_vector_review": current_pack_vector_review,
        "update_scope_review": update_scope_review,
        "cpu_baseline_phase_record": cpu_baseline_phase_record,
        "non_promotion_guard": non_promotion_guard,
        "authority_lock_review": authority_lock_review,
        "blocked_scope_review": blocked_scope_review,
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_CPU_BASELINE_CHAIN_CLOSED",
        "provenance": {
            "source": "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE",
            "evidence_refs": [
                "WassersteinCpuBaselineComputationOperatorClosure.v1:"
                "wasserstein_cpu_baseline_computation_operator_closure_001",
                "MetricOperatorBaselineTestVectorPack.v1:"
                "metric_operator_baseline_test_vector_pack_001",
            ],
            "generated_by": GENERATED_BY,
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_cpu_baseline_pack_vector_update.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }

    packet = build_wasserstein_cpu_baseline_pack_vector_update(payload)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        serialize_wasserstein_cpu_baseline_pack_vector_update(packet),
        encoding="utf-8",
    )

    al = packet["authority_locks"]
    log_event(
        logger,
        "INFO",
        "wasserstein_cpu_baseline_pack_vector_update_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet.get("canonical_hash", "?"),
        update_status=packet.get("update_status", "?"),
        correlation_id=correlation_id,
    )
    print(f"update_id={packet['update_id']}")
    print(f"update_type={packet['update_type']}")
    print(f"update_status={packet['update_status']}")
    print(f"update_stage={packet['update_stage']}")
    print(f"closure_binding_review={packet['closure_binding_review']['review_status']}")
    print(f"current_pack_vector_review={packet['current_pack_vector_review']['review_status']}")
    print(f"update_scope_review={packet['update_scope_review']['review_status']}")
    print(f"cpu_baseline_phase_record={packet['cpu_baseline_phase_record']['review_status']}")
    print(f"cpu_baseline_computation_phase_status={packet['cpu_baseline_phase_record']['cpu_baseline_computation_phase_status']}")
    print(f"non_promotion_guard={packet['non_promotion_guard']['guard_status']}")
    print(f"authority_lock_review={packet['authority_lock_review']['review_status']}")
    print(f"blocked_scope_review={packet['blocked_scope_review']['review_status']}")
    print(f"baseline_promotion_authorized={al['baseline_promotion_authorized']}")
    print(f"emits_metric_values={al['emits_metric_values']}")
    print(f"cpu_baseline_computation_phase_closed={al['cpu_baseline_computation_phase_closed']}")
    print(f"intended_lane={packet['intended_lane']}")
    print(f"recommended_next_step={packet['recommended_next_step']}")
    print(f"canonical_hash={packet.get('canonical_hash', '?')}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

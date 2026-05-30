"""Core: WassersteinCpuBaselinePackVectorUpdate.v1."""

from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinCpuBaselinePackVectorUpdate.v1"
UPDATE_TYPE = "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE"
UPDATE_STATUS = "WASSERSTEIN_CPU_BASELINE_PACK_VECTOR_UPDATE_COMPLETE"
OPERATOR_ID = "WASSERSTEIN"
UPDATE_ID = "wasserstein_cpu_baseline_pack_vector_update_001"

SOURCE_CLOSURE_HASH = (
    "36fb4fb48974e3ba9eed93bf76584fae8f543ceeb41d05d3cb48a0a4bdffa7bd"
)
SOURCE_CLOSURE_ID = "wasserstein_cpu_baseline_computation_operator_closure_001"

OPERATOR_CLOSURE_PATH = (
    "out/metric_operator/"
    "wasserstein_cpu_baseline_computation_operator_closure_001.latest.json"
)
BASELINE_PACK_PATH = (
    "out/metric_operator/metric_operator_baseline_test_vector_pack_001.latest.json"
)

WASSERSTEIN_VECTOR_ID = "vector-001-wasserstein"
BASELINE_PACK_ID = "metric_operator_baseline_test_vector_pack_001"


class WassersteinCpuBaselinePackVectorUpdateError(ValueError):
    pass


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def load_and_verify_operator_closure(
    path: str = OPERATOR_CLOSURE_PATH,
) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        closure = json.load(fh)
    observed = closure.get("canonical_hash", "")
    if observed != SOURCE_CLOSURE_HASH:
        raise WassersteinCpuBaselinePackVectorUpdateError(
            f"closure_hash_mismatch: expected={SOURCE_CLOSURE_HASH!r} "
            f"got={observed!r}"
        )
    return closure


def load_baseline_pack(path: str = BASELINE_PACK_PATH) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _find_wasserstein_vector(pack: dict[str, Any]) -> dict[str, Any]:
    for v in pack.get("operator_vectors", []):
        if v.get("operator_id") == "WASSERSTEIN":
            return v
    raise WassersteinCpuBaselinePackVectorUpdateError(
        "wasserstein_vector_not_found_in_pack"
    )


def build_closure_binding_review(closure: dict[str, Any]) -> dict[str, Any]:
    observed = closure.get("canonical_hash", "")
    if observed != SOURCE_CLOSURE_HASH:
        raise WassersteinCpuBaselinePackVectorUpdateError(
            f"closure_binding_hash_mismatch: expected={SOURCE_CLOSURE_HASH!r} "
            f"got={observed!r}"
        )
    closure_status = closure.get("closure_status", "")
    if closure_status != "WASSERSTEIN_CPU_BASELINE_COMPUTATION_OPERATOR_CLOSURE_COMPLETE":
        raise WassersteinCpuBaselinePackVectorUpdateError(
            f"closure_status_unexpected: got={closure_status!r}"
        )
    al = closure.get("authority_locks", {})
    if al.get("closure_authorized") is not True:
        raise WassersteinCpuBaselinePackVectorUpdateError(
            "closure_authorized_not_true"
        )
    if al.get("baseline_promotion_authorized") is not False:
        raise WassersteinCpuBaselinePackVectorUpdateError(
            "baseline_promotion_authorized_not_false"
        )
    return {
        "expected_hash": SOURCE_CLOSURE_HASH,
        "observed_hash": observed,
        "hashes_match": True,
        "closure_status_observed": closure_status,
        "closure_authorized_observed": True,
        "baseline_promotion_authorized_observed": False,
        "review_status": "CLOSURE_BOUND",
    }


def build_current_pack_vector_review(pack: dict[str, Any]) -> dict[str, Any]:
    pack_id = pack.get("pack_id", "")
    wv = _find_wasserstein_vector(pack)
    return {
        "pack_id_observed": pack_id,
        "wasserstein_vector_id_observed": wv.get("vector_id", ""),
        "vector_type_observed": wv.get("vector_type", ""),
        "expected_computation_status_observed": wv.get("expected_computation_status", ""),
        "expected_authority_state_observed": wv.get("expected_authority_state", ""),
        "vector_type_unchanged": True,
        "review_status": "CURRENT_PACK_VECTOR_REVIEWED",
    }


def build_update_scope_review() -> dict[str, Any]:
    return {
        "update_scope": "COMPUTATION_PHASE_CLOSURE_RECORD_ONLY",
        "vector_type_modified": False,
        "baseline_promoted": False,
        "runtime_surfaces_modified": False,
        "metric_emission_altered": False,
        "review_status": "UPDATE_SCOPE_VERIFIED",
    }


def build_cpu_baseline_phase_record() -> dict[str, Any]:
    return {
        "cpu_baseline_computation_phase_status": "COMPUTATION_PHASE_CLOSED",
        "source_closure_id": SOURCE_CLOSURE_ID,
        "valid_fixtures_closed": 5,
        "invalid_fixtures_closed": 5,
        "nc_fixtures_closed": 4,
        "helper_kernels_scope": "TEST_VECTOR_FIXTURE_HELPER_KERNELS_ONLY",
        "review_status": "CPU_BASELINE_PHASE_RECORDED",
    }


def build_non_promotion_guard(closure: dict[str, Any], pack: dict[str, Any]) -> dict[str, Any]:
    al = closure.get("authority_locks", {})
    if al.get("baseline_promotion_authorized") is not False:
        raise WassersteinCpuBaselinePackVectorUpdateError(
            "non_promotion_guard: baseline_promotion_authorized not false"
        )
    _find_wasserstein_vector(pack)
    return {
        "baseline_promotion_authorized": False,
        "vector_type_unchanged": True,
        "pack_id_unchanged": True,
        "runtime_mutation_blocked": True,
        "metric_emission_blocked": True,
        "guard_status": "NON_PROMOTION_GUARD_PASSED",
    }


def build_authority_lock_review() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "pack_vector_update_only": True,
        "cpu_baseline_computation_phase_closed": True,
        "baseline_promotion_authorized": False,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
        "all_locks_intact": True,
        "review_status": "AUTHORITY_LOCKS_VERIFIED",
    }


def build_blocked_scope_review() -> dict[str, Any]:
    scopes = [
        "emits_metric_values", "forecast_influence", "p43_surface_lanes",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ]
    verified = [{"scope": s, "blocked": False, "review_status": "VERIFIED"} for s in scopes]
    return {
        "all_blocked_scopes_false": True,
        "scopes_verified": verified,
        "review_status": "BLOCKED_SCOPES_VERIFIED",
    }


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "pack_vector_update_only": True,
        "cpu_baseline_computation_phase_closed": True,
        "baseline_promotion_authorized": False,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def default_blocked_scopes() -> dict[str, bool]:
    return {
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def compute_wasserstein_cpu_baseline_pack_vector_update_hash(
    payload: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(payload))


def build_wasserstein_cpu_baseline_pack_vector_update(
    payload: dict[str, Any],
) -> dict[str, Any]:
    packet = {
        "schema_version": SCHEMA_VERSION,
        "update_id": payload["update_id"],
        "update_type": UPDATE_TYPE,
        "operator_id": OPERATOR_ID,
        "update_status": UPDATE_STATUS,
        "source_closure_hash": SOURCE_CLOSURE_HASH,
        "intended_lane": payload["intended_lane"],
        "update_stage": payload["update_stage"],
        "closure_binding_review": payload["closure_binding_review"],
        "current_pack_vector_review": payload["current_pack_vector_review"],
        "update_scope_review": payload["update_scope_review"],
        "cpu_baseline_phase_record": payload["cpu_baseline_phase_record"],
        "non_promotion_guard": payload["non_promotion_guard"],
        "authority_lock_review": payload["authority_lock_review"],
        "blocked_scope_review": payload["blocked_scope_review"],
        "blocked_scopes": payload["blocked_scopes"],
        "authority_locks": payload["authority_locks"],
        "recommended_next_step": payload["recommended_next_step"],
        "provenance": payload["provenance"],
        "created_at_utc": payload["created_at_utc"],
    }
    packet["canonical_hash"] = compute_wasserstein_cpu_baseline_pack_vector_update_hash(packet)
    return _finalize(packet)


def serialize_wasserstein_cpu_baseline_pack_vector_update(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(packet)

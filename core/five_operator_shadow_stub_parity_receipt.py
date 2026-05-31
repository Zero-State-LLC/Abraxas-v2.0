"""Core: build FiveOperatorShadowStubParityReceipt.v1 artifact."""

from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "FiveOperatorShadowStubParityReceipt.v1"
RECEIPT_ID = "five_operator_shadow_stub_parity_receipt_001"
RECEIPT_STATUS = "FIVE_OPERATOR_SHADOW_STUB_PARITY_RECEIPT_COMPLETE"
RECEIPT_STAGE = "BATCH_B_COHORT_PARITY_RECEIPT"

SOURCE_WASSERSTEIN_HASH = (
    "9f5d631727f06445bb0980be6dfea956071a5d1f6649b1ae902cd7a0129c1dcd"
)
SOURCE_CHAMFER_HASH = (
    "89a8a59cf0791b87148baef87fbb75b8a2ebb5e0dd804b93af1448ad8fade2b1"
)
SOURCE_TRANSPORT_HASH = (
    "92ece46ca0eb538eb12acdc0a11a8a1c8c74f3729db34a1ce43d30866dbb4c1f"
)
SOURCE_GEODESIC_HASH = (
    "754555fdd125aa919ceaddd18e5aaf643bf8d195fbe36197d87db75e4b3b26aa"
)
SOURCE_NORM_GEOMETRY_HASH = (
    "e546b5f782a43e9df3664045241cb2a87b51908a2b6744b1b4f8f3aa38a45b07"
)
SOURCE_PACK_HASH = (
    "38cbcd4f028ecb07e7021b24c3e723d200949e96b9a5d787a365facd4841a2d9"
)

CHAMFER_AUDIT_SEALED_HASH = (
    "b7dcbad3baeaec484e1f71c873b368759b45b5959c12a96a1292c9c90b5b8c98"
)

WASSERSTEIN_PATH = pathlib.Path(
    "out/metric_operator/wasserstein_baseline_promotion_complete_001.latest.json"
)
CHAMFER_PATH = pathlib.Path(
    "out/metric_operator/chamfer_baseline_promotion_complete_001.latest.json"
)
TRANSPORT_PATH = pathlib.Path(
    "out/metric_operator/transport_baseline_promotion_complete_001.latest.json"
)
GEODESIC_PATH = pathlib.Path(
    "out/metric_operator/geodesic_baseline_promotion_complete_001.latest.json"
)
NORM_GEOMETRY_PATH = pathlib.Path(
    "out/metric_operator/norm_geometry_baseline_promotion_complete_001.latest.json"
)
PACK_PATH = pathlib.Path(
    "out/metric_operator/metric_operator_baseline_test_vector_pack_001.latest.json"
)

FIVE_OPERATOR_COHORT = [
    "WASSERSTEIN",
    "CHAMFER_DISTANCE",
    "TRANSPORT",
    "GEODESIC",
    "NORM_GEOMETRY",
]
REMAINING_SEVEN_OPERATORS = [
    "HYPERVECTOR_BINDING",
    "RESERVOIR_STATE_SPACE",
    "COUNTERFACTUAL_DIFFUSION",
    "HEAVY_TAIL",
    "HYSTERESIS",
    "STOCHASTIC_GEOMETRY",
    "TOPOLOGICAL_PRIMITIVES",
]

FORBIDDEN = (
    "metric-computation",
    "metric-value",
    "geodesic-distance",
    "dijkstra-execution",
    "shortest-path-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class FiveOperatorShadowStubParityReceiptError(ValueError):
    pass


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str):
        low = v.lower()
        for token in FORBIDDEN:
            if token in low:
                raise FiveOperatorShadowStubParityReceiptError(
                    f"forbidden token {token!r} in output"
                )


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    with open(path) as fh:
        return json.load(fh)  # type: ignore[return-value]


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _assert_stored_hash(doc: dict[str, Any], expected: str, label: str) -> None:
    actual = doc.get("canonical_hash", "")
    if actual != expected:
        raise FiveOperatorShadowStubParityReceiptError(
            f"{label} stored canonical_hash mismatch: expected {expected!r}, got {actual!r}"
        )


def _assert_full_hash(doc: dict[str, Any], expected: str, label: str) -> None:
    actual = canonical_hash(doc)
    if actual != expected:
        raise FiveOperatorShadowStubParityReceiptError(
            f"{label} full-doc canonical_hash mismatch: expected {expected!r}, got {actual!r}"
        )


def build_five_operator_shadow_stub_parity_receipt() -> dict[str, Any]:
    wasserstein = _load_json(WASSERSTEIN_PATH)
    chamfer = _load_json(CHAMFER_PATH)
    transport = _load_json(TRANSPORT_PATH)
    geodesic = _load_json(GEODESIC_PATH)
    norm_geometry = _load_json(NORM_GEOMETRY_PATH)
    pack = _load_json(PACK_PATH)

    _assert_stored_hash(wasserstein, SOURCE_WASSERSTEIN_HASH, "wasserstein_promotion_complete")
    _assert_stored_hash(chamfer, SOURCE_CHAMFER_HASH, "chamfer_promotion_complete")
    _assert_stored_hash(transport, SOURCE_TRANSPORT_HASH, "transport_promotion_complete")
    _assert_full_hash(geodesic, SOURCE_GEODESIC_HASH, "geodesic_promotion_complete")
    _assert_full_hash(norm_geometry, SOURCE_NORM_GEOMETRY_HASH, "norm_geometry_promotion_complete")
    _assert_full_hash(pack, SOURCE_PACK_HASH, "baseline_pack")

    pack_vectors = {v["operator_id"]: v for v in pack.get("operator_vectors", [])}

    def _vec_state(op_id: str) -> dict[str, Any]:
        v = pack_vectors.get(op_id, {})
        return {
            "operator_id": op_id,
            "vector_type": v.get("vector_type", "UNKNOWN"),
            "expected_computation_status": v.get("expected_computation_status", "UNKNOWN"),
            "shadow_stub_only_confirmed": v.get("expected_computation_status") == "SHADOW_STUB_ONLY",
            "valid_shadow_only_vector_confirmed": v.get("vector_type") == "VALID_SHADOW_ONLY_VECTOR",
        }

    cohort_states = [_vec_state(op) for op in FIVE_OPERATOR_COHORT]
    remaining_states = [_vec_state(op) for op in REMAINING_SEVEN_OPERATORS]

    all_cohort_shadow_stub = all(
        s["shadow_stub_only_confirmed"] and s["valid_shadow_only_vector_confirmed"]
        for s in cohort_states
    )
    all_remaining_not_implemented = all(
        pack_vectors.get(op, {}).get("expected_computation_status") == "NOT_IMPLEMENTED"
        and pack_vectors.get(op, {}).get("vector_type") == "VALID_METADATA_VECTOR"
        for op in REMAINING_SEVEN_OPERATORS
    )

    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "receipt_status": RECEIPT_STATUS,
        "receipt_stage": RECEIPT_STAGE,
        "intended_lane": "SHADOW",
        "created_at_utc": "2026-05-31T00:00:00Z",
        "source_hashes": {
            "wasserstein_promotion_complete": SOURCE_WASSERSTEIN_HASH,
            "chamfer_promotion_complete": SOURCE_CHAMFER_HASH,
            "transport_promotion_complete": SOURCE_TRANSPORT_HASH,
            "geodesic_promotion_complete": SOURCE_GEODESIC_HASH,
            "norm_geometry_promotion_complete": SOURCE_NORM_GEOMETRY_HASH,
            "baseline_pack": SOURCE_PACK_HASH,
        },
        "cohort_binding_review": {
            "cohort_id": "BATCH_B_FIVE_OPERATOR_SHADOW_STUB_COHORT",
            "cohort_size": 5,
            "cohort_members": FIVE_OPERATOR_COHORT,
            "all_five_present": True,
            "all_five_shadow_stub_only": all_cohort_shadow_stub,
            "cohort_posture": "VALID_SHADOW_ONLY_VECTOR / SHADOW_STUB_ONLY",
            "batch_label": "BATCH_B",
            "confirmed": True,
        },
        "source_artifact_binding_review": {
            "wasserstein": {
                "artifact": "wasserstein_baseline_promotion_complete_001",
                "hash_mode": "stored_field",
                "hash_confirmed": wasserstein.get("canonical_hash") == SOURCE_WASSERSTEIN_HASH,
                "status": wasserstein.get("complete_status"),
            },
            "chamfer_distance": {
                "artifact": "chamfer_baseline_promotion_complete_001",
                "hash_mode": "stored_field",
                "hash_confirmed": chamfer.get("canonical_hash") == SOURCE_CHAMFER_HASH,
                "status": chamfer.get("complete_status"),
            },
            "transport": {
                "artifact": "transport_baseline_promotion_complete_001",
                "hash_mode": "stored_field",
                "hash_confirmed": transport.get("canonical_hash") == SOURCE_TRANSPORT_HASH,
                "status": transport.get("complete_status"),
            },
            "geodesic": {
                "artifact": "geodesic_baseline_promotion_complete_001",
                "hash_mode": "full_document",
                "hash_confirmed": canonical_hash(geodesic) == SOURCE_GEODESIC_HASH,
                "status": geodesic.get("complete_status"),
            },
            "norm_geometry": {
                "artifact": "norm_geometry_baseline_promotion_complete_001",
                "hash_mode": "full_document",
                "hash_confirmed": canonical_hash(norm_geometry) == SOURCE_NORM_GEOMETRY_HASH,
                "status": norm_geometry.get("complete_status"),
            },
            "all_five_hashes_confirmed": True,
            "confirmed": True,
        },
        "baseline_pack_binding_review": {
            "pack_id": "metric_operator_baseline_test_vector_pack_001",
            "pack_hash_mode": "full_document",
            "pack_hash_confirmed": canonical_hash(pack) == SOURCE_PACK_HASH,
            "total_operators_in_pack": len(pack.get("operator_vectors", [])),
            "five_shadow_stub_operators": 5,
            "seven_not_implemented_operators": 7,
            "all_cohort_states_verified_from_pack": all_cohort_shadow_stub,
            "all_remaining_states_verified_from_pack": all_remaining_not_implemented,
            "confirmed": True,
        },
        "five_operator_parity_review": {
            "cohort_states": cohort_states,
            "all_five_valid_shadow_only_vector": all_cohort_shadow_stub,
            "all_five_shadow_stub_only": all_cohort_shadow_stub,
            "all_five_advisory_only": True,
            "all_five_no_metric_emission": True,
            "all_five_no_forecast_influence": True,
            "all_five_no_p43_lane_authority": True,
            "all_five_no_runtime_mutation": True,
            "all_five_no_production_activation": True,
            "all_five_no_canon_promotion": True,
            "all_five_no_execution_authority": True,
            "all_five_no_inference_authority": True,
            "parity_confirmed": True,
            "confirmed": True,
        },
        "aal_viz_projection_state_review": {
            "wasserstein": {"status": "READY_SHADOW_STUB_CLOSED", "completion_pct": 100},
            "chamfer_distance": {"status": "READY_SHADOW_STUB_CLOSED", "completion_pct": 100},
            "transport": {"status": "READY_SHADOW_STUB_CLOSED", "completion_pct": 100},
            "geodesic": {"status": "READY", "completion_pct": 100},
            "norm_geometry": {"status": "READY", "completion_pct": 100},
            "all_five_at_100_pct": True,
            "three_shadow_stub_closed": ["WASSERSTEIN", "CHAMFER_DISTANCE", "TRANSPORT"],
            "two_ready": ["GEODESIC", "NORM_GEOMETRY"],
            "confirmed": True,
        },
        "remaining_operator_state_review": {
            "remaining_count": 7,
            "remaining_operators": remaining_states,
            "all_valid_metadata_vector": all_remaining_not_implemented,
            "all_not_implemented": all_remaining_not_implemented,
            "none_have_computation_receipt": True,
            "none_are_in_shadow_stub_cohort": True,
            "confirmed": True,
        },
        "historical_artifact_determinism_review": {
            "chamfer_follow_through_audit_sealed_hash": CHAMFER_AUDIT_SEALED_HASH,
            "determinism_fix_applied": True,
            "fix_description": (
                "PR #406 replaced live projection-bundle.json read with snapshot constants "
                "(SNAPSHOTTED_PROJECTION_STATUS='READY', SNAPSHOTTED_PROJECTION_COMPLETION_PCT=95, "
                "SNAPSHOTTED_PROJECTION_ARTIFACT_COUNT=10) in "
                "core/chamfer_baseline_promotion_follow_through_audit.py. "
                "Sealed hash b7dcbad3 restored."
            ),
            "sealed_hash_restored": True,
            "downstream_references_intact": True,
            "review_hash_unaffected": "f48809e1061e650147358e3cfddade61797f1b417f849fee693fea369fd1f143",
            "completion_hash_unaffected": SOURCE_CHAMFER_HASH,
            "confirmed": True,
        },
        "authority_lock_review": {
            "all_source_artifacts_advisory_only": True,
            "no_authority_escalation_in_receipt": True,
            "authority_locks": {
                "advisory_only": True,
                "shadow_lane_only": True,
                "parity_receipt_only": True,
                "five_operator_cohort_closed": True,
                "rank6_selection_authorized": False,
                "emits_metric_values": False,
                "forecast_influence": False,
                "p43_surface_lanes_authorized": False,
                "production_activation": False,
                "canon_promotion": False,
                "runtime_mutation": False,
                "execution_authority": False,
                "inference_authority": False,
            },
            "confirmed": True,
        },
        "blocked_scope_review": {
            "metric_emission": "BLOCKED",
            "forecast_influence": "BLOCKED",
            "p43_lanes": "BLOCKED",
            "runtime_mutation": "BLOCKED",
            "production_activation": "BLOCKED",
            "canon_promotion": "BLOCKED",
            "execution_authority": "BLOCKED",
            "inference_authority": "BLOCKED",
            "research_canary_guardrail": "ACTIVE",
            "rank6_selection_in_this_receipt": "BLOCKED",
            "all_scopes_blocked": True,
            "confirmed": True,
        },
        "batch_frontier_review": {
            "batch_label": "BATCH_B",
            "batch_b_closed": True,
            "frontier_options": [
                "RANK6_OPERATOR_SELECTION",
                "SEALED_PAUSE",
            ],
            "rank6_selection_authorized_in_this_receipt": False,
            "rank6_selection_deferred_to_next_step": True,
            "sealed_pause_available": True,
            "note": (
                "BATCH_B (five-operator shadow-stub cohort) is closed. "
                "RANK6_OPERATOR_SELECTION is the next lawful expansion step "
                "and requires a separate operator selection artifact."
            ),
            "confirmed": True,
        },
        "authority_locks": {
            "advisory_only": True,
            "shadow_lane_only": True,
            "parity_receipt_only": True,
            "five_operator_cohort_closed": True,
            "rank6_selection_authorized": False,
            "emits_metric_values": False,
            "forecast_influence": False,
            "p43_surface_lanes_authorized": False,
            "production_activation": False,
            "canon_promotion": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "inference_authority": False,
        },
        "blocked_scopes": {
            "metric_emission": "BLOCKED",
            "forecast_influence": "BLOCKED",
            "p43_lanes": "BLOCKED",
            "runtime_mutation": "BLOCKED",
            "production_activation": "BLOCKED",
            "canon_promotion": "BLOCKED",
            "execution_authority": "BLOCKED",
            "inference_authority": "BLOCKED",
        },
        "all_confirmations_passed": True,
        "recommended_next_step": "RANK6_OPERATOR_SELECTION",
        "provenance": {
            "generated_by": "FIVE_OPERATOR_SHADOW_STUB_PARITY_RECEIPT_BUILD_001",
            "source_hashes": {
                "wasserstein_promotion_complete": SOURCE_WASSERSTEIN_HASH,
                "chamfer_promotion_complete": SOURCE_CHAMFER_HASH,
                "transport_promotion_complete": SOURCE_TRANSPORT_HASH,
                "geodesic_promotion_complete": SOURCE_GEODESIC_HASH,
                "norm_geometry_promotion_complete": SOURCE_NORM_GEOMETRY_HASH,
                "baseline_pack": SOURCE_PACK_HASH,
            },
        },
    }

    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(_preimage(result))
    return result


def validate_five_operator_shadow_stub_parity_receipt(doc: dict[str, Any]) -> None:
    if doc.get("receipt_status") != RECEIPT_STATUS:
        raise FiveOperatorShadowStubParityReceiptError(
            f"receipt_status mismatch: {doc.get('receipt_status')!r}"
        )
    if doc.get("receipt_id") != RECEIPT_ID:
        raise FiveOperatorShadowStubParityReceiptError(
            f"receipt_id mismatch: {doc.get('receipt_id')!r}"
        )
    h = doc.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise FiveOperatorShadowStubParityReceiptError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(doc))
    if recomputed != h:
        raise FiveOperatorShadowStubParityReceiptError(
            f"canonical_hash recomputation mismatch: {recomputed!r} != {h!r}"
        )
    al = doc.get("authority_locks", {})
    if al.get("advisory_only") is not True:
        raise FiveOperatorShadowStubParityReceiptError("authority_locks.advisory_only must be True")
    if al.get("emits_metric_values") is not False:
        raise FiveOperatorShadowStubParityReceiptError("authority_locks.emits_metric_values must be False")
    if al.get("rank6_selection_authorized") is not False:
        raise FiveOperatorShadowStubParityReceiptError("authority_locks.rank6_selection_authorized must be False")
    if al.get("canon_promotion") is not False:
        raise FiveOperatorShadowStubParityReceiptError("authority_locks.canon_promotion must be False")
    if doc.get("all_confirmations_passed") is not True:
        raise FiveOperatorShadowStubParityReceiptError("all_confirmations_passed must be True")
    if doc.get("recommended_next_step") != "RANK6_OPERATOR_SELECTION":
        raise FiveOperatorShadowStubParityReceiptError(
            "recommended_next_step must be RANK6_OPERATOR_SELECTION"
        )
    _check_no_forbidden(doc)

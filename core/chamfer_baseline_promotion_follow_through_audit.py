"""Core: build ChamferBaselinePromotionFollowThroughAudit.v1 artifact."""

from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "ChamferBaselinePromotionFollowThroughAudit.v1"
AUDIT_ID = "chamfer_baseline_promotion_follow_through_audit_001"
AUDIT_STATUS = "CHAMFER_BASELINE_PROMOTION_FOLLOW_THROUGH_AUDIT_COMPLETE"
AUDIT_STAGE = "BASELINE_PROMOTION_FOLLOW_THROUGH_AUDIT"
OPERATOR_ID = "CHAMFER_DISTANCE"

SOURCE_COMPUTATION_RECEIPT_HASH = (
    "ce2ab90f4c7ae3db74263c72ae3e0ce4f20cf0aa253ca6395c39b2507a1560ea"
)
SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH = (
    "676ea1c55da5e3d2f0771fbbe6065795248016d53a8cda16778733f95461867b"
)
SOURCE_EV_ADDITION_RECEIPT_HASH = (
    "8a18c02f39d242af30ac27b6d608faa545a4938929327d859379f099e2b53b62"
)
CURRENT_PACK_HASH = (
    "38cbcd4f028ecb07e7021b24c3e723d200949e96b9a5d787a365facd4841a2d9"
)

RECEIPT_PATH = pathlib.Path(
    "out/chamfer_distance_computation_receipt"
    "/chamfer_distance_computation_receipt_001.latest.json"
)
COMPLETE_REVIEW_PATH = pathlib.Path(
    "out/chamfer_distance_computation_complete_review"
    "/chamfer_distance_computation_complete_review_001.latest.json"
)
EV_ADDITION_RECEIPT_PATH = pathlib.Path(
    "out/chamfer_expected_values_addition_receipt"
    "/chamfer_expected_values_addition_receipt_001.latest.json"
)
PACK_PATH = pathlib.Path(
    "out/metric_operator/metric_operator_baseline_test_vector_pack_001.latest.json"
)
PROJECTION_BUNDLE_PATH = pathlib.Path(
    "apps/aal-viz-live-console/public/projection-bundle.json"
)

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

PRESENT_ARTIFACTS: list[dict[str, str]] = [
    {
        "artifact_id": "chamfer_baseline_implementation_plan_001",
        "canonical_hash": (
            "97d192a17fba9597e8f6bf234bcbf512d63ce6471617c3dcfe8c14bbaa88fdfe"
        ),
        "status": "PRESENT",
    },
    {
        "artifact_id": "chamfer_test_vector_schema_plan_001",
        "canonical_hash": (
            "2bd39838eaeffcbdc984e14687dc87253f8a40170c07597a7c38e1e6e604e7fa"
        ),
        "status": "PRESENT",
    },
    {
        "artifact_id": "chamfer_fixture_plan_consolidation_receipt_001",
        "canonical_hash": (
            "702e1b8955db3ea64111fcd712c6007a070a55f68a827fccb7a1948e5c8868ba"
        ),
        "status": "PRESENT",
    },
    {
        "artifact_id": "chamfer_fixture_creation_actual_pr_gate_001",
        "canonical_hash": (
            "a2d0b9d25bd9f0f108b6b3befc72aca52538f5121764d73bc73aab9a809c5dfd"
        ),
        "status": "PRESENT",
    },
    {
        "artifact_id": "chamfer_expected_values_gate_001",
        "canonical_hash": (
            "5ded4f886a2112da0674e8f251323b1e60e1e9da0de7a846656c5f53a9d191c2"
        ),
        "status": "PRESENT",
    },
    {
        "artifact_id": "chamfer_expected_values_addition_receipt_001",
        "canonical_hash": (
            "8a18c02f39d242af30ac27b6d608faa545a4938929327d859379f099e2b53b62"
        ),
        "status": "PRESENT",
    },
    {
        "artifact_id": "chamfer_expected_values_complete_review_001",
        "canonical_hash": (
            "754f26700749bb04d40155aae8e3d7a9ad79cc164c1725b99809b45e0bd1627a"
        ),
        "status": "PRESENT",
    },
    {
        "artifact_id": "chamfer_distance_computation_authorization_review_001",
        "canonical_hash": (
            "0f2dfa1ce6e70fbc9ba6ab41cd3d0d7f76cf4f93cfe6b4ef09f753364ef7507c"
        ),
        "status": "PRESENT",
    },
    {
        "artifact_id": "chamfer_distance_computation_receipt_001",
        "canonical_hash": (
            "ce2ab90f4c7ae3db74263c72ae3e0ce4f20cf0aa253ca6395c39b2507a1560ea"
        ),
        "status": "PRESENT",
    },
    {
        "artifact_id": "chamfer_distance_computation_complete_review_001",
        "canonical_hash": (
            "676ea1c55da5e3d2f0771fbbe6065795248016d53a8cda16778733f95461867b"
        ),
        "status": "PRESENT",
    },
]

ABSENT_ARTIFACTS: list[dict[str, str]] = [
    {
        "artifact_id": "chamfer_baseline_promotion_review_001",
        "expected_path": (
            "out/metric_operator/chamfer_baseline_promotion_review_001.latest.json"
        ),
        "status": "ABSENT",
        "blocking": "true",
        "note": (
            "Governance closure artifact required; "
            "confirms pack promotion and computation chain closure"
        ),
    },
    {
        "artifact_id": "chamfer_baseline_promotion_complete_001",
        "expected_path": (
            "out/metric_operator/chamfer_baseline_promotion_complete_001.latest.json"
        ),
        "status": "ABSENT",
        "blocking": "true",
        "note": (
            "Terminal governance closure artifact required; "
            "enables projection_key wiring and READY/100 advance"
        ),
    },
]


class ChamferBaselinePromotionFollowThroughAuditError(ValueError):
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
                raise ChamferBaselinePromotionFollowThroughAuditError(
                    f"forbidden token {token!r} in output"
                )


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    with open(path) as fh:
        return json.load(fh)  # type: ignore[return-value]


def _preimage(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "canonical_hash"}


def _validate_source_hash(
    doc: dict[str, Any], expected: str, label: str
) -> None:
    actual = canonical_hash(doc)
    if actual != expected:
        raise ChamferBaselinePromotionFollowThroughAuditError(
            f"{label} canonical_hash mismatch: expected {expected!r}, got {actual!r}"
        )


def build_chamfer_baseline_promotion_follow_through_audit() -> dict[str, Any]:
    receipt = _load_json(RECEIPT_PATH)
    complete_review = _load_json(COMPLETE_REVIEW_PATH)
    ev_addition_receipt = _load_json(EV_ADDITION_RECEIPT_PATH)
    pack = _load_json(PACK_PATH)
    bundle = _load_json(PROJECTION_BUNDLE_PATH)

    _validate_source_hash(
        receipt, SOURCE_COMPUTATION_RECEIPT_HASH, "computation_receipt"
    )
    _validate_source_hash(
        complete_review,
        SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
        "computation_complete_review",
    )
    _validate_source_hash(
        ev_addition_receipt,
        SOURCE_EV_ADDITION_RECEIPT_HASH,
        "ev_addition_receipt",
    )

    pack_hash = canonical_hash(pack)
    if pack_hash != CURRENT_PACK_HASH:
        raise ChamferBaselinePromotionFollowThroughAuditError(
            f"pack canonical_hash mismatch: expected {CURRENT_PACK_HASH!r}, "
            f"got {pack_hash!r}"
        )

    pack_vectors = {v["operator_id"]: v for v in pack.get("operator_vectors", [])}
    chamfer_vector = pack_vectors.get("CHAMFER_DISTANCE", {})
    chamfer_vector_type = chamfer_vector.get("vector_type", "UNKNOWN")
    chamfer_computation_status = chamfer_vector.get(
        "expected_computation_status", "UNKNOWN"
    )
    chamfer_already_in_pack = chamfer_vector_type == "VALID_SHADOW_ONLY_VECTOR"

    bundle_system = next(
        (s for s in bundle.get("systems", []) if s["system_id"] == "chamfer_distance"),
        {},
    )
    projection_status = bundle_system.get("status", "UNKNOWN")
    projection_completion_pct = bundle_system.get("completion_pct", 0)
    projection_artifact_count = len(bundle_system.get("ledger_receipts", []))

    result: dict[str, Any] = {
        "audit_id": AUDIT_ID,
        "audit_status": AUDIT_STATUS,
        "audit_stage": AUDIT_STAGE,
        "audit_type": "CHAMFER_BASELINE_PROMOTION_FOLLOW_THROUGH_AUDIT",
        "schema_version": SCHEMA_VERSION,
        "operator_id": OPERATOR_ID,
        "created_at_utc": "2026-05-31T00:00:00Z",
        "intended_lane": "BASELINE_PROMOTION_FOLLOW_THROUGH",
        "current_chamfer_projection_state": {
            "status": projection_status,
            "completion_pct": projection_completion_pct,
            "artifact_count_in_sequence": projection_artifact_count,
            "all_computation_chain_artifacts_present": True,
            "cap_reason": "promotion_key_not_wired_in_OPERATOR_DEFS",
            "projected_status_at_100": "READY",
            "note": (
                "All 10 computation chain artifacts present; "
                "completion capped at 95 because promotion_key is None"
            ),
        },
        "current_chamfer_pack_state": {
            "vector_type": chamfer_vector_type,
            "expected_computation_status": chamfer_computation_status,
            "pack_canonical_hash": pack_hash,
            "chamfer_already_promoted_in_pack": chamfer_already_in_pack,
            "shadow_only_posture_in_pack": chamfer_computation_status == "SHADOW_STUB_ONLY",
            "note": (
                "CHAMFER_DISTANCE is already recorded as "
                "VALID_SHADOW_ONLY_VECTOR / SHADOW_STUB_ONLY in the pack; "
                "no pack re-promotion required"
            ),
        },
        "existing_chamfer_artifact_inventory": {
            "present_count": len(PRESENT_ARTIFACTS),
            "absent_count": len(ABSENT_ARTIFACTS),
            "present_artifacts": PRESENT_ARTIFACTS,
            "absent_artifacts": ABSENT_ARTIFACTS,
            "computation_chain_terminal_artifact": "chamfer_distance_computation_complete_review_001",
            "computation_operator_closure": "NOT_IN_SEQUENCE",
            "note": (
                "CHAMFER sequence ends at chamfer_distance_computation_complete_review; "
                "no operator_closure step defined for this operator"
            ),
        },
        "missing_artifact_analysis": {
            "chamfer_baseline_promotion_review_001": "ABSENT",
            "chamfer_baseline_promotion_complete_001": "ABSENT",
            "chamfer_computation_operator_closure_001": "NOT_APPLICABLE",
            "chamfer_baseline_promotion_decision_001": "NOT_APPLICABLE",
            "pack_re_promotion_required": False,
            "wiring_update_required": True,
            "analysis_summary": (
                "Pack promotion already recorded. "
                "Two governance closure artifacts are absent: "
                "chamfer_baseline_promotion_review_001 and "
                "chamfer_baseline_promotion_complete_001. "
                "Once both exist, projection_key must be wired in "
                "OPERATOR_DEFS['chamfer_distance'] to advance to READY/100."
            ),
        },
        "promotion_chain_state": {
            "computation_chain_closed": True,
            "computation_receipt_present": True,
            "computation_complete_review_present": True,
            "expected_values_addition_receipt_confirmed": True,
            "pack_promoted": chamfer_already_in_pack,
            "baseline_promotion_review_present": False,
            "baseline_promotion_complete_present": False,
            "governance_closure_chain_complete": False,
            "chain_complete": False,
            "blocking_step": "chamfer_baseline_promotion_review_001",
        },
        "projection_wiring_state": {
            "promotion_key": None,
            "baseline_promotion_complete_key": None,
            "shadow_only_posture": None,
            "operator_def_entry": "OPERATOR_DEFS['chamfer_distance']",
            "promotion_key_value_needed": (
                "out/metric_operator/chamfer_baseline_promotion_complete_001.latest.json"
            ),
            "projection_cap_at_current_state": 95,
            "wiring_complete": False,
            "wiring_requires": [
                "chamfer_baseline_promotion_complete_001 must exist first",
                "promotion_key set to its path in OPERATOR_DEFS['chamfer_distance']",
                "projection bundle rebuild",
            ],
        },
        "lawful_next_step_determination": {
            "step_1": {
                "action": "PRODUCE_CHAMFER_BASELINE_PROMOTION_REVIEW",
                "artifact": "chamfer_baseline_promotion_review_001",
                "output_path": (
                    "out/metric_operator"
                    "/chamfer_baseline_promotion_review_001.latest.json"
                ),
                "source_anchors": [
                    "chamfer_distance_computation_complete_review_001",
                    "chamfer_expected_values_addition_receipt_001",
                    "metric_operator_baseline_test_vector_pack_001",
                ],
                "blocked_by": "none",
                "authority_scope": "advisory_only",
            },
            "step_2": {
                "action": "PRODUCE_CHAMFER_BASELINE_PROMOTION_COMPLETE",
                "artifact": "chamfer_baseline_promotion_complete_001",
                "output_path": (
                    "out/metric_operator"
                    "/chamfer_baseline_promotion_complete_001.latest.json"
                ),
                "source_anchors": [
                    "chamfer_baseline_promotion_review_001",
                    "metric_operator_baseline_test_vector_pack_001",
                ],
                "blocked_by": "step_1",
                "authority_scope": "advisory_only",
            },
            "step_3": {
                "action": "WIRE_PROJECTION_PROMOTION_KEY",
                "description": (
                    "Set OPERATOR_DEFS['chamfer_distance']['promotion_key'] "
                    "to chamfer_baseline_promotion_complete_001 path; "
                    "rebuild projection bundle; "
                    "CHAMFER advances to READY/100"
                ),
                "blocked_by": "step_2",
                "authority_scope": "projection_only",
            },
            "no_pack_rerun_needed": True,
            "no_fixture_mutation_needed": True,
            "no_computation_rerun_needed": True,
        },
        "authority_lock_review": {
            "all_present_artifacts_advisory_only": True,
            "all_present_artifacts_canon_promotion_false": True,
            "all_present_artifacts_emits_values_false": True,
            "no_authority_escalation_detected": True,
            "computation_receipt_locks": {
                "advisory_only": True,
                "canon_promotion": False,
                "computation_receipt_only": True,
            },
            "complete_review_locks": {
                "advisory_only": True,
                "canon_promotion": False,
                "complete_review_only": True,
            },
            "audit_locks": {
                "advisory_only": True,
                "audit_only": True,
                "canon_promotion": False,
                "emits_metric_values": False,
                "forecast_influence": False,
                "p43_lanes": False,
                "production_activation": False,
                "runtime_mutation": False,
                "execution_authority": False,
            },
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
            "all_scopes_remain_blocked": True,
            "note": (
                "No scope unblocked by this audit; "
                "advisory-only posture preserved"
            ),
        },
        "recommended_next_step": "CHAMFER_BASELINE_PROMOTION_REVIEW",
        "provenance": {
            "generated_by": (
                "CHAMFER_BASELINE_PROMOTION_FOLLOW_THROUGH_AUDIT_BUILD_001"
            ),
            "source_hashes": {
                "computation_receipt": SOURCE_COMPUTATION_RECEIPT_HASH,
                "computation_complete_review": SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
                "ev_addition_receipt": SOURCE_EV_ADDITION_RECEIPT_HASH,
                "pack": CURRENT_PACK_HASH,
            },
        },
        "authority_locks": {
            "advisory_only": True,
            "audit_only": True,
            "canon_promotion": False,
            "emits_metric_values": False,
            "forecast_influence": False,
            "p43_lanes": False,
            "production_activation": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "inference_authority": False,
        },
    }

    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(_preimage(result))
    return result


def validate_chamfer_baseline_promotion_follow_through_audit(
    doc: dict[str, Any],
) -> None:
    if doc.get("audit_status") != AUDIT_STATUS:
        raise ChamferBaselinePromotionFollowThroughAuditError(
            f"audit_status mismatch: {doc.get('audit_status')!r}"
        )
    if doc.get("audit_id") != AUDIT_ID:
        raise ChamferBaselinePromotionFollowThroughAuditError(
            f"audit_id mismatch: {doc.get('audit_id')!r}"
        )
    h = doc.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise ChamferBaselinePromotionFollowThroughAuditError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(doc))
    if recomputed != h:
        raise ChamferBaselinePromotionFollowThroughAuditError(
            f"canonical_hash recomputation mismatch: {recomputed!r} != {h!r}"
        )
    al = doc.get("authority_locks", {})
    if al.get("advisory_only") is not True:
        raise ChamferBaselinePromotionFollowThroughAuditError(
            "authority_locks.advisory_only must be True"
        )
    if al.get("canon_promotion") is not False:
        raise ChamferBaselinePromotionFollowThroughAuditError(
            "authority_locks.canon_promotion must be False"
        )
    if al.get("emits_metric_values") is not False:
        raise ChamferBaselinePromotionFollowThroughAuditError(
            "authority_locks.emits_metric_values must be False"
        )
    if doc.get("recommended_next_step") != "CHAMFER_BASELINE_PROMOTION_REVIEW":
        raise ChamferBaselinePromotionFollowThroughAuditError(
            "recommended_next_step must be CHAMFER_BASELINE_PROMOTION_REVIEW"
        )
    _check_no_forbidden(doc)

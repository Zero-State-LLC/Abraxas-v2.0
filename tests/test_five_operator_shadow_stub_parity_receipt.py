"""Tests: FiveOperatorShadowStubParityReceipt.v1 artifact."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.five_operator_shadow_stub_parity_receipt import (
    CHAMFER_AUDIT_SEALED_HASH,
    FIVE_OPERATOR_COHORT,
    RECEIPT_ID,
    RECEIPT_STATUS,
    RECEIPT_STAGE,
    REMAINING_SEVEN_OPERATORS,
    SCHEMA_VERSION,
    SOURCE_CHAMFER_HASH,
    SOURCE_GEODESIC_HASH,
    SOURCE_NORM_GEOMETRY_HASH,
    SOURCE_PACK_HASH,
    SOURCE_TRANSPORT_HASH,
    SOURCE_WASSERSTEIN_HASH,
    FiveOperatorShadowStubParityReceiptError,
    build_five_operator_shadow_stub_parity_receipt,
    validate_five_operator_shadow_stub_parity_receipt,
)
from core.canonical.json import canonical_hash

OUT_PATH = Path(
    "out/metric_operator/five_operator_shadow_stub_parity_receipt_001.latest.json"
)


@pytest.fixture(scope="module")
def receipt() -> dict:
    return build_five_operator_shadow_stub_parity_receipt()


def test_receipt_status(receipt: dict) -> None:
    assert receipt["receipt_status"] == RECEIPT_STATUS


def test_receipt_id(receipt: dict) -> None:
    assert receipt["receipt_id"] == RECEIPT_ID


def test_schema_version(receipt: dict) -> None:
    assert receipt["schema_version"] == SCHEMA_VERSION


def test_receipt_stage(receipt: dict) -> None:
    assert receipt["receipt_stage"] == RECEIPT_STAGE


def test_intended_lane(receipt: dict) -> None:
    assert receipt["intended_lane"] == "SHADOW"


def test_canonical_hash_present_and_valid(receipt: dict) -> None:
    h = receipt.get("canonical_hash", "")
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_recomputes(receipt: dict) -> None:
    preimage = {k: v for k, v in receipt.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == receipt["canonical_hash"]


def test_source_hashes(receipt: dict) -> None:
    sh = receipt["source_hashes"]
    assert sh["wasserstein_promotion_complete"] == SOURCE_WASSERSTEIN_HASH
    assert sh["chamfer_promotion_complete"] == SOURCE_CHAMFER_HASH
    assert sh["transport_promotion_complete"] == SOURCE_TRANSPORT_HASH
    assert sh["geodesic_promotion_complete"] == SOURCE_GEODESIC_HASH
    assert sh["norm_geometry_promotion_complete"] == SOURCE_NORM_GEOMETRY_HASH
    assert sh["baseline_pack"] == SOURCE_PACK_HASH


def test_cohort_binding_review(receipt: dict) -> None:
    cbr = receipt["cohort_binding_review"]
    assert cbr["cohort_size"] == 5
    assert cbr["cohort_members"] == FIVE_OPERATOR_COHORT
    assert cbr["all_five_present"] is True
    assert cbr["all_five_shadow_stub_only"] is True
    assert cbr["cohort_posture"] == "VALID_SHADOW_ONLY_VECTOR / SHADOW_STUB_ONLY"
    assert cbr["batch_label"] == "BATCH_B"
    assert cbr["confirmed"] is True


def test_source_artifact_binding_review(receipt: dict) -> None:
    sabr = receipt["source_artifact_binding_review"]
    assert sabr["wasserstein"]["hash_confirmed"] is True
    assert sabr["chamfer_distance"]["hash_confirmed"] is True
    assert sabr["transport"]["hash_confirmed"] is True
    assert sabr["geodesic"]["hash_confirmed"] is True
    assert sabr["norm_geometry"]["hash_confirmed"] is True
    assert sabr["all_five_hashes_confirmed"] is True
    assert sabr["confirmed"] is True


def test_baseline_pack_binding_review(receipt: dict) -> None:
    pbr = receipt["baseline_pack_binding_review"]
    assert pbr["pack_hash_confirmed"] is True
    assert pbr["total_operators_in_pack"] == 12
    assert pbr["five_shadow_stub_operators"] == 5
    assert pbr["seven_not_implemented_operators"] == 7
    assert pbr["all_cohort_states_verified_from_pack"] is True
    assert pbr["all_remaining_states_verified_from_pack"] is True
    assert pbr["confirmed"] is True


def test_five_operator_parity_review(receipt: dict) -> None:
    fpr = receipt["five_operator_parity_review"]
    states = fpr["cohort_states"]
    assert len(states) == 5
    for s in states:
        assert s["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
        assert s["expected_computation_status"] == "SHADOW_STUB_ONLY"
        assert s["shadow_stub_only_confirmed"] is True
        assert s["valid_shadow_only_vector_confirmed"] is True
    assert fpr["all_five_valid_shadow_only_vector"] is True
    assert fpr["all_five_shadow_stub_only"] is True
    assert fpr["all_five_advisory_only"] is True
    assert fpr["all_five_no_metric_emission"] is True
    assert fpr["all_five_no_forecast_influence"] is True
    assert fpr["all_five_no_p43_lane_authority"] is True
    assert fpr["all_five_no_runtime_mutation"] is True
    assert fpr["all_five_no_production_activation"] is True
    assert fpr["all_five_no_canon_promotion"] is True
    assert fpr["all_five_no_execution_authority"] is True
    assert fpr["all_five_no_inference_authority"] is True
    assert fpr["parity_confirmed"] is True
    assert fpr["confirmed"] is True


def test_five_operator_cohort_members(receipt: dict) -> None:
    states = receipt["five_operator_parity_review"]["cohort_states"]
    ids = [s["operator_id"] for s in states]
    assert set(ids) == set(FIVE_OPERATOR_COHORT)


def test_aal_viz_projection_state_review(receipt: dict) -> None:
    avr = receipt["aal_viz_projection_state_review"]
    assert avr["wasserstein"]["status"] == "READY_SHADOW_STUB_CLOSED"
    assert avr["wasserstein"]["completion_pct"] == 100
    assert avr["chamfer_distance"]["status"] == "READY_SHADOW_STUB_CLOSED"
    assert avr["chamfer_distance"]["completion_pct"] == 100
    assert avr["transport"]["status"] == "READY_SHADOW_STUB_CLOSED"
    assert avr["transport"]["completion_pct"] == 100
    assert avr["geodesic"]["status"] == "READY"
    assert avr["geodesic"]["completion_pct"] == 100
    assert avr["norm_geometry"]["status"] == "READY"
    assert avr["norm_geometry"]["completion_pct"] == 100
    assert avr["all_five_at_100_pct"] is True
    assert avr["confirmed"] is True


def test_remaining_operator_state_review(receipt: dict) -> None:
    ror = receipt["remaining_operator_state_review"]
    assert ror["remaining_count"] == 7
    states = ror["remaining_operators"]
    assert len(states) == 7
    for s in states:
        assert s["vector_type"] == "VALID_METADATA_VECTOR"
        assert s["expected_computation_status"] == "NOT_IMPLEMENTED"
    assert ror["all_valid_metadata_vector"] is True
    assert ror["all_not_implemented"] is True
    assert ror["confirmed"] is True


def test_remaining_operator_ids(receipt: dict) -> None:
    ids = [s["operator_id"] for s in receipt["remaining_operator_state_review"]["remaining_operators"]]
    assert set(ids) == set(REMAINING_SEVEN_OPERATORS)


def test_historical_artifact_determinism_review(receipt: dict) -> None:
    hadr = receipt["historical_artifact_determinism_review"]
    assert hadr["chamfer_follow_through_audit_sealed_hash"] == CHAMFER_AUDIT_SEALED_HASH
    assert hadr["determinism_fix_applied"] is True
    assert hadr["sealed_hash_restored"] is True
    assert hadr["downstream_references_intact"] is True
    assert hadr["completion_hash_unaffected"] == SOURCE_CHAMFER_HASH
    assert hadr["confirmed"] is True


def test_authority_lock_review(receipt: dict) -> None:
    alr = receipt["authority_lock_review"]
    assert alr["all_source_artifacts_advisory_only"] is True
    assert alr["no_authority_escalation_in_receipt"] is True
    al = alr["authority_locks"]
    assert al["advisory_only"] is True
    assert al["shadow_lane_only"] is True
    assert al["parity_receipt_only"] is True
    assert al["five_operator_cohort_closed"] is True
    assert al["rank6_selection_authorized"] is False
    assert al["emits_metric_values"] is False
    assert al["forecast_influence"] is False
    assert al["p43_surface_lanes_authorized"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False
    assert al["runtime_mutation"] is False
    assert al["execution_authority"] is False
    assert al["inference_authority"] is False
    assert alr["confirmed"] is True


def test_authority_locks_top_level(receipt: dict) -> None:
    al = receipt["authority_locks"]
    assert al["advisory_only"] is True
    assert al["parity_receipt_only"] is True
    assert al["five_operator_cohort_closed"] is True
    assert al["rank6_selection_authorized"] is False
    assert al["emits_metric_values"] is False
    assert al["canon_promotion"] is False
    assert al["execution_authority"] is False


def test_blocked_scope_review(receipt: dict) -> None:
    bsr = receipt["blocked_scope_review"]
    assert bsr["metric_emission"] == "BLOCKED"
    assert bsr["forecast_influence"] == "BLOCKED"
    assert bsr["p43_lanes"] == "BLOCKED"
    assert bsr["runtime_mutation"] == "BLOCKED"
    assert bsr["production_activation"] == "BLOCKED"
    assert bsr["canon_promotion"] == "BLOCKED"
    assert bsr["execution_authority"] == "BLOCKED"
    assert bsr["inference_authority"] == "BLOCKED"
    assert bsr["research_canary_guardrail"] == "ACTIVE"
    assert bsr["rank6_selection_in_this_receipt"] == "BLOCKED"
    assert bsr["all_scopes_blocked"] is True
    assert bsr["confirmed"] is True


def test_batch_frontier_review(receipt: dict) -> None:
    bfr = receipt["batch_frontier_review"]
    assert bfr["batch_label"] == "BATCH_B"
    assert bfr["batch_b_closed"] is True
    assert "RANK6_OPERATOR_SELECTION" in bfr["frontier_options"]
    assert "SEALED_PAUSE" in bfr["frontier_options"]
    assert bfr["rank6_selection_authorized_in_this_receipt"] is False
    assert bfr["rank6_selection_deferred_to_next_step"] is True
    assert bfr["confirmed"] is True


def test_all_confirmations_passed(receipt: dict) -> None:
    assert receipt["all_confirmations_passed"] is True


def test_recommended_next_step(receipt: dict) -> None:
    assert receipt["recommended_next_step"] == "RANK6_OPERATOR_SELECTION"


def test_validate_passes(receipt: dict) -> None:
    validate_five_operator_shadow_stub_parity_receipt(receipt)


def test_validate_wrong_status_raises(receipt: dict) -> None:
    bad = {**receipt, "receipt_status": "WRONG"}
    with pytest.raises(FiveOperatorShadowStubParityReceiptError):
        validate_five_operator_shadow_stub_parity_receipt(bad)


def test_validate_wrong_hash_raises(receipt: dict) -> None:
    bad = {**receipt, "canonical_hash": "a" * 64}
    with pytest.raises(FiveOperatorShadowStubParityReceiptError):
        validate_five_operator_shadow_stub_parity_receipt(bad)


def test_validate_wrong_next_step_raises(receipt: dict) -> None:
    bad = {**receipt, "recommended_next_step": "WRONG"}
    with pytest.raises(FiveOperatorShadowStubParityReceiptError):
        validate_five_operator_shadow_stub_parity_receipt(bad)


def test_on_disk_artifact_matches_build(receipt: dict) -> None:
    if not OUT_PATH.exists():
        pytest.skip("on-disk artifact not yet generated; run the runner script first")
    on_disk = json.loads(OUT_PATH.read_text())
    assert on_disk["canonical_hash"] == receipt["canonical_hash"]
    assert on_disk["receipt_status"] == RECEIPT_STATUS

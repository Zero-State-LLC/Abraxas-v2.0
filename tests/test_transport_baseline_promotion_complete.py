"""Tests for TransportBaselinePromotionComplete.v1."""

from __future__ import annotations

import copy
import json

import pytest

from core.transport_baseline_promotion_complete import (
    COMPLETE_ID,
    COMPLETE_STAGE,
    COMPLETE_STATUS,
    NOT_IMPLEMENTED_OPERATORS,
    OPERATOR_ID,
    SCHEMA_VERSION,
    SHADOW_STUB_OPERATORS,
    SOURCE_CLOSURE_HASH,
    SOURCE_DECISION_HASH,
    SOURCE_PRE_PROMOTION_PACK_HASH,
    SOURCE_PROMOTION_REVIEW_HASH,
    UPDATED_PACK_HASH,
    TransportBaselinePromotionCompleteError,
    build_transport_baseline_promotion_complete,
    validate_transport_baseline_promotion_complete,
)
from core.canonical.json import canonical_hash


@pytest.fixture(scope="module")
def doc():
    return build_transport_baseline_promotion_complete()


class TestBuildBasicFields:
    def test_schema_version(self, doc):
        assert doc["schema_version"] == SCHEMA_VERSION

    def test_complete_id(self, doc):
        assert doc["complete_id"] == COMPLETE_ID

    def test_complete_status(self, doc):
        assert doc["complete_status"] == COMPLETE_STATUS

    def test_complete_stage(self, doc):
        assert doc["complete_stage"] == COMPLETE_STAGE

    def test_operator_id(self, doc):
        assert doc["operator_id"] == OPERATOR_ID

    def test_intended_lane(self, doc):
        assert doc["intended_lane"] == "SHADOW"

    def test_recommended_next_step(self, doc):
        assert doc["recommended_next_step"] == "TRANSPORT_SHADOW_STUB_PHASE_CLOSED"

    def test_canonical_hash_present(self, doc):
        h = doc.get("canonical_hash", "")
        assert isinstance(h, str) and len(h) == 64

    def test_canonical_hash_verifiable(self, doc):
        preimage = {k: v for k, v in doc.items() if k != "canonical_hash"}
        assert canonical_hash(preimage) == doc["canonical_hash"]


class TestReviewBinding:
    def test_review_binding_present(self, doc):
        assert "review_binding" in doc

    def test_review_status_confirmed(self, doc):
        assert doc["review_binding"]["review_status_confirmed"] is True

    def test_review_status_value(self, doc):
        assert doc["review_binding"]["review_status"] == "TRANSPORT_BASELINE_PROMOTION_REVIEW_COMPLETE"

    def test_review_on_main(self, doc):
        assert doc["review_binding"]["review_on_main"] is True

    def test_all_reviews_passed_confirmed(self, doc):
        assert doc["review_binding"]["all_reviews_passed_confirmed"] is True

    def test_canonical_hash_confirmed(self, doc):
        assert doc["review_binding"]["canonical_hash_confirmed"] is True

    def test_source_review_hash(self, doc):
        assert doc["review_binding"]["source_review_hash"] == SOURCE_PROMOTION_REVIEW_HASH

    def test_no_op_parity_confirmed(self, doc):
        assert doc["review_binding"]["no_op_parity_confirmed"] is True

    def test_review_stage_confirmed(self, doc):
        assert doc["review_binding"]["review_stage_confirmed"] is True


class TestDecisionBinding:
    def test_decision_binding_present(self, doc):
        assert "decision_binding" in doc

    def test_decision_id(self, doc):
        assert doc["decision_binding"]["decision_id"] == "TRANSPORT_BASELINE_PROMOTION_DECISION_2026_05_30_001"

    def test_decision_value(self, doc):
        assert doc["decision_binding"]["decision_value"] == "approve_transport_shadow_stub_baseline_promotion_review"

    def test_decision_on_main(self, doc):
        assert doc["decision_binding"]["decision_on_main"] is True

    def test_baseline_promotion_review_authorized_confirmed(self, doc):
        assert doc["decision_binding"]["baseline_promotion_review_authorized_confirmed"] is True

    def test_target_vector_type_confirmed(self, doc):
        assert doc["decision_binding"]["target_vector_type_confirmed"] is True

    def test_target_expected_computation_status_confirmed(self, doc):
        assert doc["decision_binding"]["target_expected_computation_status_confirmed"] is True

    def test_transport_computation_phase_closed_acknowledged_confirmed(self, doc):
        assert doc["decision_binding"]["transport_computation_phase_closed_acknowledged_confirmed"] is True

    def test_metric_emission_authorized_false(self, doc):
        assert doc["decision_binding"]["metric_emission_authorized_confirmed_false"] is True

    def test_forecast_influence_authorized_false(self, doc):
        assert doc["decision_binding"]["forecast_influence_authorized_confirmed_false"] is True

    def test_p43_authorized_false(self, doc):
        assert doc["decision_binding"]["p43_surface_lanes_authorized_confirmed_false"] is True

    def test_production_activation_authorized_false(self, doc):
        assert doc["decision_binding"]["production_activation_authorized_confirmed_false"] is True

    def test_source_decision_hash(self, doc):
        assert doc["decision_binding"]["source_decision_hash"] == SOURCE_DECISION_HASH


class TestClosureBinding:
    def test_closure_binding_present(self, doc):
        assert "closure_binding" in doc

    def test_closure_status(self, doc):
        assert doc["closure_binding"]["closure_status"] == "TRANSPORT_COMPUTATION_OPERATOR_CLOSURE_COMPLETE"

    def test_closure_status_confirmed(self, doc):
        assert doc["closure_binding"]["closure_status_confirmed"] is True

    def test_all_closure_passed_confirmed(self, doc):
        assert doc["closure_binding"]["all_closure_passed_confirmed"] is True

    def test_computation_phase_complete_confirmed(self, doc):
        assert doc["closure_binding"]["computation_phase_complete_confirmed"] is True

    def test_source_closure_hash(self, doc):
        assert doc["closure_binding"]["source_closure_hash"] == SOURCE_CLOSURE_HASH


class TestBaselinePackUpdate:
    def test_baseline_pack_update_present(self, doc):
        assert "baseline_pack_update" in doc

    def test_operator_id(self, doc):
        assert doc["baseline_pack_update"]["operator_id"] == OPERATOR_ID

    def test_previous_vector_type(self, doc):
        assert doc["baseline_pack_update"]["previous_vector_type"] == "VALID_METADATA_VECTOR"

    def test_new_vector_type(self, doc):
        assert doc["baseline_pack_update"]["new_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"

    def test_previous_expected_computation_status(self, doc):
        assert doc["baseline_pack_update"]["previous_expected_computation_status"] == "NOT_IMPLEMENTED"

    def test_new_expected_computation_status(self, doc):
        assert doc["baseline_pack_update"]["new_expected_computation_status"] == "SHADOW_STUB_ONLY"

    def test_pre_promotion_pack_hash(self, doc):
        assert doc["baseline_pack_update"]["pre_promotion_pack_hash"] == SOURCE_PRE_PROMOTION_PACK_HASH

    def test_updated_pack_hash(self, doc):
        assert doc["baseline_pack_update"]["updated_pack_hash"] == UPDATED_PACK_HASH

    def test_pack_update_confirmed(self, doc):
        assert doc["baseline_pack_update"]["pack_update_confirmed"] is True

    def test_evidence_refs_present(self, doc):
        refs = doc["baseline_pack_update"]["evidence_refs"]
        assert isinstance(refs, list) and len(refs) == 4

    def test_evidence_refs_sorted(self, doc):
        refs = doc["baseline_pack_update"]["evidence_refs"]
        assert refs == sorted(refs)

    def test_evidence_refs_contains_closure(self, doc):
        refs = doc["baseline_pack_update"]["evidence_refs"]
        assert "TransportComputationOperatorClosure.v1:transport_computation_operator_closure_001" in refs

    def test_evidence_refs_contains_decision(self, doc):
        refs = doc["baseline_pack_update"]["evidence_refs"]
        assert "TransportBaselinePromotionDecision:TRANSPORT_BASELINE_PROMOTION_DECISION_2026_05_30_001" in refs

    def test_evidence_refs_contains_review(self, doc):
        refs = doc["baseline_pack_update"]["evidence_refs"]
        assert "TransportBaselinePromotionReview.v1:transport_baseline_promotion_review_001" in refs

    def test_evidence_refs_contains_registry(self, doc):
        refs = doc["baseline_pack_update"]["evidence_refs"]
        assert "contracts/canon/metric_operator_registry.v1.schema.json" in refs


class TestParityStateCompletion:
    def test_parity_state_completion_present(self, doc):
        assert "parity_state_completion" in doc

    def test_shadow_stub_operator_count(self, doc):
        assert doc["parity_state_completion"]["shadow_stub_operator_count"] == len(SHADOW_STUB_OPERATORS)

    def test_not_implemented_operator_count(self, doc):
        assert doc["parity_state_completion"]["not_implemented_operator_count"] == len(NOT_IMPLEMENTED_OPERATORS)

    def test_parity_state_confirmed(self, doc):
        assert doc["parity_state_completion"]["parity_state_confirmed"] is True

    def test_all_remaining_advisory_only(self, doc):
        assert doc["parity_state_completion"]["all_remaining_advisory_only"] is True

    @pytest.mark.parametrize("op", SHADOW_STUB_OPERATORS)
    def test_shadow_stub_op_vector_type(self, doc, op):
        state = doc["parity_state_completion"]["shadow_stub_operators"][op]
        assert state["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"

    @pytest.mark.parametrize("op", SHADOW_STUB_OPERATORS)
    def test_shadow_stub_op_computation_status(self, doc, op):
        state = doc["parity_state_completion"]["shadow_stub_operators"][op]
        assert state["expected_computation_status"] == "SHADOW_STUB_ONLY"

    @pytest.mark.parametrize("op", NOT_IMPLEMENTED_OPERATORS)
    def test_not_implemented_op_vector_type(self, doc, op):
        state = doc["parity_state_completion"]["not_implemented_operators"][op]
        assert state["vector_type"] == "VALID_METADATA_VECTOR"

    @pytest.mark.parametrize("op", NOT_IMPLEMENTED_OPERATORS)
    def test_not_implemented_op_status(self, doc, op):
        state = doc["parity_state_completion"]["not_implemented_operators"][op]
        assert state["expected_computation_status"] == "NOT_IMPLEMENTED"


class TestUnchangedOperatorsReview:
    def test_unchanged_operators_review_present(self, doc):
        assert "unchanged_operators_review" in doc

    def test_all_unchanged_operators_confirmed(self, doc):
        assert doc["unchanged_operators_review"]["all_unchanged_operators_confirmed"] is True

    @pytest.mark.parametrize("op", [o for o in SHADOW_STUB_OPERATORS if o != "TRANSPORT"])
    def test_unchanged_shadow_stub_op_confirmed(self, doc, op):
        state = doc["unchanged_operators_review"]["unchanged_shadow_stub_operators"][op]
        assert state["unchanged_confirmed"] is True

    @pytest.mark.parametrize("op", NOT_IMPLEMENTED_OPERATORS)
    def test_unchanged_not_implemented_op_confirmed(self, doc, op):
        state = doc["unchanged_operators_review"]["unchanged_not_implemented_operators"][op]
        assert state["unchanged_confirmed"] is True


class TestAuthorityLockCompletion:
    def test_authority_lock_completion_present(self, doc):
        assert "authority_lock_completion" in doc

    @pytest.mark.parametrize("flag", [
        "advisory_only", "shadow_lane_only", "baseline_promotion_complete_only", "baseline_pack_update_authorized",
    ])
    def test_true_flags(self, doc, flag):
        assert doc["authority_lock_completion"][flag] is True

    @pytest.mark.parametrize("flag", [
        "emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
        "production_activation", "canon_promotion", "runtime_mutation",
        "execution_authority", "inference_authority",
    ])
    def test_false_flags(self, doc, flag):
        assert doc["authority_lock_completion"][flag] is False

    def test_target_vector_type(self, doc):
        assert doc["authority_lock_completion"]["target_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"

    def test_target_expected_computation_status(self, doc):
        assert doc["authority_lock_completion"]["target_expected_computation_status"] == "SHADOW_STUB_ONLY"


class TestBlockedScopeCompletion:
    def test_blocked_scope_completion_present(self, doc):
        assert "blocked_scope_completion" in doc

    @pytest.mark.parametrize("flag", [
        "canon_promotion", "emits_metric_values", "execution_authority",
        "forecast_influence", "inference_authority", "p43_surface_lanes_authorized",
        "production_activation", "runtime_mutation", "spine_refresh",
        "research_canary_mutation",
    ])
    def test_blocked_scope_false(self, doc, flag):
        assert doc["blocked_scope_completion"][flag] is False


class TestValidateRoundTrip:
    def test_validate_passes(self, doc):
        validate_transport_baseline_promotion_complete(doc)

    def test_validate_wrong_schema_version(self, doc):
        d = copy.deepcopy(doc)
        d["schema_version"] = "Wrong.v1"
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)

    def test_validate_wrong_complete_status(self, doc):
        d = copy.deepcopy(doc)
        d["complete_status"] = "WRONG"
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)

    def test_validate_wrong_operator_id(self, doc):
        d = copy.deepcopy(doc)
        d["operator_id"] = "GEODESIC"
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)

    def test_validate_wrong_lane(self, doc):
        d = copy.deepcopy(doc)
        d["intended_lane"] = "LIVE"
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)

    def test_validate_bad_review_hash(self, doc):
        d = copy.deepcopy(doc)
        d["review_binding"]["source_review_hash"] = "bad"
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)

    def test_validate_bad_decision_hash(self, doc):
        d = copy.deepcopy(doc)
        d["decision_binding"]["source_decision_hash"] = "bad"
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)

    def test_validate_bad_closure_hash(self, doc):
        d = copy.deepcopy(doc)
        d["closure_binding"]["source_closure_hash"] = "bad"
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)

    def test_validate_bad_pack_hash(self, doc):
        d = copy.deepcopy(doc)
        d["baseline_pack_update"]["updated_pack_hash"] = "bad"
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)

    def test_validate_pack_update_not_confirmed(self, doc):
        d = copy.deepcopy(doc)
        d["baseline_pack_update"]["pack_update_confirmed"] = False
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)

    def test_validate_parity_state_not_confirmed(self, doc):
        d = copy.deepcopy(doc)
        d["parity_state_completion"]["parity_state_confirmed"] = False
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)

    def test_validate_authority_lock_advisory_false(self, doc):
        d = copy.deepcopy(doc)
        d["authority_lock_completion"]["advisory_only"] = False
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)

    def test_validate_authority_lock_emits_metric_true(self, doc):
        d = copy.deepcopy(doc)
        d["authority_lock_completion"]["emits_metric_values"] = True
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)

    def test_validate_blocked_scope_canon_true(self, doc):
        d = copy.deepcopy(doc)
        d["blocked_scope_completion"]["canon_promotion"] = True
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)

    def test_validate_canonical_hash_mismatch(self, doc):
        d = copy.deepcopy(doc)
        d["canonical_hash"] = "a" * 64
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)

    def test_validate_canonical_hash_too_short(self, doc):
        d = copy.deepcopy(doc)
        d["canonical_hash"] = "abc"
        with pytest.raises(TransportBaselinePromotionCompleteError):
            validate_transport_baseline_promotion_complete(d)


class TestForbiddenTokens:
    @pytest.mark.parametrize("token", [
        "metric-computation", "metric-value", "geodesic-distance",
        "fixture-file", "numpy", "scipy", "gpu-kernel",
    ])
    def test_forbidden_token_rejected(self, token):
        from core.transport_baseline_promotion_complete import _check_no_forbidden, TransportBaselinePromotionCompleteError
        with pytest.raises(TransportBaselinePromotionCompleteError):
            _check_no_forbidden({"bad": token})

    def test_safe_string_passes(self):
        from core.transport_baseline_promotion_complete import _check_no_forbidden
        _check_no_forbidden({"ok": "shadow_stub_fixture_only_no_runtime_execution"})


class TestJsonSerialization:
    def test_json_roundtrip(self, doc):
        serialized = json.dumps(doc, sort_keys=True)
        restored = json.loads(serialized)
        assert restored["complete_status"] == COMPLETE_STATUS
        assert restored["canonical_hash"] == doc["canonical_hash"]

    def test_all_required_sections_present(self, doc):
        required = {
            "review_binding", "decision_binding", "closure_binding",
            "baseline_pack_update", "parity_state_completion",
            "unchanged_operators_review", "authority_lock_completion",
            "blocked_scope_completion", "recommended_next_step",
        }
        assert required.issubset(doc.keys())

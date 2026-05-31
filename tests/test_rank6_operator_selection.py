"""Tests: Rank6OperatorSelection.v1 artifact."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.rank6_operator_selection import (
    CANDIDATE_POOL,
    CRITERIA,
    REJECTION_REASONS,
    SCHEMA_VERSION,
    SELECTED_OPERATOR,
    SELECTION_ID,
    SELECTION_STAGE,
    SELECTION_STATUS,
    SOURCE_PARITY_RECEIPT_HASH,
    Rank6OperatorSelectionError,
    build_rank6_operator_selection,
    validate_rank6_operator_selection,
)
from core.canonical.json import canonical_hash

OUT_PATH = Path("out/metric_operator/rank6_operator_selection_001.latest.json")


@pytest.fixture(scope="module")
def selection() -> dict:
    return build_rank6_operator_selection()


def test_selection_status(selection: dict) -> None:
    assert selection["selection_status"] == SELECTION_STATUS


def test_selection_id(selection: dict) -> None:
    assert selection["selection_id"] == SELECTION_ID


def test_schema_version(selection: dict) -> None:
    assert selection["schema_version"] == SCHEMA_VERSION


def test_selection_stage(selection: dict) -> None:
    assert selection["selection_stage"] == SELECTION_STAGE


def test_intended_lane(selection: dict) -> None:
    assert selection["intended_lane"] == "SHADOW"


def test_source_parity_receipt_hash(selection: dict) -> None:
    assert selection["source_parity_receipt_hash"] == SOURCE_PARITY_RECEIPT_HASH


def test_canonical_hash_present(selection: dict) -> None:
    h = selection.get("canonical_hash", "")
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_recomputes(selection: dict) -> None:
    preimage = {k: v for k, v in selection.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == selection["canonical_hash"]


def test_source_parity_receipt_binding(selection: dict) -> None:
    b = selection["source_parity_receipt_binding"]
    assert b["canonical_hash"] == SOURCE_PARITY_RECEIPT_HASH
    assert b["hash_confirmed"] is True
    assert b["five_operator_cohort_closed"] is True
    assert b["batch_b_complete"] is True
    assert b["rank6_selection_authorized_by_parity_receipt"] is False
    assert b["rank6_selection_authorized_by_this_artifact"] is True
    assert b["confirmed"] is True


def test_candidate_pool_review(selection: dict) -> None:
    cpr = selection["candidate_pool_review"]
    assert cpr["pool_size"] == 7
    assert set(cpr["candidate_pool"]) == set(CANDIDATE_POOL)
    assert cpr["all_candidates_valid_metadata_vector"] is True
    assert cpr["all_candidates_not_implemented"] is True
    assert cpr["none_are_shadow_stub_already"] is True
    assert cpr["none_have_computation_receipt"] is True
    assert cpr["confirmed"] is True


def test_deterministic_selection_criteria(selection: dict) -> None:
    dsc = selection["deterministic_selection_criteria"]
    assert dsc["criteria_count"] == len(CRITERIA)
    criteria_ids = [c["criterion_id"] for c in dsc["criteria"]]
    assert set(criteria_ids) == set(CRITERIA)
    assert dsc["max_possible_score"] == len(CRITERIA) * 5
    assert dsc["selection_rule"] == "highest_total_score_wins"


def test_candidate_scoring_matrix_has_all_candidates(selection: dict) -> None:
    csm = selection["candidate_scoring_matrix"]
    scored_ids = {r["operator_id"] for r in csm["scored_candidates"]}
    assert scored_ids == set(CANDIDATE_POOL)


def test_candidate_scoring_matrix_winner(selection: dict) -> None:
    csm = selection["candidate_scoring_matrix"]
    assert csm["winner"] == SELECTED_OPERATOR
    assert csm["winner_total_score"] == 42


def test_candidate_scoring_matrix_runner_up(selection: dict) -> None:
    csm = selection["candidate_scoring_matrix"]
    assert csm["runner_up"] == "HYSTERESIS"
    assert csm["runner_up_total_score"] == 39
    assert csm["score_margin"] == 3


def test_candidate_scores_ranked_descending(selection: dict) -> None:
    rows = selection["candidate_scoring_matrix"]["scored_candidates"]
    totals = [r["total"] for r in rows]
    assert totals == sorted(totals, reverse=True)


def test_candidate_scores_max_possible(selection: dict) -> None:
    max_possible = len(CRITERIA) * 5
    for row in selection["candidate_scoring_matrix"]["scored_candidates"]:
        assert row["max_possible"] == max_possible
        assert 1 <= row["total"] <= max_possible


def test_selected_rank6_operator(selection: dict) -> None:
    sel = selection["selected_rank6_operator"]
    assert sel["operator_id"] == SELECTED_OPERATOR
    assert sel["rank"] == 6
    assert sel["batch"] == "BATCH_C"
    assert sel["total_score"] == 42
    assert sel["current_vector_type"] == "VALID_METADATA_VECTOR"
    assert sel["current_computation_status"] == "NOT_IMPLEMENTED"
    assert sel["target_vector_type_after_implementation"] == "VALID_SHADOW_ONLY_VECTOR"
    assert sel["target_computation_status_after_implementation"] == "SHADOW_STUB_ONLY"
    assert sel["implementation_authorized_by_this_artifact"] is False
    assert sel["fixture_creation_authorized_by_this_artifact"] is False


def test_rejection_summary_has_six_entries(selection: dict) -> None:
    rejected = selection["rejection_summary"]["rejected_candidates"]
    assert len(rejected) == 6
    ids = {r["operator_id"] for r in rejected}
    assert SELECTED_OPERATOR not in ids
    assert ids == set(CANDIDATE_POOL) - {SELECTED_OPERATOR}


def test_rejection_summary_all_have_reasons(selection: dict) -> None:
    for r in selection["rejection_summary"]["rejected_candidates"]:
        assert len(r["rejection_reason"]) > 10
        assert r["operator_id"] in REJECTION_REASONS


def test_selected_operator_readiness_summary(selection: dict) -> None:
    srs = selection["selected_operator_readiness_summary"]
    assert srs["operator_id"] == SELECTED_OPERATOR
    assert srs["selection_complete"] is True
    assert srs["implementation_authorized"] is False
    assert srs["fixture_corpus_authorized"] is False
    assert srs["baseline_pack_update_authorized"] is False
    assert srs["shadow_stub_implementation_next"] is True
    assert srs["no_metric_emission_on_implementation"] is True
    assert srs["no_runtime_authority_on_implementation"] is True


def test_blocked_scope_review(selection: dict) -> None:
    bsr = selection["blocked_scope_review"]
    assert "BLOCKED" in bsr["rank6_implementation"]
    assert bsr["fixture_creation"] == "BLOCKED"
    assert bsr["baseline_pack_update"] == "BLOCKED"
    assert bsr["metric_emission"] == "BLOCKED"
    assert bsr["forecast_influence"] == "BLOCKED"
    assert bsr["p43_lanes"] == "BLOCKED"
    assert bsr["runtime_mutation"] == "BLOCKED"
    assert bsr["production_activation"] == "BLOCKED"
    assert bsr["canon_promotion"] == "BLOCKED"
    assert bsr["execution_authority"] == "BLOCKED"
    assert bsr["inference_authority"] == "BLOCKED"
    assert bsr["research_canary_guardrail"] == "ACTIVE"
    assert bsr["all_scopes_blocked"] is True
    assert bsr["confirmed"] is True


def test_authority_lock_review(selection: dict) -> None:
    alr = selection["authority_lock_review"]
    assert alr["no_authority_escalation_in_selection"] is True
    assert alr["selection_is_advisory_only"] is True
    al = alr["authority_locks"]
    assert al["advisory_only"] is True
    assert al["shadow_lane_only"] is True
    assert al["operator_selection_only"] is True
    assert al["rank6_operator_selected"] is True
    assert al["rank6_implementation_authorized"] is False
    assert al["fixture_creation_authorized"] is False
    assert al["baseline_pack_update_authorized"] is False
    assert al["emits_metric_values"] is False
    assert al["forecast_influence"] is False
    assert al["p43_surface_lanes_authorized"] is False
    assert al["production_activation"] is False
    assert al["canon_promotion"] is False
    assert al["runtime_mutation"] is False
    assert al["execution_authority"] is False
    assert al["inference_authority"] is False
    assert alr["confirmed"] is True


def test_authority_locks_top_level(selection: dict) -> None:
    al = selection["authority_locks"]
    assert al["advisory_only"] is True
    assert al["rank6_operator_selected"] is True
    assert al["rank6_implementation_authorized"] is False
    assert al["emits_metric_values"] is False
    assert al["canon_promotion"] is False
    assert al["execution_authority"] is False


def test_all_confirmations_passed(selection: dict) -> None:
    assert selection["all_confirmations_passed"] is True


def test_recommended_next_step(selection: dict) -> None:
    assert selection["recommended_next_step"] == "HEAVY_TAIL_SHADOW_STUB_IMPLEMENTATION"


def test_five_operator_cohort_referenced_in_provenance(selection: dict) -> None:
    prov = selection["provenance"]
    assert prov["selected_operator"] == SELECTED_OPERATOR
    assert prov["source_parity_receipt_hash"] == SOURCE_PARITY_RECEIPT_HASH


def test_validate_passes(selection: dict) -> None:
    validate_rank6_operator_selection(selection)


def test_validate_wrong_status_raises(selection: dict) -> None:
    bad = {**selection, "selection_status": "WRONG"}
    with pytest.raises(Rank6OperatorSelectionError):
        validate_rank6_operator_selection(bad)


def test_validate_wrong_hash_raises(selection: dict) -> None:
    bad = {**selection, "canonical_hash": "b" * 64}
    with pytest.raises(Rank6OperatorSelectionError):
        validate_rank6_operator_selection(bad)


def test_validate_wrong_next_step_raises(selection: dict) -> None:
    bad = {**selection, "recommended_next_step": "WRONG"}
    with pytest.raises(Rank6OperatorSelectionError):
        validate_rank6_operator_selection(bad)


def test_validate_wrong_receipt_hash_raises(selection: dict) -> None:
    bad = {**selection, "source_parity_receipt_hash": "a" * 64}
    with pytest.raises(Rank6OperatorSelectionError):
        validate_rank6_operator_selection(bad)


def test_on_disk_artifact_matches_build(selection: dict) -> None:
    if not OUT_PATH.exists():
        pytest.skip("on-disk artifact not yet generated; run the runner script first")
    on_disk = json.loads(OUT_PATH.read_text())
    assert on_disk["canonical_hash"] == selection["canonical_hash"]
    assert on_disk["selection_status"] == SELECTION_STATUS
    assert on_disk["selected_rank6_operator"]["operator_id"] == SELECTED_OPERATOR

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.heavy_tail_baseline_promotion_review import (
    REVIEW_STAGE,
    REVIEW_STATUS,
    SCHEMA_VERSION,
    build_heavy_tail_baseline_promotion_review,
    validate_heavy_tail_baseline_promotion_review,
)

OUT_PATH = Path("out/metric_operator/heavy_tail_baseline_promotion_review_001.latest.json")


def test_build_sets_top_level_fields() -> None:
    review = build_heavy_tail_baseline_promotion_review()
    assert review["schema_version"] == SCHEMA_VERSION
    assert review["review_status"] == REVIEW_STATUS
    assert review["review_stage"] == REVIEW_STAGE
    assert review["recommended_next_step"] == "HEAVY_TAIL_BASELINE_PROMOTION_COMPLETE"


def test_authorization_review_confirms_pack_update_scope() -> None:
    review = build_heavy_tail_baseline_promotion_review()
    auth = review["authorization_review"]
    assert auth["implementation_authorized"] is True
    assert auth["baseline_pack_update_authorized"] is True
    assert auth["next_steps_include_review"] is True


def test_current_pack_and_target_state_are_distinct() -> None:
    review = build_heavy_tail_baseline_promotion_review()
    current = review["current_pack_state_review"]
    target = review["target_state_review"]
    assert current["current_vector_type"] == "VALID_METADATA_VECTOR"
    assert current["current_expected_computation_status"] == "NOT_IMPLEMENTED"
    assert target["target_vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert target["target_expected_computation_status"] == "SHADOW_STUB_ONLY"
    assert target["pack_update_required"] is True


def test_operator_state_after_update_promotes_heavy_tail_only() -> None:
    review = build_heavy_tail_baseline_promotion_review()
    state = review["operator_state_after_update"]
    assert state["HEAVY_TAIL"]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert state["HEAVY_TAIL"]["expected_computation_status"] == "SHADOW_STUB_ONLY"
    assert state["WASSERSTEIN"]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert state["COUNTERFACTUAL_DIFFUSION"]["vector_type"] == "VALID_METADATA_VECTOR"


def test_parity_review_adds_heavy_tail_to_shadow_stub_set() -> None:
    review = build_heavy_tail_baseline_promotion_review()
    parity = review["parity_review"]
    assert parity["heavy_tail_at_shadow_stub_after_promotion"] is True
    assert parity["shadow_stub_operator_count"] == 6
    assert "HEAVY_TAIL" in parity["shadow_stub_operators_after_update"]


def test_build_is_deterministic() -> None:
    first = build_heavy_tail_baseline_promotion_review()
    second = build_heavy_tail_baseline_promotion_review()
    assert first == second
    assert first["canonical_hash"] == second["canonical_hash"]


def test_validate_accepts_built_review() -> None:
    validate_heavy_tail_baseline_promotion_review(
        build_heavy_tail_baseline_promotion_review()
    )


def test_validate_rejects_current_pack_mismatch() -> None:
    review = json.loads(json.dumps(build_heavy_tail_baseline_promotion_review()))
    review["current_pack_state_review"]["current_vector_type"] = "VALID_SHADOW_ONLY_VECTOR"
    with pytest.raises(ValueError, match="current_vector_type"):
        validate_heavy_tail_baseline_promotion_review(review)


def test_generated_artifact_matches_builder_if_present() -> None:
    if not OUT_PATH.exists():
        pytest.skip("generated artifact not yet emitted in this worktree")
    doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    assert doc == build_heavy_tail_baseline_promotion_review()


def test_schema_validates_generated_or_built_review() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path(
            "contracts/canon/heavy_tail_baseline_promotion_review.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    if OUT_PATH.exists():
        doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    else:
        doc = build_heavy_tail_baseline_promotion_review()
    jsonschema.validate(doc, schema)

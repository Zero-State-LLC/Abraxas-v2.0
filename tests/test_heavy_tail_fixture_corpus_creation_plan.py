from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.heavy_tail_fixture_corpus_creation_plan import (
    FIXTURE_BASE_DIRECTORY,
    INVALID_FIXTURE_COUNT,
    LOCKED_FALSE_FLAGS,
    LOCKED_TRUE_FLAGS,
    NOT_COMPUTABLE_FIXTURE_COUNT,
    SOURCE_AUTH_HASH,
    SOURCE_SCHEMA_PLAN_HASH,
    TOTAL_FIXTURE_COUNT,
    VALID_FIXTURE_COUNT,
    HeavyTailFixtureCorpusCreationPlanValidationError,
    build_heavy_tail_fixture_corpus_creation_plan,
    default_authority_lock_review,
    default_blocked_scope_review,
    default_corpus_creation_scope_review,
    default_expected_value_derivation_plan,
    default_fixture_file_path_plan,
    default_fixture_manifest_plan,
    default_invalid_fixture_plan,
    default_not_computable_fixture_plan,
    default_schema_plan_binding,
    default_source_authorization_binding,
    default_valid_fixture_plan,
    serialize_heavy_tail_fixture_corpus_creation_plan,
)


def _payload() -> dict:
    return {
        "plan_id": "heavy-tail-fixture-corpus-creation-plan-test-001",
        "source_authorization_binding": default_source_authorization_binding(),
        "schema_plan_binding": default_schema_plan_binding(),
        "fixture_manifest_plan": default_fixture_manifest_plan(),
        "valid_fixture_plan": default_valid_fixture_plan(),
        "invalid_fixture_plan": default_invalid_fixture_plan(),
        "not_computable_fixture_plan": default_not_computable_fixture_plan(),
        "expected_value_derivation_plan": default_expected_value_derivation_plan(),
        "fixture_file_path_plan": default_fixture_file_path_plan(),
        "corpus_creation_scope_review": default_corpus_creation_scope_review(),
        "authority_lock_review": default_authority_lock_review(),
        "blocked_scope_review": default_blocked_scope_review(),
        "recommended_next_step": "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_RECEIPT",
        "provenance": {
            "source": "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_PLAN_TEST",
            "evidence_refs": [
                f"HeavyTailShadowStubImplementationAuthorization.v1:"
                f"heavy_tail_shadow_stub_implementation_authorization_001:"
                f"{SOURCE_AUTH_HASH}",
                f"HeavyTailTestVectorSchemaPlan.v1:"
                f"heavy_tail_test_vector_schema_plan_001:"
                f"{SOURCE_SCHEMA_PLAN_HASH}",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "heavy_tail_fixture_corpus_creation_plan.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-31T00:00:00Z",
    }


def test_hash_deterministic() -> None:
    a = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    b = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_schema_version_fixed() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    assert p["schema_version"] == "HeavyTailFixtureCorpusCreationPlan.v1"


def test_plan_type_fixed() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    assert p["plan_type"] == "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_PLAN"


def test_plan_status_fixed() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    assert p["plan_status"] == "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_PLAN_COMPLETE"


def test_operator_id_fixed() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    assert p["operator_id"] == "HEAVY_TAIL"


def test_source_authorization_hash_confirmed() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    binding = p["source_authorization_binding"]
    assert binding["authorization_canonical_hash"] == SOURCE_AUTH_HASH
    assert binding["hash_confirmed"] is True
    assert binding["fixture_creation_authorized_acknowledged"] is True
    assert binding["fixture_files_not_created_in_this_plan"] is True


def test_schema_plan_hash_confirmed() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    binding = p["schema_plan_binding"]
    assert binding["schema_plan_canonical_hash"] == SOURCE_SCHEMA_PLAN_HASH
    assert binding["hash_confirmed"] is True
    assert binding["fixture_count_consistent_with_schema_plan"] is True


def test_schema_plan_covers_all_eight_fields() -> None:
    binding = default_schema_plan_binding()
    required = {
        "alpha", "sample_count", "expected_tail_threshold",
        "sequence_values", "expected_tail_index",
        "expected_moment_summary", "expected_status", "expected_outcome_reason",
    }
    assert required <= set(binding["schema_fields_covered"])


def test_fixture_manifest_plan_counts() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    manifest = p["fixture_manifest_plan"]
    assert manifest["total_fixture_count"] == TOTAL_FIXTURE_COUNT == 16
    assert manifest["valid_fixture_count"] == VALID_FIXTURE_COUNT == 6
    assert manifest["invalid_fixture_count"] == INVALID_FIXTURE_COUNT == 4
    assert manifest["not_computable_fixture_count"] == NOT_COMPUTABLE_FIXTURE_COUNT == 6
    assert manifest["fixture_files_created_in_this_plan"] is False


def test_valid_fixture_plan_count() -> None:
    assert len(default_valid_fixture_plan()) == VALID_FIXTURE_COUNT


def test_invalid_fixture_plan_count() -> None:
    assert len(default_invalid_fixture_plan()) == INVALID_FIXTURE_COUNT


def test_not_computable_fixture_plan_count() -> None:
    assert len(default_not_computable_fixture_plan()) == NOT_COMPUTABLE_FIXTURE_COUNT


def test_valid_fixture_ids_unique_and_sorted() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    ids = [f["fixture_id"] for f in p["valid_fixture_plan"]]
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))


def test_invalid_fixture_ids_unique_and_sorted() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    ids = [f["fixture_id"] for f in p["invalid_fixture_plan"]]
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))


def test_not_computable_fixture_ids_unique_and_sorted() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    ids = [f["fixture_id"] for f in p["not_computable_fixture_plan"]]
    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))


def test_all_fixture_ids_globally_unique() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    all_ids = (
        [f["fixture_id"] for f in p["valid_fixture_plan"]]
        + [f["fixture_id"] for f in p["invalid_fixture_plan"]]
        + [f["fixture_id"] for f in p["not_computable_fixture_plan"]]
    )
    assert len(all_ids) == TOTAL_FIXTURE_COUNT
    assert len(all_ids) == len(set(all_ids))


def test_valid_fixture_labels_match_schema_plan() -> None:
    labels = {f["fixture_label"] for f in default_valid_fixture_plan()}
    expected = {
        "bounded_power_law_alpha_2",
        "bounded_power_law_alpha_3",
        "light_tail_control_sequence",
        "single_large_outlier_sequence",
        "monotone_rank_frequency_sequence",
        "repeated_equal_values_control",
    }
    assert labels == expected


def test_invalid_fixture_labels_match_schema_plan() -> None:
    labels = {f["fixture_label"] for f in default_invalid_fixture_plan()}
    expected = {
        "missing_alpha",
        "missing_sample_count",
        "missing_sequence_values",
        "invalid_expected_status",
    }
    assert labels == expected


def test_not_computable_fixture_labels_match_schema_plan() -> None:
    labels = {f["fixture_label"] for f in default_not_computable_fixture_plan()}
    expected = {
        "alpha_lte_zero",
        "sample_count_zero",
        "empty_sequence",
        "non_finite_sequence_value",
        "negative_sequence_value",
        "sample_count_mismatch",
    }
    assert labels == expected


def test_no_fixture_files_created_in_any_plan_item() -> None:
    for f in default_valid_fixture_plan():
        assert f["fixture_file_created"] is False
    for f in default_invalid_fixture_plan():
        assert f["fixture_file_created"] is False
    for f in default_not_computable_fixture_plan():
        assert f["fixture_file_created"] is False


def test_valid_fixtures_all_computable() -> None:
    for f in default_valid_fixture_plan():
        assert f["planned_expected_status"] == "COMPUTABLE"


def test_not_computable_fixtures_all_not_computable_state() -> None:
    for f in default_not_computable_fixture_plan():
        assert f["planned_expected_state"] == "NOT_COMPUTABLE"


def test_valid_fixtures_have_alpha_in_bounds() -> None:
    for f in default_valid_fixture_plan():
        assert 0.0 < f["planned_alpha"] <= 5.0


def test_valid_fixtures_have_sample_count_in_bounds() -> None:
    for f in default_valid_fixture_plan():
        assert 1 <= f["planned_sample_count"] <= 1000


def test_all_planned_file_paths_use_base_directory() -> None:
    for f in default_valid_fixture_plan():
        assert f["planned_file_path"].startswith(FIXTURE_BASE_DIRECTORY)
    for f in default_invalid_fixture_plan():
        assert f["planned_file_path"].startswith(FIXTURE_BASE_DIRECTORY)
    for f in default_not_computable_fixture_plan():
        assert f["planned_file_path"].startswith(FIXTURE_BASE_DIRECTORY)


def test_fixture_file_path_plan_total_count() -> None:
    fpp = default_fixture_file_path_plan()
    assert len(fpp["fixture_file_paths"]) == TOTAL_FIXTURE_COUNT
    assert fpp["fixture_files_created_in_this_plan"] is False


def test_fixture_file_path_plan_base_directory() -> None:
    fpp = default_fixture_file_path_plan()
    assert fpp["fixture_base_directory"] == FIXTURE_BASE_DIRECTORY


def test_expected_value_derivation_plan_no_computation() -> None:
    plan = default_expected_value_derivation_plan()
    assert plan["computation_in_plan"] is False
    assert plan["derivation_executed_at_plan_stage"] is False
    assert plan["actual_values_declared_at_fixture_receipt_stage"] is True


def test_corpus_creation_scope_review_confirmed() -> None:
    scope = default_corpus_creation_scope_review()
    assert scope["confirmed"] is True
    assert scope["fixture_creation_authorized"] is True
    assert scope["fixture_files_created_in_this_plan"] is False
    assert scope["computation_not_in_scope"] is True
    assert scope["metric_emission_not_in_scope"] is True


def test_all_locked_true_flags_true() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    for flag in LOCKED_TRUE_FLAGS:
        assert p["authority_lock_review"][flag] is True, f"{flag} must be True"


def test_all_locked_false_flags_false() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    for flag in LOCKED_FALSE_FLAGS:
        assert p["authority_lock_review"][flag] is False, f"{flag} must be False"


def test_canonical_hash_64_hex() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    h = p["canonical_hash"]
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_recommended_next_step() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    assert p["recommended_next_step"] == "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_RECEIPT"


def test_serialize_is_valid_json() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    raw = serialize_heavy_tail_fixture_corpus_creation_plan(p)
    parsed = json.loads(raw)
    assert parsed["schema_version"] == "HeavyTailFixtureCorpusCreationPlan.v1"
    assert parsed["operator_id"] == "HEAVY_TAIL"


def test_blocked_scope_review_confirmed() -> None:
    p = build_heavy_tail_fixture_corpus_creation_plan(_payload())
    bsr = p["blocked_scope_review"]
    assert bsr["confirmed"] is True
    assert bsr["computation"] == "BLOCKED"
    assert bsr["metric_emission"] == "BLOCKED"
    assert bsr["execution_authority"] == "BLOCKED"


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (
            lambda p: p["source_authorization_binding"].__setitem__(
                "authorization_canonical_hash", "b" * 64
            ),
            "authorization_hash_mismatch",
        ),
        (
            lambda p: p["source_authorization_binding"].__setitem__(
                "hash_confirmed", False
            ),
            "authorization_hash_not_confirmed",
        ),
        (
            lambda p: p["schema_plan_binding"].__setitem__(
                "schema_plan_canonical_hash", "c" * 64
            ),
            "schema_plan_hash_mismatch",
        ),
        (
            lambda p: p["schema_plan_binding"].__setitem__("hash_confirmed", False),
            "schema_plan_hash_not_confirmed",
        ),
        (
            lambda p: p["fixture_manifest_plan"].__setitem__(
                "fixture_files_created_in_this_plan", True
            ),
            "fixture_files_must_not_be_created_in_this_plan",
        ),
        (
            lambda p: p.__setitem__("valid_fixture_plan", p["valid_fixture_plan"][:3]),
            "valid_fixture_plan_count_mismatch",
        ),
        (
            lambda p: p.__setitem__("invalid_fixture_plan", []),
            "invalid_fixture_plan_count_mismatch",
        ),
        (
            lambda p: p.__setitem__("not_computable_fixture_plan", []),
            "not_computable_fixture_plan_count_mismatch",
        ),
        (
            lambda p: p["authority_lock_review"].__setitem__("execution_authority", True),
            "authority_lock_must_be_false:execution_authority",
        ),
        (
            lambda p: p["authority_lock_review"].__setitem__("advisory_only", False),
            "authority_lock_must_be_true:advisory_only",
        ),
        (
            lambda p: p["authority_lock_review"].__setitem__(
                "fixture_creation_authorized", False
            ),
            "authority_lock_must_be_true:fixture_creation_authorized",
        ),
        (
            lambda p: p["provenance"].__setitem__(
                "generated_by", "bad-metric-computation-ref"
            ),
            "forbidden_provenance_reference_detected",
        ),
    ],
)
def test_validation_rejects_invalid(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(HeavyTailFixtureCorpusCreationPlanValidationError, match=err):
        build_heavy_tail_fixture_corpus_creation_plan(payload)


def test_committed_artifact_parseable() -> None:
    path = Path(
        "out/metric_operator/"
        "heavy_tail_fixture_corpus_creation_plan_001.latest.json"
    )
    if not path.exists():
        pytest.skip("artifact not yet emitted")
    data = json.loads(path.read_text())
    assert data["schema_version"] == "HeavyTailFixtureCorpusCreationPlan.v1"
    assert data["operator_id"] == "HEAVY_TAIL"
    assert data["plan_status"] == "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_PLAN_COMPLETE"
    assert len(data["canonical_hash"]) == 64
    assert (
        data["source_authorization_binding"]["authorization_canonical_hash"]
        == SOURCE_AUTH_HASH
    )
    assert (
        data["schema_plan_binding"]["schema_plan_canonical_hash"]
        == SOURCE_SCHEMA_PLAN_HASH
    )
    assert data["fixture_manifest_plan"]["total_fixture_count"] == TOTAL_FIXTURE_COUNT

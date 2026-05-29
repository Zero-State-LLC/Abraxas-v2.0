from __future__ import annotations

import pytest

from core.wasserstein_test_vector_fixture_file_creation_complete_review import (
    SOURCE_ACTUAL_PR_GATE_HASH,
    SOURCE_FIXTURE_CREATION_RECEIPT_HASH,
    build_wasserstein_test_vector_fixture_file_creation_complete_review,
    compute_wasserstein_test_vector_fixture_file_creation_complete_review_hash,
    default_authority_locks,
    default_blocked_scopes,
    scan_fixture_corpus,
    serialize_wasserstein_test_vector_fixture_file_creation_complete_review,
)

# ---------------------------------------------------------------------------
# Shared corpus fixture
# ---------------------------------------------------------------------------


def _corpus() -> dict:
    return scan_fixture_corpus()


def _payload(corpus: dict | None = None) -> dict:
    c = corpus or _corpus()
    return {
        "review_id": (
            "wasserstein_test_vector_fixture_file_creation_complete_review_001"
        ),
        "intended_lane": "SHADOW",
        "review_stage": "FIXTURE_FILE_CREATION_COMPLETE_REVIEW_ONLY",
        "fixture_count_review": c["fixture_count_review"],
        "fixture_group_review": c["fixture_group_review"],
        "source_gate_hash_review": c["source_gate_hash_review"],
        "fixture_file_manifest_review": c["fixture_file_manifest_review"],
        "authority_lock_review": c["authority_lock_review"],
        "recommended_next_step": (
            "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_PLAN"
        ),
        "provenance": {
            "source": (
                "P53_WASSERSTEIN_TEST_VECTOR_FIXTURE_FILE_CREATION_COMPLETE_REVIEW"
            ),
            "evidence_refs": [
                "WassersteinTestVectorFixtureFileCreationReceipt.v1:"
                "wasserstein_test_vector_fixture_file_creation_receipt_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_fixture_file_creation_complete_review"
                ".v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Corpus scan sanity
# ---------------------------------------------------------------------------


def test_scan_corpus_total() -> None:
    corpus = _corpus()
    fcr = corpus["fixture_count_review"]
    assert fcr["total_found"] == 14
    assert fcr["valid_found"] == 5
    assert fcr["invalid_found"] == 5
    assert fcr["not_computable_found"] == 4
    assert fcr["review_passed"] is True


def test_scan_corpus_gate_hash() -> None:
    corpus = _corpus()
    sghr = corpus["source_gate_hash_review"]
    assert sghr["all_verified"] is True
    assert sghr["verified_count"] == 14
    assert sghr["failed_count"] == 0
    assert sghr["review_passed"] is True


def test_scan_corpus_authority_review() -> None:
    corpus = _corpus()
    alr = corpus["authority_lock_review"]
    assert alr["no_fixture_contains_expected_distance"] is True
    assert alr["no_fixture_contains_metric_value"] is True
    assert alr["no_fixture_authorizes_computation"] is True
    assert alr["no_fixture_authorizes_forecast"] is True
    assert alr["no_fixture_grants_execution_authority"] is True
    assert alr["all_shadow_lane"] is True
    assert alr["review_passed"] is True


def test_scan_corpus_manifest_groups() -> None:
    corpus = _corpus()
    mfr = corpus["fixture_file_manifest_review"]
    assert len(mfr["valid"]) == 5
    assert len(mfr["invalid"]) == 5
    assert len(mfr["not_computable"]) == 4


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash_and_serialization() -> None:
    p = _payload()
    a = build_wasserstein_test_vector_fixture_file_creation_complete_review(p)
    b = build_wasserstein_test_vector_fixture_file_creation_complete_review(p)
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_wasserstein_test_vector_fixture_file_creation_complete_review(
        a
    ) == serialize_wasserstein_test_vector_fixture_file_creation_complete_review(b)


# ---------------------------------------------------------------------------
# Constants enforced
# ---------------------------------------------------------------------------


def test_constants_enforced() -> None:
    packet = build_wasserstein_test_vector_fixture_file_creation_complete_review(
        _payload()
    )
    assert (
        packet["schema_version"]
        == "WassersteinTestVectorFixtureFileCreationCompleteReview.v1"
    )
    assert (
        packet["review_type"]
        == "WASSERSTEIN_TEST_VECTOR_FIXTURE_FILE_CREATION_COMPLETE_REVIEW"
    )
    assert packet["operator_id"] == "WASSERSTEIN"
    assert (
        packet["source_fixture_creation_receipt_hash"]
        == SOURCE_FIXTURE_CREATION_RECEIPT_HASH
    )
    assert packet["source_actual_pr_gate_hash"] == SOURCE_ACTUAL_PR_GATE_HASH
    assert packet["intended_lane"] == "SHADOW"
    assert packet["review_stage"] == "FIXTURE_FILE_CREATION_COMPLETE_REVIEW_ONLY"


# ---------------------------------------------------------------------------
# Authority locks
# ---------------------------------------------------------------------------


def test_fixture_files_created_true() -> None:
    packet = build_wasserstein_test_vector_fixture_file_creation_complete_review(
        _payload()
    )
    assert packet["authority_locks"]["fixture_files_created"] is True


def test_wasserstein_computation_unauthorized() -> None:
    packet = build_wasserstein_test_vector_fixture_file_creation_complete_review(
        _payload()
    )
    assert packet["authority_locks"]["wasserstein_computation_authorized"] is False


def test_review_only_lock_true() -> None:
    packet = build_wasserstein_test_vector_fixture_file_creation_complete_review(
        _payload()
    )
    assert (
        packet["authority_locks"]["fixture_file_creation_complete_review_only"] is True
    )


def test_fixture_files_created_false_raises() -> None:
    p = _payload()
    p["authority_locks"] = default_authority_locks()
    p["authority_locks"]["fixture_files_created"] = False
    with pytest.raises(ValueError, match="fixture_files_created_must_be_true"):
        build_wasserstein_test_vector_fixture_file_creation_complete_review(p)


def test_computation_authorized_true_raises() -> None:
    p = _payload()
    p["authority_locks"] = default_authority_locks()
    p["authority_locks"]["wasserstein_computation_authorized"] = True
    with pytest.raises(ValueError, match="wasserstein_computation_must_be_unauthorized"):
        build_wasserstein_test_vector_fixture_file_creation_complete_review(p)


def test_authority_locks_mutation_raises() -> None:
    p = _payload()
    p["authority_locks"] = default_authority_locks()
    p["authority_locks"]["advisory_only"] = False
    with pytest.raises(ValueError, match="invalid_authority_locks"):
        build_wasserstein_test_vector_fixture_file_creation_complete_review(p)


# ---------------------------------------------------------------------------
# Blocked scopes
# ---------------------------------------------------------------------------


def test_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_test_vector_fixture_file_creation_complete_review(
        _payload()
    )
    for k, v in packet["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    p["blocked_scopes"] = default_blocked_scopes()
    p["blocked_scopes"]["wasserstein_computation"] = True
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_test_vector_fixture_file_creation_complete_review(p)


# ---------------------------------------------------------------------------
# Fixture count review validation
# ---------------------------------------------------------------------------


def test_wrong_total_count_raises() -> None:
    p = _payload()
    p["fixture_count_review"]["total_found"] = 13
    p["fixture_count_review"]["review_passed"] = False
    with pytest.raises(ValueError, match="fixture_total_count_mismatch"):
        build_wasserstein_test_vector_fixture_file_creation_complete_review(p)


def test_wrong_valid_count_raises() -> None:
    p = _payload()
    p["fixture_count_review"]["valid_found"] = 4
    p["fixture_count_review"]["review_passed"] = False
    with pytest.raises(ValueError, match="valid_count_mismatch"):
        build_wasserstein_test_vector_fixture_file_creation_complete_review(p)


def test_count_review_not_passed_raises() -> None:
    p = _payload()
    p["fixture_count_review"]["review_passed"] = False
    with pytest.raises(ValueError, match="fixture_count_review_failed"):
        build_wasserstein_test_vector_fixture_file_creation_complete_review(p)


# ---------------------------------------------------------------------------
# Source gate hash review validation
# ---------------------------------------------------------------------------


def test_wrong_gate_hash_raises() -> None:
    p = _payload()
    p["source_gate_hash_review"]["expected_hash"] = "0" * 64
    with pytest.raises(ValueError, match="source_gate_hash_mismatch"):
        build_wasserstein_test_vector_fixture_file_creation_complete_review(p)


def test_gate_hash_not_all_verified_raises() -> None:
    p = _payload()
    p["source_gate_hash_review"]["all_verified"] = False
    p["source_gate_hash_review"]["failed_count"] = 1
    p["source_gate_hash_review"]["review_passed"] = False
    with pytest.raises(ValueError, match="source_gate_hash_verification_failed"):
        build_wasserstein_test_vector_fixture_file_creation_complete_review(p)


# ---------------------------------------------------------------------------
# Authority lock review validation
# ---------------------------------------------------------------------------


def test_expected_distance_check_fails_raises() -> None:
    p = _payload()
    p["authority_lock_review"]["no_fixture_contains_expected_distance"] = False
    p["authority_lock_review"]["review_passed"] = False
    with pytest.raises(
        ValueError,
        match="authority_lock_review_check_failed:no_fixture_contains_expected_distance",
    ):
        build_wasserstein_test_vector_fixture_file_creation_complete_review(p)


def test_metric_value_check_fails_raises() -> None:
    p = _payload()
    p["authority_lock_review"]["no_fixture_contains_metric_value"] = False
    p["authority_lock_review"]["review_passed"] = False
    with pytest.raises(
        ValueError,
        match="authority_lock_review_check_failed:no_fixture_contains_metric_value",
    ):
        build_wasserstein_test_vector_fixture_file_creation_complete_review(p)


# ---------------------------------------------------------------------------
# Enum validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("field", "value", "err"),
    [
        ("intended_lane", "LIVE", "unknown_intended_lane"),
        ("review_stage", "ACTIVE", "unknown_review_stage"),
    ],
)
def test_enum_failures(field: str, value: str, err: str) -> None:
    p = _payload()
    p[field] = value
    with pytest.raises(ValueError, match=err):
        build_wasserstein_test_vector_fixture_file_creation_complete_review(p)


# ---------------------------------------------------------------------------
# Hash / provenance
# ---------------------------------------------------------------------------


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_test_vector_fixture_file_creation_complete_review(
        _payload()
    )
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert (
        compute_wasserstein_test_vector_fixture_file_creation_complete_review_hash(
            packet
        )
        == compute_wasserstein_test_vector_fixture_file_creation_complete_review_hash(
            altered
        )
    )


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_test_vector_fixture_file_creation_complete_review(_payload())
    b = build_wasserstein_test_vector_fixture_file_creation_complete_review(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_provenance_forbidden_reference() -> None:
    p = _payload()
    p["provenance"]["source"] = "cache scheduler scoring"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_test_vector_fixture_file_creation_complete_review(p)


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["review_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_test_vector_fixture_file_creation_complete_review(p)

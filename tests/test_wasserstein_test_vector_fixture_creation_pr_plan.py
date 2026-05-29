from __future__ import annotations

import pytest

from core.wasserstein_test_vector_fixture_creation_pr_plan import (
    SOURCE_FIXTURE_PLAN_HASH,
    SOURCE_READINESS_REVIEW_HASH,
    build_wasserstein_test_vector_fixture_creation_pr_plan,
    compute_wasserstein_test_vector_fixture_creation_pr_plan_hash,
    default_authority_locks,
    default_blocked_scopes,
    default_fixture_creation_batches,
    default_proposed_fixture_file_manifest,
    default_review_requirements,
    default_validation_plan,
    serialize_wasserstein_test_vector_fixture_creation_pr_plan,
)


def _payload() -> dict:
    return {
        "pr_plan_id": "wasserstein_test_vector_fixture_creation_pr_plan_001",
        "intended_lane": "SHADOW",
        "pr_plan_stage": "FIXTURE_CREATION_PR_PLAN_ONLY",
        "recommended_next_step": (
            "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_AUTHORIZATION_REVIEW"
        ),
        "provenance": {
            "source": "P49_WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_PR_PLAN",
            "evidence_refs": [
                "WassersteinTestVectorFixtureCreationReadinessReview.v1:"
                "wasserstein_test_vector_fixture_creation_readiness_review_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_fixture_creation_pr_plan.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash_and_serialization() -> None:
    a = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    b = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_wasserstein_test_vector_fixture_creation_pr_plan(
        a
    ) == serialize_wasserstein_test_vector_fixture_creation_pr_plan(b)


def test_default_sub_structures_deterministic() -> None:
    assert default_proposed_fixture_file_manifest() == default_proposed_fixture_file_manifest()
    assert default_fixture_creation_batches() == default_fixture_creation_batches()
    assert default_validation_plan() == default_validation_plan()
    assert default_review_requirements() == default_review_requirements()


# ---------------------------------------------------------------------------
# Constants enforced
# ---------------------------------------------------------------------------


def test_constants_enforced() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    assert packet["schema_version"] == "WassersteinTestVectorFixtureCreationPRPlan.v1"
    assert (
        packet["pr_plan_type"] == "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_PR_PLAN"
    )
    assert packet["operator_id"] == "WASSERSTEIN"
    assert packet["source_readiness_review_hash"] == SOURCE_READINESS_REVIEW_HASH
    assert packet["source_fixture_plan_hash"] == SOURCE_FIXTURE_PLAN_HASH
    assert packet["intended_lane"] == "SHADOW"
    assert packet["pr_plan_stage"] == "FIXTURE_CREATION_PR_PLAN_ONLY"


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


def test_manifest_has_14_entries() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    manifest = packet["proposed_fixture_file_manifest"]
    assert len(manifest) == 14


def test_manifest_type_distribution() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    manifest = packet["proposed_fixture_file_manifest"]
    valid = [e for e in manifest if e["fixture_type"] == "VALID"]
    invalid = [e for e in manifest if e["fixture_type"] == "INVALID"]
    nc = [e for e in manifest if e["fixture_type"] == "NOT_COMPUTABLE"]
    assert len(valid) == 5
    assert len(invalid) == 5
    assert len(nc) == 4


def test_manifest_all_creation_unauthorized() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    for entry in packet["proposed_fixture_file_manifest"]:
        assert entry["creation_authorized"] is False


def test_manifest_all_status_planned() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    for entry in packet["proposed_fixture_file_manifest"]:
        assert entry["status"] == "PLANNED"


def test_manifest_unique_ids_and_paths() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    manifest = packet["proposed_fixture_file_manifest"]
    ids = [e["fixture_id"] for e in manifest]
    paths = [e["target_path"] for e in manifest]
    assert len(ids) == len(set(ids))
    assert len(paths) == len(set(paths))


def test_manifest_mutation_raises() -> None:
    p = _payload()
    bad = default_proposed_fixture_file_manifest()
    bad[0]["creation_authorized"] = True
    p["proposed_fixture_file_manifest"] = bad
    with pytest.raises(
        ValueError, match="fixture_creation_must_be_unauthorized"
    ):
        build_wasserstein_test_vector_fixture_creation_pr_plan(p)


def test_manifest_wrong_count_raises() -> None:
    p = _payload()
    p["proposed_fixture_file_manifest"] = default_proposed_fixture_file_manifest()[:5]
    with pytest.raises(ValueError, match="manifest_entry_count_mismatch"):
        build_wasserstein_test_vector_fixture_creation_pr_plan(p)


def test_manifest_duplicate_id_raises() -> None:
    p = _payload()
    m = default_proposed_fixture_file_manifest()
    m[1]["fixture_id"] = m[0]["fixture_id"]
    p["proposed_fixture_file_manifest"] = m
    with pytest.raises(ValueError, match="duplicate_fixture_id"):
        build_wasserstein_test_vector_fixture_creation_pr_plan(p)


# ---------------------------------------------------------------------------
# Batches
# ---------------------------------------------------------------------------


def test_fixture_creation_batches() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    batches = packet["fixture_creation_batches"]
    assert len(batches) == 3
    assert batches[0]["fixture_count"] == 5
    assert batches[1]["fixture_count"] == 5
    assert batches[2]["fixture_count"] == 4


def test_batches_all_unauthorized() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    for batch in packet["fixture_creation_batches"]:
        assert batch["creation_authorized"] is False


def test_batches_mutation_raises() -> None:
    p = _payload()
    batches = default_fixture_creation_batches()
    batches[0]["creation_authorized"] = True
    p["fixture_creation_batches"] = batches
    with pytest.raises(ValueError, match="batch_creation_must_be_unauthorized"):
        build_wasserstein_test_vector_fixture_creation_pr_plan(p)


# ---------------------------------------------------------------------------
# Validation plan / review requirements
# ---------------------------------------------------------------------------


def test_validation_plan_computation_unauthorized() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    assert packet["validation_plan"]["computation_authorized"] is False


def test_review_requirements_gate() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    rr = packet["review_requirements"]
    assert rr["operator_review_required"] is True
    assert rr["fixture_file_creation_authorized"] is False
    assert rr["review_status"] == "REQUIRED"


def test_review_requirements_mutation_raises() -> None:
    p = _payload()
    rr = default_review_requirements()
    rr["fixture_file_creation_authorized"] = True
    p["review_requirements"] = rr
    with pytest.raises(
        ValueError, match="fixture_file_creation_must_be_unauthorized"
    ):
        build_wasserstein_test_vector_fixture_creation_pr_plan(p)


def test_validation_plan_mutation_raises() -> None:
    p = _payload()
    vp = default_validation_plan()
    vp["computation_authorized"] = True
    p["validation_plan"] = vp
    with pytest.raises(ValueError, match="computation_must_be_unauthorized"):
        build_wasserstein_test_vector_fixture_creation_pr_plan(p)


# ---------------------------------------------------------------------------
# Authority locks / blocked scopes
# ---------------------------------------------------------------------------


def test_authority_locks_governance() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    locks = packet["authority_locks"]
    assert locks["advisory_only"] is True
    assert locks["shadow_lane_only"] is True
    assert locks["fixture_creation_pr_plan_only"] is True
    assert locks["fixture_files_created"] is False
    assert locks["fixture_file_creation_authorized"] is False
    assert locks["wasserstein_computation_authorized"] is False
    assert locks["emits_metric_values"] is False
    assert locks["expected_wasserstein_distances_added"] is False
    assert locks["forecast_influence"] is False
    assert locks["p43_surface_lanes_authorized"] is False
    assert locks["production_activation"] is False
    assert locks["canon_promotion"] is False
    assert locks["runtime_mutation"] is False
    assert locks["execution_authority"] is False
    assert locks["inference_authority"] is False


def test_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    for k, v in packet["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


def test_authority_locks_mutation_raises() -> None:
    p = _payload()
    p["authority_locks"] = default_authority_locks()
    p["authority_locks"]["fixture_file_creation_authorized"] = True
    with pytest.raises(ValueError, match="invalid_authority_locks"):
        build_wasserstein_test_vector_fixture_creation_pr_plan(p)


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    p["blocked_scopes"] = default_blocked_scopes()
    p["blocked_scopes"]["fixture_files_created"] = True
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_test_vector_fixture_creation_pr_plan(p)


# ---------------------------------------------------------------------------
# Enum validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("field", "value", "err"),
    [
        ("intended_lane", "LIVE", "unknown_intended_lane"),
        ("pr_plan_stage", "ACTIVE", "unknown_pr_plan_stage"),
    ],
)
def test_top_level_enum_failures(field: str, value: str, err: str) -> None:
    p = _payload()
    p[field] = value
    with pytest.raises(ValueError, match=err):
        build_wasserstein_test_vector_fixture_creation_pr_plan(p)


# ---------------------------------------------------------------------------
# Hash / provenance
# ---------------------------------------------------------------------------


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_wasserstein_test_vector_fixture_creation_pr_plan_hash(
        packet
    ) == compute_wasserstein_test_vector_fixture_creation_pr_plan_hash(altered)


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_test_vector_fixture_creation_pr_plan(_payload())
    b = build_wasserstein_test_vector_fixture_creation_pr_plan(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_provenance_forbidden_reference() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime scheduler cache"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_test_vector_fixture_creation_pr_plan(p)


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["pr_plan_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_test_vector_fixture_creation_pr_plan(p)

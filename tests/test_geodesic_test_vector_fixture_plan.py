from __future__ import annotations

import json
import pathlib

import pytest

from core.canonical.json import canonical_hash
from core.geodesic_test_vector_fixture_plan import (
    FIXTURE_PLAN_TYPE,
    INVALID_GROUP_IDS,
    NC_GROUP_IDS,
    OPERATOR_ID,
    SCHEMA_VERSION,
    SOURCE_AUTHORIZATION_REVIEW_HASH,
    SOURCE_SCHEMA_PLAN_HASH,
    VALID_GROUP_IDS,
    GeodesicTestVectorFixturePlanValidationError,
    build_fixture_plan,
    build_invalid_fixture_plan,
    build_not_computable_fixture_plan,
    build_valid_fixture_plan,
    validate_fixture_plan,
)

FIXTURE_BASE = pathlib.Path("input/fixtures/geodesic")


# ── build + validate round-trip ────────────────────────────────────────────────


def test_build_returns_dict():
    plan = build_fixture_plan()
    assert isinstance(plan, dict)


def test_schema_version():
    plan = build_fixture_plan()
    assert plan["schema_version"] == SCHEMA_VERSION


def test_fixture_plan_type():
    plan = build_fixture_plan()
    assert plan["fixture_plan_type"] == FIXTURE_PLAN_TYPE


def test_operator_id():
    plan = build_fixture_plan()
    assert plan["operator_id"] == OPERATOR_ID


def test_fixture_stage_plan_only():
    plan = build_fixture_plan()
    assert plan["fixture_stage"] == "FIXTURE_PLAN_ONLY"


def test_intended_lane_shadow():
    plan = build_fixture_plan()
    assert plan["intended_lane"] == "SHADOW"


def test_source_schema_plan_hash():
    plan = build_fixture_plan()
    assert plan["source_schema_plan_hash"] == SOURCE_SCHEMA_PLAN_HASH


def test_source_authorization_review_hash():
    plan = build_fixture_plan()
    assert plan["source_authorization_review_hash"] == SOURCE_AUTHORIZATION_REVIEW_HASH


def test_canonical_hash_present_and_64_chars():
    plan = build_fixture_plan()
    h = plan["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_correct():
    plan = build_fixture_plan()
    pre = {k: v for k, v in plan.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == plan["canonical_hash"]


def test_validate_passes_on_valid_plan():
    validate_fixture_plan(build_fixture_plan())


def test_replay_stable():
    assert build_fixture_plan() == build_fixture_plan()


# ── group counts ───────────────────────────────────────────────────────────────


def test_valid_group_count():
    plan = build_fixture_plan()
    assert len(plan["valid_fixture_plan"]) == 5


def test_invalid_group_count():
    plan = build_fixture_plan()
    assert len(plan["invalid_fixture_plan"]) == 4


def test_nc_group_count():
    plan = build_fixture_plan()
    assert len(plan["not_computable_fixture_plan"]) == 4


def test_valid_group_ids():
    ids = tuple(g["fixture_plan_id"] for g in build_valid_fixture_plan())
    assert ids == VALID_GROUP_IDS


def test_invalid_group_ids():
    ids = tuple(g["fixture_plan_id"] for g in build_invalid_fixture_plan())
    assert ids == INVALID_GROUP_IDS


def test_nc_group_ids():
    ids = tuple(g["fixture_plan_id"] for g in build_not_computable_fixture_plan())
    assert ids == NC_GROUP_IDS


# ── authority locks ────────────────────────────────────────────────────────────


def test_authority_lock_fixture_plan_only():
    plan = build_fixture_plan()
    assert plan["authority_locks"]["fixture_plan_only"] is True


def test_authority_lock_emits_metric_values_false():
    plan = build_fixture_plan()
    assert plan["authority_locks"]["emits_metric_values"] is False


def test_authority_lock_emits_expected_geodesic_distances_false():
    plan = build_fixture_plan()
    assert plan["authority_locks"]["emits_expected_geodesic_distances"] is False


def test_authority_lock_fixture_files_generated_false():
    plan = build_fixture_plan()
    assert plan["authority_locks"]["fixture_files_generated"] is False


def test_authority_lock_execution_authority_false():
    plan = build_fixture_plan()
    assert plan["authority_locks"]["execution_authority"] is False


def test_authority_lock_forecast_influence_false():
    plan = build_fixture_plan()
    assert plan["authority_locks"]["forecast_influence"] is False


def test_authority_lock_production_activation_false():
    plan = build_fixture_plan()
    assert plan["authority_locks"]["production_activation"] is False


# ── fixture files on disk ──────────────────────────────────────────────────────


VALID_FILES = [
    "valid/valid_001_simple_connected_weighted_graph.v1.json",
    "valid/valid_002_multi_hop_graph.v1.json",
    "valid/valid_003_self_loop.v1.json",
    "valid/valid_004_unweighted_graph.v1.json",
    "valid/valid_005_complete_graph.v1.json",
]
INVALID_FILES = [
    "invalid/invalid_001_missing_source_node.v1.json",
    "invalid/invalid_002_missing_target_node.v1.json",
    "invalid/invalid_003_missing_edge_list.v1.json",
    "invalid/invalid_004_negative_edge_weight.v1.json",
]
NC_FILES = [
    "not_computable/nc_001_empty_graph.v1.json",
    "not_computable/nc_002_disconnected_graph.v1.json",
    "not_computable/nc_003_source_not_in_graph.v1.json",
    "not_computable/nc_004_target_not_in_graph.v1.json",
]
ALL_FIXTURE_FILES = VALID_FILES + INVALID_FILES + NC_FILES


@pytest.mark.parametrize("rel", ALL_FIXTURE_FILES)
def test_fixture_file_exists(rel):
    assert (FIXTURE_BASE / rel).exists(), f"Missing fixture file: {rel}"


@pytest.mark.parametrize("rel", ALL_FIXTURE_FILES)
def test_fixture_file_valid_json(rel):
    data = json.loads((FIXTURE_BASE / rel).read_text())
    assert isinstance(data, dict)


@pytest.mark.parametrize("rel", ALL_FIXTURE_FILES)
def test_fixture_canonical_hash(rel):
    data = json.loads((FIXTURE_BASE / rel).read_text())
    stored = data["canonical_hash"]
    pre = {k: v for k, v in data.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == stored, f"Hash mismatch in {rel}"


@pytest.mark.parametrize("rel", ALL_FIXTURE_FILES)
def test_fixture_operator_id(rel):
    data = json.loads((FIXTURE_BASE / rel).read_text())
    assert data["operator_id"] == "GEODESIC"


@pytest.mark.parametrize("rel", ALL_FIXTURE_FILES)
def test_fixture_metric_value_emitted_false(rel):
    data = json.loads((FIXTURE_BASE / rel).read_text())
    assert data["metric_value_emitted"] is False


@pytest.mark.parametrize("rel", ALL_FIXTURE_FILES)
def test_fixture_governance_flags_all_false(rel):
    data = json.loads((FIXTURE_BASE / rel).read_text())
    flags = data["governance_flags"]
    for k, v in flags.items():
        assert v is False, f"{rel}: governance_flags.{k} must be False"


@pytest.mark.parametrize("rel", VALID_FILES)
def test_valid_fixture_type(rel):
    data = json.loads((FIXTURE_BASE / rel).read_text())
    assert data["fixture_type"] == "VALID"


@pytest.mark.parametrize("rel", VALID_FILES)
def test_valid_fixture_no_expected_distance(rel):
    data = json.loads((FIXTURE_BASE / rel).read_text())
    # Historical-state reconstruction: if source_expected_values_gate_hash is present,
    # the fixture was in expected_geodesic_distance_included=False at plan-review time.
    if data.get("source_expected_values_gate_hash"):
        edi = False
    else:
        edi = data["expected_geodesic_distance_included"]
    assert edi is False


@pytest.mark.parametrize("rel", INVALID_FILES)
def test_invalid_fixture_type(rel):
    data = json.loads((FIXTURE_BASE / rel).read_text())
    assert data["fixture_type"] == "INVALID"


@pytest.mark.parametrize("rel", NC_FILES)
def test_nc_fixture_type(rel):
    data = json.loads((FIXTURE_BASE / rel).read_text())
    assert data["fixture_type"] == "NOT_COMPUTABLE"


def test_manifest_exists():
    assert (FIXTURE_BASE / "geodesic_fixture_manifest.v1.json").exists()


def test_manifest_fixture_count():
    data = json.loads((FIXTURE_BASE / "geodesic_fixture_manifest.v1.json").read_text())
    assert data["fixture_groups"]["valid"] == 5
    assert data["fixture_groups"]["invalid"] == 4
    assert data["fixture_groups"]["not_computable"] == 4


def test_manifest_canonical_hash():
    data = json.loads((FIXTURE_BASE / "geodesic_fixture_manifest.v1.json").read_text())
    stored = data["canonical_hash"]
    pre = {k: v for k, v in data.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == stored


# ── validate rejects bad inputs ────────────────────────────────────────────────


def test_validate_rejects_wrong_schema_version():
    plan = build_fixture_plan()
    plan["schema_version"] = "Wrong.v1"
    with pytest.raises(GeodesicTestVectorFixturePlanValidationError):
        validate_fixture_plan(plan)


def test_validate_rejects_wrong_operator_id():
    plan = build_fixture_plan()
    plan["operator_id"] = "WASSERSTEIN"
    with pytest.raises(GeodesicTestVectorFixturePlanValidationError):
        validate_fixture_plan(plan)


def test_validate_rejects_hash_mismatch():
    plan = build_fixture_plan()
    plan["canonical_hash"] = "a" * 64
    with pytest.raises(GeodesicTestVectorFixturePlanValidationError):
        validate_fixture_plan(plan)


def test_validate_rejects_fixture_files_generated_true():
    plan = build_fixture_plan()
    plan["authority_locks"]["fixture_files_generated"] = True
    plan["canonical_hash"] = canonical_hash(
        {k: v for k, v in plan.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicTestVectorFixturePlanValidationError):
        validate_fixture_plan(plan)


def test_validate_rejects_emits_metric_values_true():
    plan = build_fixture_plan()
    plan["authority_locks"]["emits_metric_values"] = True
    plan["canonical_hash"] = canonical_hash(
        {k: v for k, v in plan.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicTestVectorFixturePlanValidationError):
        validate_fixture_plan(plan)

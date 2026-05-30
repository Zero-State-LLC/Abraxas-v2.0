from __future__ import annotations

import json
import pathlib

import pytest

from core.canonical.json import canonical_hash
from core.geodesic_expected_values_addition_receipt import (
    ADDITION_STAGE,
    DECLARED_EXPECTED_VALUES,
    RECEIPT_ID,
    RECEIPT_STATUS,
    SCHEMA_VERSION,
    SOURCE_EXPECTED_VALUES_GATE_HASH,
    VALID_FIXTURE_IDS,
    GeodesicExpectedValuesAdditionReceiptValidationError,
    build_addition_receipt,
    validate_addition_receipt,
)

FIXTURE_BASE = pathlib.Path("input/fixtures/geodesic")
VALID_FILES = sorted((FIXTURE_BASE / "valid").glob("*.json"))
INVALID_FILES = sorted((FIXTURE_BASE / "invalid").glob("*.json"))
NC_FILES = sorted((FIXTURE_BASE / "not_computable").glob("*.json"))


# ── build + validate round-trip ────────────────────────────────────────────────


def test_build_returns_dict():
    assert isinstance(build_addition_receipt(), dict)


def test_schema_version():
    assert build_addition_receipt()["schema_version"] == SCHEMA_VERSION


def test_receipt_id():
    assert build_addition_receipt()["receipt_id"] == RECEIPT_ID


def test_receipt_status():
    assert build_addition_receipt()["receipt_status"] == RECEIPT_STATUS


def test_addition_stage():
    assert build_addition_receipt()["addition_stage"] == ADDITION_STAGE


def test_intended_lane_shadow():
    assert build_addition_receipt()["intended_lane"] == "SHADOW"


def test_source_gate_hash():
    assert build_addition_receipt()["source_expected_values_gate_hash"] == SOURCE_EXPECTED_VALUES_GATE_HASH


def test_canonical_hash_present_and_64_chars():
    h = build_addition_receipt()["canonical_hash"]
    assert isinstance(h, str) and len(h) == 64


def test_canonical_hash_correct():
    receipt = build_addition_receipt()
    pre = {k: v for k, v in receipt.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == receipt["canonical_hash"]


def test_validate_passes():
    validate_addition_receipt(build_addition_receipt())


def test_replay_stable():
    assert build_addition_receipt() == build_addition_receipt()


def test_recommended_next_step():
    assert build_addition_receipt()["recommended_next_step"] == "GEODESIC_EXPECTED_VALUES_COMPLETE_REVIEW"


# ── modified fixture manifest ──────────────────────────────────────────────────


def test_modified_fixture_count():
    mfm = build_addition_receipt()["modified_fixture_manifest"]
    assert mfm["modified_fixture_count"] == 5


def test_unmodified_invalid_count():
    mfm = build_addition_receipt()["modified_fixture_manifest"]
    assert mfm["unmodified_invalid_count"] == 4


def test_unmodified_nc_count():
    mfm = build_addition_receipt()["modified_fixture_manifest"]
    assert mfm["unmodified_not_computable_count"] == 4


def test_total_fixture_count():
    mfm = build_addition_receipt()["modified_fixture_manifest"]
    assert mfm["total_fixture_count"] == 13


def test_invalid_fixtures_not_modified():
    mfm = build_addition_receipt()["modified_fixture_manifest"]
    assert mfm["invalid_fixtures_modified"] is False


def test_nc_fixtures_not_modified():
    mfm = build_addition_receipt()["modified_fixture_manifest"]
    assert mfm["not_computable_fixtures_modified"] is False


def test_fixture_files_modified_true():
    mfm = build_addition_receipt()["modified_fixture_manifest"]
    assert mfm["fixture_files_modified"] is True


# ── expected value summary ─────────────────────────────────────────────────────


def test_expected_value_summary_count():
    evs = build_addition_receipt()["expected_value_summary"]
    assert len(evs) == 5


def test_expected_value_summary_ids():
    evs = build_addition_receipt()["expected_value_summary"]
    ids = {e["fixture_id"] for e in evs}
    assert ids == set(VALID_FIXTURE_IDS)


def test_expected_value_summary_values():
    evs = build_addition_receipt()["expected_value_summary"]
    val_map = {e["fixture_id"]: e["expected_geodesic_distance"] for e in evs}
    for fid, expected in DECLARED_EXPECTED_VALUES.items():
        assert val_map[fid] == expected, f"{fid}: {val_map[fid]} != {expected}"


def test_expected_value_summary_included_true():
    evs = build_addition_receipt()["expected_value_summary"]
    for entry in evs:
        assert entry["expected_geodesic_distance_included"] is True


# ── exclusion reviews ──────────────────────────────────────────────────────────


def test_invalid_exclusion_count():
    exc = build_addition_receipt()["invalid_fixture_exclusion_review"]
    assert exc["excluded_fixture_count"] == 4


def test_invalid_exclusion_no_distance():
    exc = build_addition_receipt()["invalid_fixture_exclusion_review"]
    assert exc["all_excluded_have_no_expected_distance"] is True


def test_invalid_exclusion_not_modified():
    exc = build_addition_receipt()["invalid_fixture_exclusion_review"]
    assert exc["modification_applied"] is False


def test_nc_exclusion_count():
    exc = build_addition_receipt()["not_computable_fixture_exclusion_review"]
    assert exc["excluded_fixture_count"] == 4


def test_nc_exclusion_no_distance():
    exc = build_addition_receipt()["not_computable_fixture_exclusion_review"]
    assert exc["all_excluded_have_no_expected_distance"] is True


def test_nc_exclusion_not_modified():
    exc = build_addition_receipt()["not_computable_fixture_exclusion_review"]
    assert exc["modification_applied"] is False


# ── block reviews ──────────────────────────────────────────────────────────────


def test_no_metric_emission():
    rev = build_addition_receipt()["no_metric_emission_review"]
    assert rev["emits_metric_values"] is False
    assert rev["metric_emission_confirmed_absent"] is True


def test_no_forecast_influence():
    rev = build_addition_receipt()["no_forecast_influence_review"]
    assert rev["forecast_influence"] is False
    assert rev["forecast_confirmed_absent"] is True


# ── blocked scopes ─────────────────────────────────────────────────────────────


def test_blocked_scopes_all_false():
    bs = build_addition_receipt()["blocked_scopes"]
    for key, val in bs.items():
        assert val is False, f"blocked_scopes.{key} must be False"


# ── authority locks ────────────────────────────────────────────────────────────


def test_authority_lock_advisory_only():
    assert build_addition_receipt()["authority_locks"]["advisory_only"] is True


def test_authority_lock_shadow_lane_only():
    assert build_addition_receipt()["authority_locks"]["shadow_lane_only"] is True


def test_authority_lock_expected_values_addition_only():
    assert build_addition_receipt()["authority_locks"]["expected_values_addition_only"] is True


def test_authority_lock_expected_geodesic_distances_authorized():
    assert build_addition_receipt()["authority_locks"]["expected_geodesic_distances_authorized"] is True


def test_authority_lock_emits_metric_values_false():
    assert build_addition_receipt()["authority_locks"]["emits_metric_values"] is False


def test_authority_lock_forecast_influence_false():
    assert build_addition_receipt()["authority_locks"]["forecast_influence"] is False


def test_authority_lock_p43_surface_lanes_authorized_false():
    assert build_addition_receipt()["authority_locks"]["p43_surface_lanes_authorized"] is False


def test_authority_lock_production_activation_false():
    assert build_addition_receipt()["authority_locks"]["production_activation"] is False


def test_authority_lock_execution_authority_false():
    assert build_addition_receipt()["authority_locks"]["execution_authority"] is False


# ── live valid fixture state checks ───────────────────────────────────────────


@pytest.mark.parametrize("fpath", VALID_FILES)
def test_valid_fixture_expected_distance_included(fpath):
    d = json.loads(fpath.read_text())
    assert d["expected_geodesic_distance_included"] is True, f"{fpath.name}: flag must be True"


@pytest.mark.parametrize("fpath", VALID_FILES)
def test_valid_fixture_expected_distance_declared(fpath):
    d = json.loads(fpath.read_text())
    assert d["expected_geodesic_distance"] is not None
    assert isinstance(d["expected_geodesic_distance"], float)


@pytest.mark.parametrize("fpath", VALID_FILES)
def test_valid_fixture_expected_distance_matches_declared(fpath):
    d = json.loads(fpath.read_text())
    fid = d["fixture_id"]
    assert d["expected_geodesic_distance"] == DECLARED_EXPECTED_VALUES[fid]


@pytest.mark.parametrize("fpath", VALID_FILES)
def test_valid_fixture_gate_hash_present(fpath):
    d = json.loads(fpath.read_text())
    assert d.get("source_expected_values_gate_hash") == SOURCE_EXPECTED_VALUES_GATE_HASH


@pytest.mark.parametrize("fpath", VALID_FILES)
def test_valid_fixture_canonical_hash_still_valid(fpath):
    d = json.loads(fpath.read_text())
    stored = d["canonical_hash"]
    pre = {k: v for k, v in d.items() if k != "canonical_hash"}
    assert canonical_hash(pre) == stored, f"Hash mismatch in {fpath.name}"


@pytest.mark.parametrize("fpath", INVALID_FILES)
def test_invalid_fixture_no_expected_distance(fpath):
    d = json.loads(fpath.read_text())
    assert d.get("expected_geodesic_distance_included") is False


@pytest.mark.parametrize("fpath", NC_FILES)
def test_nc_fixture_no_expected_distance(fpath):
    d = json.loads(fpath.read_text())
    assert d.get("expected_geodesic_distance_included") is False


# ── validate rejects bad inputs ────────────────────────────────────────────────


def test_validate_rejects_wrong_schema_version():
    receipt = build_addition_receipt()
    receipt["schema_version"] = "Wrong.v1"
    with pytest.raises(GeodesicExpectedValuesAdditionReceiptValidationError):
        validate_addition_receipt(receipt)


def test_validate_rejects_wrong_receipt_status():
    receipt = build_addition_receipt()
    receipt["receipt_status"] = "WRONG"
    with pytest.raises(GeodesicExpectedValuesAdditionReceiptValidationError):
        validate_addition_receipt(receipt)


def test_validate_rejects_hash_mismatch():
    receipt = build_addition_receipt()
    receipt["canonical_hash"] = "a" * 64
    with pytest.raises(GeodesicExpectedValuesAdditionReceiptValidationError):
        validate_addition_receipt(receipt)


def test_validate_rejects_emits_metric_values_true():
    receipt = build_addition_receipt()
    receipt["authority_locks"]["emits_metric_values"] = True
    receipt["canonical_hash"] = canonical_hash(
        {k: v for k, v in receipt.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicExpectedValuesAdditionReceiptValidationError):
        validate_addition_receipt(receipt)


def test_validate_rejects_wrong_gate_hash():
    receipt = build_addition_receipt()
    receipt["source_expected_values_gate_hash"] = "b" * 64
    receipt["canonical_hash"] = canonical_hash(
        {k: v for k, v in receipt.items() if k != "canonical_hash"}
    )
    with pytest.raises(GeodesicExpectedValuesAdditionReceiptValidationError):
        validate_addition_receipt(receipt)

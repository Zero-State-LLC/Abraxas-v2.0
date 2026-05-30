"""Tests for TRANSPORT test vector fixture corpus builder and disk artifacts."""
from __future__ import annotations

import pytest

from core.transport_test_vector_fixture_corpus import (
    ALL_FIXTURE_IDS,
    FIXTURE_BASE_PATH,
    FIXTURE_IDS_INVALID,
    FIXTURE_IDS_NC,
    FIXTURE_IDS_VALID,
    SCHEMA_VERSION,
    SOURCE_FIXTURE_PLAN_HASH,
    SOURCE_IMPLEMENTATION_GATE_HASH,
    TransportFixtureCorpusError,
    build_all_fixtures,
    build_single_fixture,
    validate_all_fixtures,
    validate_fixture_document,
)


class TestBuildAllFixtures:
    def test_returns_15_fixtures(self) -> None:
        fixtures = build_all_fixtures()
        assert len(fixtures) == 15

    def test_ordering_matches_all_fixture_ids(self) -> None:
        fixtures = build_all_fixtures()
        ids = tuple(f["fixture_id"] for f in fixtures)
        assert ids == ALL_FIXTURE_IDS

    def test_valid_first_then_invalid_then_nc(self) -> None:
        fixtures = build_all_fixtures()
        types = [f["fixture_type"] for f in fixtures]
        assert types[:6] == ["VALID"] * 6
        assert types[6:10] == ["INVALID"] * 4
        assert types[10:] == ["NOT_COMPUTABLE"] * 5

    def test_all_have_schema_version(self) -> None:
        fixtures = build_all_fixtures()
        for f in fixtures:
            assert f["schema_version"] == SCHEMA_VERSION

    def test_all_have_64_char_canonical_hash(self) -> None:
        fixtures = build_all_fixtures()
        for f in fixtures:
            h = f.get("canonical_hash", "")
            assert isinstance(h, str), f["fixture_id"]
            assert len(h) == 64, f["fixture_id"]

    def test_all_have_metric_value_emitted_false(self) -> None:
        fixtures = build_all_fixtures()
        for f in fixtures:
            assert f["metric_value_emitted"] is False, f["fixture_id"]

    def test_all_have_fixture_creation_authorized_true(self) -> None:
        fixtures = build_all_fixtures()
        for f in fixtures:
            assert f["fixture_creation_authorized"] is True, f["fixture_id"]

    def test_all_have_intended_lane_shadow(self) -> None:
        fixtures = build_all_fixtures()
        for f in fixtures:
            assert f["intended_lane"] == "SHADOW", f["fixture_id"]

    def test_all_bind_source_fixture_plan_hash(self) -> None:
        fixtures = build_all_fixtures()
        for f in fixtures:
            assert f["source_fixture_plan_hash"] == SOURCE_FIXTURE_PLAN_HASH

    def test_all_bind_source_implementation_gate_hash(self) -> None:
        fixtures = build_all_fixtures()
        for f in fixtures:
            assert f["source_implementation_gate_hash"] == SOURCE_IMPLEMENTATION_GATE_HASH

    def test_all_hashes_distinct(self) -> None:
        fixtures = build_all_fixtures()
        hashes = [f["canonical_hash"] for f in fixtures]
        assert len(set(hashes)) == 15, "canonical hashes must all be distinct"

    def test_deterministic_repeated_build(self) -> None:
        a = build_all_fixtures()
        b = build_all_fixtures()
        for fa, fb in zip(a, b):
            assert fa["canonical_hash"] == fb["canonical_hash"], fa["fixture_id"]


class TestValidFixtures:
    def setup_method(self) -> None:
        all_f = build_all_fixtures()
        self.valid = [f for f in all_f if f["fixture_type"] == "VALID"]

    def test_count_is_6(self) -> None:
        assert len(self.valid) == 6

    def test_ids_match(self) -> None:
        ids = tuple(f["fixture_id"] for f in self.valid)
        assert ids == FIXTURE_IDS_VALID

    def test_all_have_expected_distance_included_true(self) -> None:
        for f in self.valid:
            assert f["expected_transport_distance_included"] is True, f["fixture_id"]

    def test_expected_distances(self) -> None:
        expected = {
            "tv-valid-001": 0.0,
            "tv-valid-002": 2.0,
            "tv-valid-003": 2.5,
            "tv-valid-004": 2.5,
            "tv-valid-005": 3.0,
            "tv-valid-006": 0.0,
        }
        for f in self.valid:
            assert f["expected_transport_distance"] == expected[f["fixture_id"]], (
                f"wrong expected distance for {f['fixture_id']}"
            )

    def test_all_have_supply_demand_cost_matrix(self) -> None:
        for f in self.valid:
            inp = f["input"]
            assert "supply" in inp, f["fixture_id"]
            assert "demand" in inp, f["fixture_id"]
            assert "cost_matrix" in inp, f["fixture_id"]

    def test_all_balanced(self) -> None:
        for f in self.valid:
            inp = f["input"]
            supply = [x for x in inp["supply"] if x is not None]
            demand = [x for x in inp["demand"] if x is not None]
            assert abs(sum(supply) - sum(demand)) < 1e-12, (
                f"unbalanced: {f['fixture_id']}"
            )

    def test_cost_matrix_shape_matches_supply_demand(self) -> None:
        for f in self.valid:
            inp = f["input"]
            n_s = len(inp["supply"])
            n_d = len(inp["demand"])
            cm = inp["cost_matrix"]
            assert len(cm) == n_s, f["fixture_id"]
            for row in cm:
                assert len(row) == n_d, f["fixture_id"]

    def test_all_have_closed_form_derivation(self) -> None:
        for f in self.valid:
            assert f.get("expected_value_derivation") == "closed_form_trivial"

    def test_tv_valid_001_diagonal_is_zero(self) -> None:
        f = build_single_fixture("tv-valid-001")
        cm = f["input"]["cost_matrix"]
        assert cm[0][0] == 0.0
        assert cm[1][1] == 0.0

    def test_tv_valid_002_off_diagonal_is_two(self) -> None:
        f = build_single_fixture("tv-valid-002")
        cm = f["input"]["cost_matrix"]
        assert cm[0][1] == 2.0
        assert cm[1][0] == 2.0

    def test_tv_valid_003_1x4_shape(self) -> None:
        f = build_single_fixture("tv-valid-003")
        assert len(f["input"]["supply"]) == 1
        assert len(f["input"]["demand"]) == 4
        assert len(f["input"]["cost_matrix"]) == 1
        assert len(f["input"]["cost_matrix"][0]) == 4

    def test_tv_valid_004_4x1_shape(self) -> None:
        f = build_single_fixture("tv-valid-004")
        assert len(f["input"]["supply"]) == 4
        assert len(f["input"]["demand"]) == 1
        assert len(f["input"]["cost_matrix"]) == 4
        for row in f["input"]["cost_matrix"]:
            assert len(row) == 1

    def test_tv_valid_005_1x1_cost_3(self) -> None:
        f = build_single_fixture("tv-valid-005")
        assert f["input"]["cost_matrix"] == [[3.0]]

    def test_tv_valid_006_diagonal_zero_3x3(self) -> None:
        f = build_single_fixture("tv-valid-006")
        cm = f["input"]["cost_matrix"]
        assert cm[0][0] == 0.0
        assert cm[1][1] == 0.0
        assert cm[2][2] == 0.0


class TestInvalidFixtures:
    def setup_method(self) -> None:
        all_f = build_all_fixtures()
        self.invalid = [f for f in all_f if f["fixture_type"] == "INVALID"]

    def test_count_is_4(self) -> None:
        assert len(self.invalid) == 4

    def test_ids_match(self) -> None:
        ids = tuple(f["fixture_id"] for f in self.invalid)
        assert ids == FIXTURE_IDS_INVALID

    def test_all_have_expected_distance_included_false(self) -> None:
        for f in self.invalid:
            assert f["expected_transport_distance_included"] is False, f["fixture_id"]

    def test_all_have_rejection_reason(self) -> None:
        for f in self.invalid:
            assert isinstance(f.get("rejection_reason"), str)
            assert len(f["rejection_reason"]) > 0

    def test_all_rejection_reasons_start_with_invalid_input(self) -> None:
        for f in self.invalid:
            assert f["rejection_reason"].startswith("INVALID_INPUT:"), f["fixture_id"]

    def test_tv_invalid_001_missing_supply(self) -> None:
        f = build_single_fixture("tv-invalid-001")
        assert "supply" not in f["input"]
        assert "demand" in f["input"]

    def test_tv_invalid_002_missing_demand(self) -> None:
        f = build_single_fixture("tv-invalid-002")
        assert "demand" not in f["input"]
        assert "supply" in f["input"]

    def test_tv_invalid_003_missing_cost_matrix(self) -> None:
        f = build_single_fixture("tv-invalid-003")
        assert "cost_matrix" not in f["input"]
        assert "supply" in f["input"]
        assert "demand" in f["input"]

    def test_tv_invalid_004_shape_mismatch(self) -> None:
        f = build_single_fixture("tv-invalid-004")
        supply = f["input"]["supply"]
        demand = f["input"]["demand"]
        cm = f["input"]["cost_matrix"]
        assert len(cm) == len(supply)
        assert len(cm[0]) != len(demand)


class TestNotComputableFixtures:
    def setup_method(self) -> None:
        all_f = build_all_fixtures()
        self.nc = [f for f in all_f if f["fixture_type"] == "NOT_COMPUTABLE"]

    def test_count_is_5(self) -> None:
        assert len(self.nc) == 5

    def test_ids_match(self) -> None:
        ids = tuple(f["fixture_id"] for f in self.nc)
        assert ids == FIXTURE_IDS_NC

    def test_all_have_expected_distance_included_false(self) -> None:
        for f in self.nc:
            assert f["expected_transport_distance_included"] is False, f["fixture_id"]

    def test_all_have_not_computable_reason(self) -> None:
        for f in self.nc:
            assert isinstance(f.get("not_computable_reason"), str)
            assert len(f["not_computable_reason"]) > 0

    def test_all_have_rejection_reason(self) -> None:
        for f in self.nc:
            assert isinstance(f.get("rejection_reason"), str)
            assert f["rejection_reason"].startswith("NOT_COMPUTABLE:"), f["fixture_id"]

    def test_tv_nc_001_unbalanced(self) -> None:
        f = build_single_fixture("tv-nc-001")
        assert f["not_computable_reason"] == "UNBALANCED_SUPPLY_DEMAND"
        s = sum(f["input"]["supply"])
        d = sum(f["input"]["demand"])
        assert abs(s - d) > 0.0

    def test_tv_nc_002_negative_supply(self) -> None:
        f = build_single_fixture("tv-nc-002")
        assert f["not_computable_reason"] == "NEGATIVE_SUPPLY_VALUE"
        assert any(x < 0 for x in f["input"]["supply"] if x is not None)

    def test_tv_nc_003_negative_cost(self) -> None:
        f = build_single_fixture("tv-nc-003")
        assert f["not_computable_reason"] == "NEGATIVE_COST_VALUE"
        flat = [c for row in f["input"]["cost_matrix"] for c in row if c is not None]
        assert any(c < 0 for c in flat)

    def test_tv_nc_004_empty_supply(self) -> None:
        f = build_single_fixture("tv-nc-004")
        assert f["not_computable_reason"] == "EMPTY_SUPPLY_VECTOR"
        assert f["input"]["supply"] == []

    def test_tv_nc_005_non_finite_supply(self) -> None:
        f = build_single_fixture("tv-nc-005")
        assert f["not_computable_reason"] == "NON_FINITE_SUPPLY_VALUE"
        assert None in f["input"]["supply"]
        assert "non_finite_marker" in f


class TestValidateFixtureDocument:
    def test_valid_fixture_passes(self) -> None:
        f = build_single_fixture("tv-valid-001")
        validate_fixture_document(f)

    def test_invalid_fixture_passes(self) -> None:
        f = build_single_fixture("tv-invalid-001")
        validate_fixture_document(f)

    def test_nc_fixture_passes(self) -> None:
        f = build_single_fixture("tv-nc-001")
        validate_fixture_document(f)

    def test_wrong_schema_version_raises(self) -> None:
        f = build_single_fixture("tv-valid-001")
        f = {**f, "schema_version": "Wrong.v1"}
        with pytest.raises(TransportFixtureCorpusError):
            validate_fixture_document(f)

    def test_tampered_hash_raises(self) -> None:
        f = build_single_fixture("tv-valid-001")
        f = {**f, "canonical_hash": "a" * 64}
        with pytest.raises(TransportFixtureCorpusError):
            validate_fixture_document(f)

    def test_wrong_plan_hash_raises(self) -> None:
        f = build_single_fixture("tv-valid-001")
        f = dict(f)
        f["source_fixture_plan_hash"] = "b" * 64
        with pytest.raises(TransportFixtureCorpusError):
            validate_fixture_document(f)

    def test_metric_value_emitted_true_raises(self) -> None:
        from core.canonical.json import canonical_dumps, canonical_hash
        f = build_single_fixture("tv-valid-001")
        pre = {k: v for k, v in f.items() if k != "canonical_hash"}
        pre["metric_value_emitted"] = True
        h = canonical_hash(canonical_dumps(pre))
        bad = {**pre, "canonical_hash": h}
        with pytest.raises(TransportFixtureCorpusError):
            validate_fixture_document(bad)


class TestValidateAllFixtures:
    def test_passes_for_built_corpus(self) -> None:
        fixtures = build_all_fixtures()
        validate_all_fixtures(fixtures)

    def test_raises_wrong_count(self) -> None:
        fixtures = build_all_fixtures()[:14]
        with pytest.raises(TransportFixtureCorpusError):
            validate_all_fixtures(fixtures)

    def test_raises_wrong_ordering(self) -> None:
        fixtures = build_all_fixtures()
        reordered = fixtures[1:] + [fixtures[0]]
        with pytest.raises(TransportFixtureCorpusError):
            validate_all_fixtures(reordered)


class TestDiskArtifacts:
    """These tests require the fixture runner to have been executed first."""

    def test_fixture_directory_exists(self) -> None:
        assert FIXTURE_BASE_PATH.is_dir(), (
            f"fixture directory {FIXTURE_BASE_PATH} does not exist; "
            "run scripts/run_transport_test_vector_fixture_corpus.py first"
        )

    @pytest.mark.parametrize("fixture_id", ALL_FIXTURE_IDS)
    def test_fixture_file_exists(self, fixture_id: str) -> None:
        path = FIXTURE_BASE_PATH / f"{fixture_id}.json"
        assert path.exists(), f"fixture file missing: {path}"

    @pytest.mark.parametrize("fixture_id", ALL_FIXTURE_IDS)
    def test_fixture_file_validates(self, fixture_id: str) -> None:
        from core.transport_test_vector_fixture_corpus import load_fixture_from_disk
        doc = load_fixture_from_disk(fixture_id)
        validate_fixture_document(doc)

    def test_all_disk_fixtures_validate(self) -> None:
        from core.transport_test_vector_fixture_corpus import load_all_fixtures_from_disk
        docs = load_all_fixtures_from_disk()
        validate_all_fixtures(docs)

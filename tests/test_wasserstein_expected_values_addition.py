from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.wasserstein_expected_values_addition import (
    EXPECTED_WASSERSTEIN_DISTANCES,
    INVALID_FIXTURE_IDS,
    NC_FIXTURE_IDS,
    SOURCE_EXPECTED_VALUES_GATE_HASH,
    VALID_FIXTURE_FILES,
    WassersteinExpectedValuesAdditionError,
    build_expected_value_summary,
    build_invalid_fixture_exclusion_review,
    build_modified_fixture_manifest,
    build_no_forecast_influence_review,
    build_no_metric_emission_review,
    build_not_computable_fixture_exclusion_review,
    build_wasserstein_expected_values_addition_receipt,
    compute_wasserstein_expected_values_addition_receipt_hash,
    default_authority_locks,
    default_blocked_scopes,
    serialize_wasserstein_expected_values_addition_receipt,
)


def _payload() -> dict:
    return {
        "receipt_id": "wasserstein_expected_values_addition_receipt_001",
        "intended_lane": "SHADOW",
        "addition_stage": "EXPECTED_VALUES_ADDITION_ONLY",
        "modified_fixture_manifest": build_modified_fixture_manifest(),
        "expected_value_summary": build_expected_value_summary(),
        "invalid_fixture_exclusion_review": build_invalid_fixture_exclusion_review(),
        "not_computable_fixture_exclusion_review": (
            build_not_computable_fixture_exclusion_review()
        ),
        "no_metric_emission_review": build_no_metric_emission_review(),
        "no_forecast_influence_review": build_no_forecast_influence_review(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "WASSERSTEIN_EXPECTED_VALUES_COMPLETE_REVIEW",
        "provenance": {
            "source": "P60_WASSERSTEIN_EXPECTED_VALUES_ADDITION",
            "evidence_refs": [
                "WassersteinExpectedValuesGate.v1:"
                "wasserstein_expected_values_gate_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/wasserstein_expected_values_gate.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Source constants
# ---------------------------------------------------------------------------


def test_source_gate_hash_correct() -> None:
    assert (
        SOURCE_EXPECTED_VALUES_GATE_HASH
        == "21baf9d688ba3ec0590e14355e26d043b48693ac71ecdb0d69da0afcf3b09bb2"
    )


def test_expected_distance_values_correct() -> None:
    assert abs(EXPECTED_WASSERSTEIN_DISTANCES["valid-001"] - 0.4) < 1e-9
    assert abs(EXPECTED_WASSERSTEIN_DISTANCES["valid-002"] - 0.4) < 1e-9
    assert abs(EXPECTED_WASSERSTEIN_DISTANCES["valid-003"] - 0.866025) < 1e-6
    assert abs(EXPECTED_WASSERSTEIN_DISTANCES["valid-004"] - 0.2) < 1e-9
    assert abs(EXPECTED_WASSERSTEIN_DISTANCES["valid-005"]) < 1e-9


def test_valid_fixture_files_all_present() -> None:
    assert len(VALID_FIXTURE_FILES) == 5
    for fpath in VALID_FIXTURE_FILES.values():
        assert Path(fpath).exists(), f"fixture_file_missing:{fpath}"


def test_excluded_fixture_counts() -> None:
    assert len(INVALID_FIXTURE_IDS) == 5
    assert len(NC_FIXTURE_IDS) == 4


# ---------------------------------------------------------------------------
# Fixture file contents after addition
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fixture_id", sorted(EXPECTED_WASSERSTEIN_DISTANCES))
def test_fixture_expected_wasserstein_distance_included(fixture_id: str) -> None:
    data = json.loads(Path(VALID_FIXTURE_FILES[fixture_id]).read_text(encoding="utf-8"))
    assert data["expected_wasserstein_distance_included"] is True


@pytest.mark.parametrize("fixture_id", sorted(EXPECTED_WASSERSTEIN_DISTANCES))
def test_fixture_expected_wasserstein_distance_value(fixture_id: str) -> None:
    data = json.loads(Path(VALID_FIXTURE_FILES[fixture_id]).read_text(encoding="utf-8"))
    expected = EXPECTED_WASSERSTEIN_DISTANCES[fixture_id]
    assert abs(data["expected_wasserstein_distance"] - expected) < 1e-9


@pytest.mark.parametrize("fixture_id", sorted(EXPECTED_WASSERSTEIN_DISTANCES))
def test_fixture_source_gate_hash(fixture_id: str) -> None:
    data = json.loads(Path(VALID_FIXTURE_FILES[fixture_id]).read_text(encoding="utf-8"))
    assert data["source_expected_values_gate_hash"] == SOURCE_EXPECTED_VALUES_GATE_HASH


@pytest.mark.parametrize("fixture_id", sorted(EXPECTED_WASSERSTEIN_DISTANCES))
def test_fixture_metric_value_emitted_false(fixture_id: str) -> None:
    data = json.loads(Path(VALID_FIXTURE_FILES[fixture_id]).read_text(encoding="utf-8"))
    assert data["metric_value_emitted"] is False


@pytest.mark.parametrize("fixture_id", sorted(EXPECTED_WASSERSTEIN_DISTANCES))
def test_fixture_intended_lane_shadow(fixture_id: str) -> None:
    data = json.loads(Path(VALID_FIXTURE_FILES[fixture_id]).read_text(encoding="utf-8"))
    assert data["intended_lane"] == "SHADOW"


# ---------------------------------------------------------------------------
# build_modified_fixture_manifest
# ---------------------------------------------------------------------------


def test_modified_fixture_manifest_count() -> None:
    mfm = build_modified_fixture_manifest()
    assert len(mfm) == 5


def test_modified_fixture_manifest_all_added() -> None:
    for entry in build_modified_fixture_manifest():
        assert entry["addition_status"] == "ADDED"


def test_modified_fixture_manifest_no_metric_emission() -> None:
    for entry in build_modified_fixture_manifest():
        assert entry["metric_value_emitted"] is False


def test_modified_fixture_manifest_shadow_only() -> None:
    for entry in build_modified_fixture_manifest():
        assert entry["shadow_only"] is True


def test_modified_fixture_manifest_gate_hash() -> None:
    for entry in build_modified_fixture_manifest():
        assert (
            entry["source_expected_values_gate_hash"]
            == SOURCE_EXPECTED_VALUES_GATE_HASH
        )


# ---------------------------------------------------------------------------
# build_expected_value_summary
# ---------------------------------------------------------------------------


def test_expected_value_summary_status() -> None:
    evs = build_expected_value_summary()
    assert evs["summary_status"] == "EXPECTED_VALUES_ADDITION_COMPLETE"


def test_expected_value_summary_count() -> None:
    evs = build_expected_value_summary()
    assert evs["total_fixtures_updated"] == 5


def test_expected_value_summary_shadow_only() -> None:
    evs = build_expected_value_summary()
    assert evs["all_additions_shadow_only"] is True
    assert evs["no_metric_emission"] is True


# ---------------------------------------------------------------------------
# Exclusion reviews
# ---------------------------------------------------------------------------


def test_invalid_fixture_exclusion_review_status() -> None:
    r = build_invalid_fixture_exclusion_review()
    assert r["exclusion_status"] == "INVALID_FIXTURES_EXCLUDED_UNCHANGED"


def test_invalid_fixture_exclusion_review_no_addition() -> None:
    r = build_invalid_fixture_exclusion_review()
    assert r["expected_wasserstein_distance_added"] is False
    assert r["fixtures_unchanged"] is True
    assert r["invalid_count"] == 5


def test_not_computable_fixture_exclusion_review_status() -> None:
    r = build_not_computable_fixture_exclusion_review()
    assert r["exclusion_status"] == "NOT_COMPUTABLE_FIXTURES_EXCLUDED_UNCHANGED"


def test_not_computable_fixture_exclusion_review_no_addition() -> None:
    r = build_not_computable_fixture_exclusion_review()
    assert r["expected_wasserstein_distance_added"] is False
    assert r["fixtures_unchanged"] is True
    assert r["not_computable_count"] == 4


# ---------------------------------------------------------------------------
# Review sections
# ---------------------------------------------------------------------------


def test_no_metric_emission_review_confirmed() -> None:
    r = build_no_metric_emission_review()
    assert r["review_status"] == "NO_METRIC_EMISSION_CONFIRMED"
    assert r["emits_metric_values"] is False
    assert r["no_runtime_emission"] is True
    assert r["no_p43_surface_output"] is True


def test_no_forecast_influence_review_confirmed() -> None:
    r = build_no_forecast_influence_review()
    assert r["review_status"] == "NO_FORECAST_INFLUENCE_CONFIRMED"
    assert r["forecast_influence"] is False
    assert r["no_forecast_binding"] is True
    assert r["no_p43_output"] is True


# ---------------------------------------------------------------------------
# Full build
# ---------------------------------------------------------------------------


def test_build_packet_schema_version() -> None:
    pkt = build_wasserstein_expected_values_addition_receipt(_payload())
    assert pkt["schema_version"] == "WassersteinExpectedValuesAdditionReceipt.v1"


def test_build_packet_receipt_type() -> None:
    pkt = build_wasserstein_expected_values_addition_receipt(_payload())
    assert pkt["receipt_type"] == "WASSERSTEIN_EXPECTED_VALUES_ADDITION_RECEIPT"


def test_build_packet_constants() -> None:
    pkt = build_wasserstein_expected_values_addition_receipt(_payload())
    assert pkt["operator_id"] == "WASSERSTEIN"
    assert (
        pkt["source_expected_values_gate_hash"] == SOURCE_EXPECTED_VALUES_GATE_HASH
    )
    assert pkt["intended_lane"] == "SHADOW"
    assert pkt["addition_stage"] == "EXPECTED_VALUES_ADDITION_ONLY"


def test_build_packet_authority_locks_addition_only() -> None:
    pkt = build_wasserstein_expected_values_addition_receipt(_payload())
    assert pkt["authority_locks"]["expected_values_addition_only"] is True


def test_build_packet_expected_wasserstein_distances_authorized() -> None:
    pkt = build_wasserstein_expected_values_addition_receipt(_payload())
    assert pkt["authority_locks"]["expected_wasserstein_distances_authorized"] is True


def test_build_packet_emits_metric_values_false() -> None:
    pkt = build_wasserstein_expected_values_addition_receipt(_payload())
    assert pkt["authority_locks"]["emits_metric_values"] is False


def test_build_packet_execution_authority_false() -> None:
    pkt = build_wasserstein_expected_values_addition_receipt(_payload())
    assert pkt["authority_locks"]["execution_authority"] is False


def test_build_packet_blocked_scopes_all_false() -> None:
    pkt = build_wasserstein_expected_values_addition_receipt(_payload())
    for k, v in pkt["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


def test_build_packet_has_canonical_hash() -> None:
    pkt = build_wasserstein_expected_values_addition_receipt(_payload())
    assert "canonical_hash" in pkt
    assert len(pkt["canonical_hash"]) == 64


def test_build_packet_recommended_next_step() -> None:
    pkt = build_wasserstein_expected_values_addition_receipt(_payload())
    assert pkt["recommended_next_step"] == "WASSERSTEIN_EXPECTED_VALUES_COMPLETE_REVIEW"


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash() -> None:
    a = build_wasserstein_expected_values_addition_receipt(_payload())
    b = build_wasserstein_expected_values_addition_receipt(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_deterministic_serialization() -> None:
    a = build_wasserstein_expected_values_addition_receipt(_payload())
    b = build_wasserstein_expected_values_addition_receipt(_payload())
    assert serialize_wasserstein_expected_values_addition_receipt(
        a
    ) == serialize_wasserstein_expected_values_addition_receipt(b)


def test_hash_excludes_itself() -> None:
    pkt = build_wasserstein_expected_values_addition_receipt(_payload())
    altered = dict(pkt)
    altered["canonical_hash"] = "0" * 64
    assert (
        compute_wasserstein_expected_values_addition_receipt_hash(pkt)
        == compute_wasserstein_expected_values_addition_receipt_hash(altered)
    )


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_expected_values_addition_receipt(_payload())
    b = build_wasserstein_expected_values_addition_receipt(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


# ---------------------------------------------------------------------------
# Validation failures
# ---------------------------------------------------------------------------


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["receipt_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_expected_values_addition_receipt(p)


def test_authority_locks_emits_metric_values_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["emits_metric_values"] = True
    p["authority_locks"] = al
    with pytest.raises(ValueError, match="emits_metric_values_must_be_false"):
        build_wasserstein_expected_values_addition_receipt(p)


def test_expected_values_addition_only_false_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["expected_values_addition_only"] = False
    p["authority_locks"] = al
    with pytest.raises(
        ValueError, match="expected_values_addition_only_must_be_true"
    ):
        build_wasserstein_expected_values_addition_receipt(p)


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    bs = default_blocked_scopes()
    bs["production_activation"] = True
    p["blocked_scopes"] = bs
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_expected_values_addition_receipt(p)


def test_provenance_forbidden_reference_raises() -> None:
    p = _payload()
    p["provenance"]["source"] = "scoring metric-value authority-flag"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_expected_values_addition_receipt(p)


@pytest.mark.parametrize(
    ("field", "value", "err"),
    [
        ("intended_lane", "LIVE", "unknown_intended_lane"),
        ("addition_stage", "ACTIVE", "unknown_addition_stage"),
    ],
)
def test_enum_failures(field: str, value: str, err: str) -> None:
    p = _payload()
    p[field] = value
    with pytest.raises(ValueError, match=err):
        build_wasserstein_expected_values_addition_receipt(p)


def test_manifest_metric_emission_mutation_raises() -> None:
    p = _payload()
    mfm = build_modified_fixture_manifest()
    mfm[0]["metric_value_emitted"] = True
    p["modified_fixture_manifest"] = mfm
    with pytest.raises(
        WassersteinExpectedValuesAdditionError,
        match="fixture_metric_value_emitted_must_be_false",
    ):
        build_wasserstein_expected_values_addition_receipt(p)


def test_invalid_fixture_exclusion_review_mutation_raises() -> None:
    p = _payload()
    r = build_invalid_fixture_exclusion_review()
    r["expected_wasserstein_distance_added"] = True
    p["invalid_fixture_exclusion_review"] = r
    with pytest.raises(
        WassersteinExpectedValuesAdditionError,
        match="invalid_fixtures_must_not_have_expected_distance_added",
    ):
        build_wasserstein_expected_values_addition_receipt(p)

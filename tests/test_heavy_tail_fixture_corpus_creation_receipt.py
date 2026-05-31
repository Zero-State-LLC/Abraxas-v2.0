from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.heavy_tail_fixture_corpus_creation_receipt import (
    FIXTURE_BASE_DIR,
    FIXTURE_CORPUS_PLAN_HASH,
    INVALID_FIXTURE_COUNT,
    LOCKED_FALSE_FLAGS,
    LOCKED_TRUE_FLAGS,
    NOT_COMPUTABLE_FIXTURE_COUNT,
    SOURCE_AUTH_HASH,
    SOURCE_SCHEMA_PLAN_HASH,
    TOTAL_FIXTURE_COUNT,
    VALID_FIXTURE_COUNT,
    HeavyTailFixtureCorpusCreationReceiptValidationError,
    _INVALID_FIXTURE_CORES,
    _NOT_COMPUTABLE_FIXTURE_CORES,
    _VALID_FIXTURE_CORES,
    build_all_fixtures,
    build_fixture_content,
    build_receipt,
    default_authority_lock_review,
    default_blocked_scope_review,
    default_corpus_creation_scope_review,
    default_fixture_corpus_plan_binding,
    default_schema_plan_binding,
    default_source_authorization_binding,
    fixture_path,
    serialize_receipt,
)


def _fixtures() -> list[dict]:
    return build_all_fixtures()


def _payload(fixtures: list[dict] | None = None) -> dict:
    fx = fixtures or _fixtures()
    return {
        "receipt_id": "heavy-tail-fixture-corpus-creation-receipt-test-001",
        "source_authorization_binding": default_source_authorization_binding(),
        "schema_plan_binding": default_schema_plan_binding(),
        "fixture_corpus_plan_binding": default_fixture_corpus_plan_binding(),
        "corpus_creation_scope_review": default_corpus_creation_scope_review(fx),
        "authority_lock_review": default_authority_lock_review(),
        "blocked_scope_review": default_blocked_scope_review(),
        "recommended_next_step": "HEAVY_TAIL_COMPUTATION_RECEIPT",
        "provenance": {
            "source": "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_RECEIPT_TEST",
            "evidence_refs": [
                f"HeavyTailShadowStubImplementationAuthorization.v1:"
                f"heavy_tail_shadow_stub_implementation_authorization_001:"
                f"{SOURCE_AUTH_HASH}",
                f"HeavyTailTestVectorSchemaPlan.v1:"
                f"heavy_tail_test_vector_schema_plan_001:"
                f"{SOURCE_SCHEMA_PLAN_HASH}",
                f"HeavyTailFixtureCorpusCreationPlan.v1:"
                f"heavy_tail_fixture_corpus_creation_plan_001:"
                f"{FIXTURE_CORPUS_PLAN_HASH}",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "heavy_tail_fixture_corpus_creation_receipt.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-31T00:00:00Z",
    }


def test_valid_fixture_core_count() -> None:
    assert len(_VALID_FIXTURE_CORES) == VALID_FIXTURE_COUNT


def test_invalid_fixture_core_count() -> None:
    assert len(_INVALID_FIXTURE_CORES) == INVALID_FIXTURE_COUNT


def test_not_computable_fixture_core_count() -> None:
    assert len(_NOT_COMPUTABLE_FIXTURE_CORES) == NOT_COMPUTABLE_FIXTURE_COUNT


def test_build_all_fixtures_total_count() -> None:
    assert len(_fixtures()) == TOTAL_FIXTURE_COUNT


def test_all_fixture_ids_unique() -> None:
    ids = [f["fixture_id"] for f in _fixtures()]
    assert len(ids) == len(set(ids))


def test_valid_fixture_ids() -> None:
    valid = [f for f in _fixtures() if f["fixture_group"] == "valid"]
    ids = sorted(f["fixture_id"] for f in valid)
    assert ids == ["ht-valid-001", "ht-valid-002", "ht-valid-003",
                   "ht-valid-004", "ht-valid-005", "ht-valid-006"]


def test_invalid_fixture_ids() -> None:
    inv = [f for f in _fixtures() if f["fixture_group"] == "invalid"]
    ids = sorted(f["fixture_id"] for f in inv)
    assert ids == ["ht-invalid-001", "ht-invalid-002", "ht-invalid-003", "ht-invalid-004"]


def test_not_computable_fixture_ids() -> None:
    nc = [f for f in _fixtures() if f["fixture_group"] == "not_computable"]
    ids = sorted(f["fixture_id"] for f in nc)
    assert ids == ["ht-nc-001", "ht-nc-002", "ht-nc-003",
                   "ht-nc-004", "ht-nc-005", "ht-nc-006"]


def test_valid_fixtures_have_computable_status() -> None:
    for f in _fixtures():
        if f["fixture_group"] == "valid":
            assert f["expected_status"] == "COMPUTABLE", f["fixture_id"]


def test_invalid_fixtures_have_invalid_input_or_sentinel_status() -> None:
    allowed = {"INVALID_INPUT", "UNKNOWN"}
    for f in _fixtures():
        if f["fixture_group"] == "invalid":
            assert f["expected_status"] in allowed, (
                f"{f['fixture_id']} unexpected status: {f['expected_status']}"
            )


def test_invalid_fixtures_except_sentinel_have_invalid_input_status() -> None:
    for f in _fixtures():
        if f["fixture_group"] == "invalid" and f["fixture_id"] != "ht-invalid-004":
            assert f["expected_status"] == "INVALID_INPUT", f["fixture_id"]


def test_not_computable_fixtures_have_not_computable_status() -> None:
    for f in _fixtures():
        if f["fixture_group"] == "not_computable":
            assert f["expected_status"] == "NOT_COMPUTABLE", f["fixture_id"]


def test_valid_fixtures_have_tail_index_above_threshold_or_below() -> None:
    valid = [f for f in _fixtures() if f["fixture_group"] == "valid"]
    above = [f for f in valid if f.get("expected_tail_index", 0) > 1.5]
    below = [f for f in valid if f.get("expected_tail_index", 0) <= 1.5]
    assert len(above) >= 3
    assert len(below) >= 1


def test_ht_valid_001_power_law_alpha_2() -> None:
    core = next(c for c in _VALID_FIXTURE_CORES if c["fixture_id"] == "ht-valid-001")
    assert core["alpha"] == 2.0
    assert core["sample_count"] == 20
    assert len(core["sequence_values"]) == 20
    assert core["expected_status"] == "COMPUTABLE"
    assert core["expected_tail_index"] == 2.0
    assert core["expected_moment_summary"]["mean"] == 31.65
    assert core["expected_outcome_reason"] == "POWER_LAW_HEAVY_TAIL_DETECTED"


def test_ht_valid_002_power_law_alpha_3() -> None:
    core = next(c for c in _VALID_FIXTURE_CORES if c["fixture_id"] == "ht-valid-002")
    assert core["alpha"] == 3.0
    assert core["sample_count"] == 20
    assert len(core["sequence_values"]) == 20
    assert core["expected_tail_index"] == 3.0
    assert core["expected_outcome_reason"] == "POWER_LAW_HEAVY_TAIL_DETECTED"


def test_ht_valid_003_light_tail_control() -> None:
    core = next(c for c in _VALID_FIXTURE_CORES if c["fixture_id"] == "ht-valid-003")
    assert core["alpha"] == 5.0
    assert core["expected_tail_index"] == 0.8
    assert core["expected_tail_index"] < core["expected_tail_threshold"]
    assert core["expected_outcome_reason"] == "LIGHT_TAIL_CONTROL"


def test_ht_valid_004_single_outlier() -> None:
    core = next(c for c in _VALID_FIXTURE_CORES if c["fixture_id"] == "ht-valid-004")
    assert max(core["sequence_values"]) == 1000
    assert core["expected_outcome_reason"] == "SINGLE_OUTLIER_DOMINATED"


def test_ht_valid_005_monotone() -> None:
    core = next(c for c in _VALID_FIXTURE_CORES if c["fixture_id"] == "ht-valid-005")
    vals = core["sequence_values"]
    assert vals == sorted(vals, reverse=True)
    assert core["expected_outcome_reason"] == "MONOTONE_RANK_FREQUENCY"


def test_ht_valid_006_equal_values() -> None:
    core = next(c for c in _VALID_FIXTURE_CORES if c["fixture_id"] == "ht-valid-006")
    assert len(set(core["sequence_values"])) == 1
    assert core["expected_tail_index"] == 0.0
    assert core["expected_moment_summary"]["variance"] == 0.0
    assert core["expected_outcome_reason"] == "REPEATED_EQUAL_VALUES"


def test_ht_invalid_001_missing_alpha() -> None:
    core = next(c for c in _INVALID_FIXTURE_CORES if c["fixture_id"] == "ht-invalid-001")
    assert "alpha" not in core
    assert core["expected_status"] == "INVALID_INPUT"
    assert core["expected_outcome_reason"] == "MISSING_ALPHA_FIELD"


def test_ht_invalid_002_missing_sample_count() -> None:
    core = next(c for c in _INVALID_FIXTURE_CORES if c["fixture_id"] == "ht-invalid-002")
    assert "sample_count" not in core
    assert core["expected_status"] == "INVALID_INPUT"


def test_ht_invalid_003_missing_sequence_values() -> None:
    core = next(c for c in _INVALID_FIXTURE_CORES if c["fixture_id"] == "ht-invalid-003")
    assert "sequence_values" not in core
    assert core["expected_status"] == "INVALID_INPUT"


def test_ht_invalid_004_invalid_expected_status() -> None:
    core = next(c for c in _INVALID_FIXTURE_CORES if c["fixture_id"] == "ht-invalid-004")
    assert core["expected_status"] == "UNKNOWN"
    assert core["expected_outcome_reason"] == "INVALID_EXPECTED_STATUS_VALUE"


def test_ht_nc_001_alpha_lte_zero() -> None:
    core = next(c for c in _NOT_COMPUTABLE_FIXTURE_CORES if c["fixture_id"] == "ht-nc-001")
    assert core["alpha"] <= 0
    assert core["expected_status"] == "NOT_COMPUTABLE"
    assert core["expected_outcome_reason"] == "ALPHA_NOT_POSITIVE"


def test_ht_nc_002_sample_count_zero() -> None:
    core = next(c for c in _NOT_COMPUTABLE_FIXTURE_CORES if c["fixture_id"] == "ht-nc-002")
    assert core["sample_count"] == 0
    assert core["sequence_values"] == []
    assert core["expected_outcome_reason"] == "ZERO_SAMPLE_COUNT"


def test_ht_nc_003_empty_sequence() -> None:
    core = next(c for c in _NOT_COMPUTABLE_FIXTURE_CORES if c["fixture_id"] == "ht-nc-003")
    assert core["sequence_values"] == []
    assert core["expected_outcome_reason"] == "EMPTY_SEQUENCE"


def test_ht_nc_004_non_finite_value() -> None:
    core = next(c for c in _NOT_COMPUTABLE_FIXTURE_CORES if c["fixture_id"] == "ht-nc-004")
    assert None in core["sequence_values"]
    assert core["expected_outcome_reason"] == "NON_FINITE_VALUE"


def test_ht_nc_005_negative_value() -> None:
    core = next(c for c in _NOT_COMPUTABLE_FIXTURE_CORES if c["fixture_id"] == "ht-nc-005")
    assert any(v is not None and v < 0 for v in core["sequence_values"])
    assert core["expected_outcome_reason"] == "NEGATIVE_VALUE"


def test_ht_nc_006_sample_count_mismatch() -> None:
    core = next(c for c in _NOT_COMPUTABLE_FIXTURE_CORES if c["fixture_id"] == "ht-nc-006")
    assert core["sample_count"] != len(core["sequence_values"])
    assert core["expected_outcome_reason"] == "SAMPLE_COUNT_MISMATCH"


def test_fixture_hash_is_deterministic() -> None:
    f1 = build_fixture_content(_VALID_FIXTURE_CORES[0])
    f2 = build_fixture_content(_VALID_FIXTURE_CORES[0])
    assert f1["fixture_hash"] == f2["fixture_hash"]


def test_fixture_hash_length() -> None:
    for f in _fixtures():
        assert len(f["fixture_hash"]) == 64
        assert all(c in "0123456789abcdef" for c in f["fixture_hash"])


def test_all_fixture_hashes_unique() -> None:
    hashes = [f["fixture_hash"] for f in _fixtures()]
    assert len(hashes) == len(set(hashes))


def test_fixture_paths_use_base_dir() -> None:
    for fid in ["ht-valid-001", "ht-invalid-001", "ht-nc-001"]:
        p = fixture_path(fid)
        assert p.startswith(FIXTURE_BASE_DIR)
        assert p.endswith(f"{fid}.json")


def test_receipt_hash_deterministic() -> None:
    fx = _fixtures()
    a = build_receipt(_payload(fx), fx)
    b = build_receipt(_payload(fx), fx)
    assert a["canonical_hash"] == b["canonical_hash"]


def test_receipt_schema_version() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    assert r["schema_version"] == "HeavyTailFixtureCorpusCreationReceipt.v1"


def test_receipt_type_and_status() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    assert r["receipt_type"] == "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_RECEIPT"
    assert r["receipt_status"] == "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_RECEIPT_COMPLETE"


def test_receipt_operator_id() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    assert r["operator_id"] == "HEAVY_TAIL"


def test_receipt_source_auth_hash_confirmed() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    b = r["source_authorization_binding"]
    assert b["authorization_canonical_hash"] == SOURCE_AUTH_HASH
    assert b["hash_confirmed"] is True


def test_receipt_schema_plan_hash_confirmed() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    b = r["schema_plan_binding"]
    assert b["schema_plan_canonical_hash"] == SOURCE_SCHEMA_PLAN_HASH
    assert b["hash_confirmed"] is True


def test_receipt_corpus_plan_hash_confirmed() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    b = r["fixture_corpus_plan_binding"]
    assert b["fixture_corpus_plan_canonical_hash"] == FIXTURE_CORPUS_PLAN_HASH
    assert b["hash_confirmed"] is True


def test_receipt_fixture_file_manifest_count() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    assert len(r["fixture_file_manifest"]) == TOTAL_FIXTURE_COUNT


def test_receipt_fixture_file_manifest_all_created() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    for entry in r["fixture_file_manifest"]:
        assert entry["fixture_created"] is True


def test_receipt_valid_fixture_receipt_count() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    assert len(r["valid_fixture_receipt"]) == VALID_FIXTURE_COUNT


def test_receipt_invalid_fixture_receipt_count() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    assert len(r["invalid_fixture_receipt"]) == INVALID_FIXTURE_COUNT


def test_receipt_not_computable_fixture_receipt_count() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    assert len(r["not_computable_fixture_receipt"]) == NOT_COMPUTABLE_FIXTURE_COUNT


def test_receipt_fixture_hash_manifest_count() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    assert len(r["fixture_hash_manifest"]) == TOTAL_FIXTURE_COUNT


def test_receipt_fixture_hash_manifest_hashes_valid() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    for fid, h in r["fixture_hash_manifest"].items():
        assert len(h) == 64, f"hash for {fid} is not 64 chars"
        assert all(c in "0123456789abcdef" for c in h)


def test_receipt_fixture_hash_manifest_consistent_with_receipt_entries() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    manifest = r["fixture_hash_manifest"]
    for section in ("valid_fixture_receipt", "invalid_fixture_receipt",
                    "not_computable_fixture_receipt"):
        for entry in r[section]:
            fid = entry["fixture_id"]
            assert entry["fixture_hash"] == manifest[fid], f"hash mismatch for {fid}"


def test_receipt_all_locked_true_flags() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    for flag in LOCKED_TRUE_FLAGS:
        assert r["authority_lock_review"][flag] is True, f"{flag} must be True"


def test_receipt_all_locked_false_flags() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    for flag in LOCKED_FALSE_FLAGS:
        assert r["authority_lock_review"][flag] is False, f"{flag} must be False"


def test_receipt_fixture_files_created_true() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    assert r["authority_lock_review"]["fixture_files_created"] is True


def test_receipt_canonical_hash_64_hex() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    h = r["canonical_hash"]
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_receipt_recommended_next_step() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    assert r["recommended_next_step"] == "HEAVY_TAIL_COMPUTATION_RECEIPT"


def test_receipt_serialize_is_valid_json() -> None:
    fx = _fixtures()
    r = build_receipt(_payload(fx), fx)
    raw = serialize_receipt(r)
    parsed = json.loads(raw)
    assert parsed["schema_version"] == "HeavyTailFixtureCorpusCreationReceipt.v1"


def test_valid_fixture_sample_count_matches_sequence_length() -> None:
    for core in _VALID_FIXTURE_CORES:
        assert core["sample_count"] == len(core["sequence_values"]), core["fixture_id"]


def test_not_computable_fixtures_trigger_conditions() -> None:
    by_id = {c["fixture_id"]: c for c in _NOT_COMPUTABLE_FIXTURE_CORES}
    assert by_id["ht-nc-001"]["alpha"] < 0
    assert by_id["ht-nc-002"]["sample_count"] == 0
    assert by_id["ht-nc-003"]["sequence_values"] == []
    assert None in by_id["ht-nc-004"]["sequence_values"]
    assert any(v is not None and v < 0 for v in by_id["ht-nc-005"]["sequence_values"])
    assert by_id["ht-nc-006"]["sample_count"] != len(by_id["ht-nc-006"]["sequence_values"])


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
            lambda p: p["fixture_corpus_plan_binding"].__setitem__(
                "fixture_corpus_plan_canonical_hash", "d" * 64
            ),
            "fixture_corpus_plan_hash_mismatch",
        ),
        (
            lambda p: p["fixture_corpus_plan_binding"].__setitem__(
                "hash_confirmed", False
            ),
            "fixture_corpus_plan_hash_not_confirmed",
        ),
        (
            lambda p: p["authority_lock_review"].__setitem__(
                "fixture_files_created", False
            ),
            "authority_lock_must_be_true:fixture_files_created",
        ),
        (
            lambda p: p["authority_lock_review"].__setitem__(
                "computation_executed", True
            ),
            "authority_lock_must_be_false:computation_executed",
        ),
        (
            lambda p: p["authority_lock_review"].__setitem__(
                "advisory_only", False
            ),
            "authority_lock_must_be_true:advisory_only",
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
    fx = _fixtures()
    payload = _payload(fx)
    mutator(payload)
    with pytest.raises(
        HeavyTailFixtureCorpusCreationReceiptValidationError, match=err
    ):
        build_receipt(payload, fx)


def test_committed_receipt_parseable() -> None:
    path = Path(
        "out/metric_operator/"
        "heavy_tail_fixture_corpus_creation_receipt_001.latest.json"
    )
    if not path.exists():
        pytest.skip("artifact not yet emitted")
    data = json.loads(path.read_text())
    assert data["schema_version"] == "HeavyTailFixtureCorpusCreationReceipt.v1"
    assert data["receipt_status"] == "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_RECEIPT_COMPLETE"
    assert len(data["canonical_hash"]) == 64
    assert len(data["fixture_file_manifest"]) == TOTAL_FIXTURE_COUNT
    assert len(data["fixture_hash_manifest"]) == TOTAL_FIXTURE_COUNT
    assert (
        data["fixture_corpus_plan_binding"]["fixture_corpus_plan_canonical_hash"]
        == FIXTURE_CORPUS_PLAN_HASH
    )


@pytest.mark.parametrize("fixture_id", [
    "ht-valid-001", "ht-valid-002", "ht-valid-003",
    "ht-valid-004", "ht-valid-005", "ht-valid-006",
    "ht-invalid-001", "ht-invalid-002", "ht-invalid-003", "ht-invalid-004",
    "ht-nc-001", "ht-nc-002", "ht-nc-003", "ht-nc-004", "ht-nc-005", "ht-nc-006",
])
def test_committed_fixture_parseable(fixture_id: str) -> None:
    path = Path(FIXTURE_BASE_DIR) / f"{fixture_id}.json"
    if not path.exists():
        pytest.skip(f"fixture not yet written: {fixture_id}")
    data = json.loads(path.read_text())
    assert data["fixture_id"] == fixture_id
    assert data["operator_id"] == "HEAVY_TAIL"
    assert len(data["fixture_hash"]) == 64

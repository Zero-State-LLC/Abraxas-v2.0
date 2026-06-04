"""Tests for HEAVY_TAIL fixture corpus creation receipt."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.heavy_tail_fixture_corpus_creation_receipt import (
    ALL_FIXTURE_IDS,
    RECEIPT_ID,
    RECEIPT_STATUS,
    SCHEMA_VERSION,
    SOURCE_AUTHORIZATION_HASH,
    SOURCE_FIXTURE_PLAN_HASH,
    HeavyTailFixtureCorpusCreationReceiptError,
    build_heavy_tail_fixture_corpus_creation_receipt,
    materialize_heavy_tail_fixture_corpus,
    validate_heavy_tail_fixture_corpus_creation_receipt,
)

RECEIPT_OUT_PATH = Path(
    "out/metric_operator/heavy_tail_fixture_corpus_creation_receipt_001.latest.json"
)
FIXTURE_DIR = Path("tests/fixtures/heavy_tail")


class TestMaterializeFixtureCorpus:
    def test_materializes_all_16_files(self, tmp_path: Path) -> None:
        docs = materialize_heavy_tail_fixture_corpus(tmp_path)
        assert len(docs) == 16
        assert len(list(tmp_path.glob("*.json"))) == 16

    def test_materialized_ids_match_expected_order(self, tmp_path: Path) -> None:
        docs = materialize_heavy_tail_fixture_corpus(tmp_path)
        assert [doc["fixture_id"] for doc in docs] == list(ALL_FIXTURE_IDS)

    def test_valid_equal_values_fixture_is_flat(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        doc = json.loads(
            (tmp_path / "ht_valid_006_repeated_equal_values_control.json").read_text(encoding="utf-8")
        )
        assert doc["sequence_values"] == [10] * 20
        assert doc["expected_outcome_reason"] == "REPEATED_EQUAL_VALUES"

    def test_invalid_missing_alpha_fixture_omits_alpha(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        doc = json.loads(
            (tmp_path / "ht_invalid_001_missing_alpha.json").read_text(encoding="utf-8")
        )
        assert "alpha" not in doc
        assert doc["expected_status"] == "INVALID_INPUT"

    def test_not_computable_non_finite_fixture_uses_null_sentinel(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        doc = json.loads(
            (tmp_path / "ht_nc_004_non_finite_sequence_value.json").read_text(encoding="utf-8")
        )
        assert None in doc["sequence_values"]
        assert doc["expected_outcome_reason"] == "NON_FINITE_VALUE"


class TestBuildReceipt:
    def test_builds_successfully(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        receipt = build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)
        assert receipt is not None

    def test_schema_version(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        receipt = build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)
        assert receipt["schema_version"] == SCHEMA_VERSION

    def test_receipt_id(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        receipt = build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)
        assert receipt["receipt_id"] == RECEIPT_ID

    def test_receipt_status(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        receipt = build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)
        assert receipt["receipt_status"] == RECEIPT_STATUS

    def test_source_hashes(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        receipt = build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)
        assert receipt["source_authorization_hash"] == SOURCE_AUTHORIZATION_HASH
        assert receipt["source_fixture_plan_hash"] == SOURCE_FIXTURE_PLAN_HASH

    def test_fixture_counts(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        receipt = build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)
        assert receipt["fixture_count_total"] == 16
        assert receipt["fixture_count_valid"] == 6
        assert receipt["fixture_count_invalid"] == 4
        assert receipt["fixture_count_not_computable"] == 6

    def test_authority_locks(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        receipt = build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)
        locks = receipt["authority_locks"]
        assert locks["fixture_files_created"] is True
        assert locks["computation_executed"] is False
        assert locks["baseline_pack_updated"] is False
        assert locks["emits_metric_values"] is False
        assert locks["execution_authority"] is False

    def test_manifest_ids_ordered(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        receipt = build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)
        ids = [item["fixture_id"] for item in receipt["fixture_manifest"]]
        assert ids == list(ALL_FIXTURE_IDS)

    def test_recommended_next_step(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        receipt = build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)
        assert receipt["recommended_next_step"] == "HEAVY_TAIL_COMPUTATION_RECEIPT"

    def test_deterministic_hash(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        a = build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)
        b = build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)
        assert a["canonical_hash"] == b["canonical_hash"]

    def test_validates_successfully(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        receipt = build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)
        validate_heavy_tail_fixture_corpus_creation_receipt(receipt)


class TestValidateReceipt:
    def test_wrong_schema_version_raises(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        receipt = build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)
        bad = {**receipt, "schema_version": "Wrong.v1"}
        with pytest.raises(HeavyTailFixtureCorpusCreationReceiptError):
            validate_heavy_tail_fixture_corpus_creation_receipt(bad)

    def test_tampered_hash_raises(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        receipt = build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)
        bad = {**receipt, "canonical_hash": "a" * 64}
        with pytest.raises(HeavyTailFixtureCorpusCreationReceiptError):
            validate_heavy_tail_fixture_corpus_creation_receipt(bad)

    def test_missing_fixture_file_raises(self, tmp_path: Path) -> None:
        materialize_heavy_tail_fixture_corpus(tmp_path)
        (tmp_path / "ht_valid_001_bounded_power_law_alpha_2.json").unlink()
        with pytest.raises(HeavyTailFixtureCorpusCreationReceiptError):
            build_heavy_tail_fixture_corpus_creation_receipt(tmp_path)


class TestDiskArtifact:
    def test_fixture_directory_exists(self) -> None:
        assert FIXTURE_DIR.exists(), (
            f"fixture directory not found at {FIXTURE_DIR}; "
            "run scripts/run_heavy_tail_fixture_corpus_creation_receipt.py first"
        )

    def test_receipt_file_exists(self) -> None:
        assert RECEIPT_OUT_PATH.exists(), (
            f"receipt artifact not found at {RECEIPT_OUT_PATH}; "
            "run scripts/run_heavy_tail_fixture_corpus_creation_receipt.py first"
        )

    def test_receipt_file_validates(self) -> None:
        if not RECEIPT_OUT_PATH.exists():
            pytest.skip("receipt artifact not yet created")
        doc = json.loads(RECEIPT_OUT_PATH.read_text(encoding="utf-8"))
        validate_heavy_tail_fixture_corpus_creation_receipt(doc)

    def test_receipt_file_hash_bindings_match_constants(self) -> None:
        if not RECEIPT_OUT_PATH.exists():
            pytest.skip("receipt artifact not yet created")
        doc = json.loads(RECEIPT_OUT_PATH.read_text(encoding="utf-8"))
        assert doc["source_authorization_hash"] == SOURCE_AUTHORIZATION_HASH
        assert doc["source_fixture_plan_hash"] == SOURCE_FIXTURE_PLAN_HASH

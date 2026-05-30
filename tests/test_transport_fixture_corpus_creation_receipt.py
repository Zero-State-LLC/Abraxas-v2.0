"""Tests for TRANSPORT fixture corpus creation receipt."""
from __future__ import annotations

import json
import pathlib

import pytest

from core.transport_fixture_corpus_creation_receipt import (
    ALL_FIXTURE_IDS,
    RECEIPT_ID,
    RECEIPT_STATUS,
    SCHEMA_VERSION,
    SOURCE_FIXTURE_PLAN_HASH,
    SOURCE_IMPLEMENTATION_GATE_HASH,
    TransportFixtureCorpusCreationReceiptError,
    build_transport_fixture_corpus_creation_receipt,
    validate_transport_fixture_corpus_creation_receipt,
)

RECEIPT_OUT_PATH = pathlib.Path(
    "out/metric_operator/"
    "transport_fixture_corpus_creation_receipt_001.latest.json"
)


class TestBuildReceipt:
    def test_builds_successfully(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt is not None

    def test_schema_version(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["schema_version"] == SCHEMA_VERSION

    def test_receipt_id(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["receipt_id"] == RECEIPT_ID

    def test_receipt_status(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["receipt_status"] == RECEIPT_STATUS

    def test_operator_id(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["operator_id"] == "TRANSPORT"

    def test_source_fixture_plan_hash(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["source_fixture_plan_hash"] == SOURCE_FIXTURE_PLAN_HASH

    def test_source_implementation_gate_hash(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["source_implementation_gate_hash"] == SOURCE_IMPLEMENTATION_GATE_HASH

    def test_fixture_count_total_15(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["fixture_count_total"] == 15

    def test_fixture_count_valid_6(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["fixture_count_valid"] == 6

    def test_fixture_count_invalid_4(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["fixture_count_invalid"] == 4

    def test_fixture_count_not_computable_5(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["fixture_count_not_computable"] == 5

    def test_metric_value_emitted_false(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["metric_value_emitted"] is False

    def test_intended_lane_shadow(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["intended_lane"] == "SHADOW"

    def test_fixture_files_created_true(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["authority_locks"]["fixture_files_created"] is True

    def test_computation_executed_false(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["authority_locks"]["computation_executed"] is False

    def test_emits_metric_values_false(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["authority_locks"]["emits_metric_values"] is False

    def test_production_activation_false(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["authority_locks"]["production_activation"] is False

    def test_forecast_influence_false(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["authority_locks"]["forecast_influence"] is False

    def test_canon_promotion_false(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["authority_locks"]["canon_promotion"] is False

    def test_runtime_mutation_false(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt["authority_locks"]["runtime_mutation"] is False

    def test_canonical_hash_64_chars(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        h = receipt.get("canonical_hash", "")
        assert isinstance(h, str) and len(h) == 64

    def test_fixture_manifest_has_15_entries(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert len(receipt["fixture_manifest"]) == 15

    def test_fixture_manifest_ids_ordered(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        ids = [m["fixture_id"] for m in receipt["fixture_manifest"]]
        assert ids == list(ALL_FIXTURE_IDS)

    def test_fixture_manifest_all_have_64_char_hash(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        for entry in receipt["fixture_manifest"]:
            h = entry.get("canonical_hash", "")
            assert isinstance(h, str) and len(h) == 64, entry["fixture_id"]

    def test_fixture_manifest_all_have_fixture_type(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        for entry in receipt["fixture_manifest"]:
            assert entry["fixture_type"] in ("VALID", "INVALID", "NOT_COMPUTABLE")

    def test_recommended_next_step(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        assert receipt.get("recommended_next_step") == "TRANSPORT_COMPUTATION_IMPLEMENTATION"

    def test_deterministic(self) -> None:
        a = build_transport_fixture_corpus_creation_receipt()
        b = build_transport_fixture_corpus_creation_receipt()
        assert a["canonical_hash"] == b["canonical_hash"]

    def test_validates_successfully(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        validate_transport_fixture_corpus_creation_receipt(receipt)


class TestValidateReceipt:
    def test_wrong_schema_version_raises(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        bad = {**receipt, "schema_version": "Wrong.v1"}
        with pytest.raises(TransportFixtureCorpusCreationReceiptError):
            validate_transport_fixture_corpus_creation_receipt(bad)

    def test_wrong_receipt_status_raises(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        bad = {**receipt, "receipt_status": "WRONG"}
        with pytest.raises(TransportFixtureCorpusCreationReceiptError):
            validate_transport_fixture_corpus_creation_receipt(bad)

    def test_tampered_canonical_hash_raises(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        bad = {**receipt, "canonical_hash": "a" * 64}
        with pytest.raises(TransportFixtureCorpusCreationReceiptError):
            validate_transport_fixture_corpus_creation_receipt(bad)

    def test_wrong_source_plan_hash_raises(self) -> None:
        receipt = build_transport_fixture_corpus_creation_receipt()
        bad = dict(receipt)
        bad["source_fixture_plan_hash"] = "b" * 64
        with pytest.raises(TransportFixtureCorpusCreationReceiptError):
            validate_transport_fixture_corpus_creation_receipt(bad)


class TestDiskArtifact:
    def test_receipt_file_exists(self) -> None:
        assert RECEIPT_OUT_PATH.exists(), (
            f"receipt artifact not found at {RECEIPT_OUT_PATH}; "
            "run scripts/run_transport_fixture_corpus_creation_receipt.py first"
        )

    def test_receipt_file_validates(self) -> None:
        if not RECEIPT_OUT_PATH.exists():
            pytest.skip("receipt artifact not yet created")
        doc = json.loads(RECEIPT_OUT_PATH.read_text())
        validate_transport_fixture_corpus_creation_receipt(doc)

    def test_receipt_file_canonical_hash_matches_module_constants(self) -> None:
        if not RECEIPT_OUT_PATH.exists():
            pytest.skip("receipt artifact not yet created")
        doc = json.loads(RECEIPT_OUT_PATH.read_text())
        assert doc["source_fixture_plan_hash"] == SOURCE_FIXTURE_PLAN_HASH
        assert doc["source_implementation_gate_hash"] == SOURCE_IMPLEMENTATION_GATE_HASH

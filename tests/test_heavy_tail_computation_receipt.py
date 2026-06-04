from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.heavy_tail_computation_receipt import (
    COMPUTATION_STATUS,
    OPERATOR_ID,
    RECOMMENDED_NEXT_STEP,
    SCHEMA_VERSION,
    SOURCE_FIXTURE_RECEIPT_HASH,
    build_heavy_tail_computation_receipt,
    validate_heavy_tail_computation_receipt,
)

OUT_PATH = Path("out/metric_operator/heavy_tail_computation_receipt_001.latest.json")


class TestHeavyTailComputationReceipt:
    def test_build_sets_top_level_fields(self) -> None:
        receipt = build_heavy_tail_computation_receipt()

        assert receipt["schema_version"] == SCHEMA_VERSION
        assert receipt["operator_id"] == OPERATOR_ID
        assert receipt["computation_status"] == COMPUTATION_STATUS
        assert receipt["recommended_next_step"] == RECOMMENDED_NEXT_STEP
        assert receipt["source_fixture_receipt_hash"] == SOURCE_FIXTURE_RECEIPT_HASH

    def test_valid_fixture_results_are_all_matches(self) -> None:
        receipt = build_heavy_tail_computation_receipt()
        results = receipt["valid_fixture_results"]

        assert len(results) == 6
        assert all(item["comparison_outcome"] == "MATCH" for item in results)
        assert all(item["metric_emitted"] is False for item in results)
        assert results[0]["computed_tail_index"] == 2.0
        assert results[1]["computed_tail_index"] == 3.0
        assert results[2]["computed_outcome_reason"] == "LIGHT_TAIL_CONTROL"
        assert results[3]["computed_outcome_reason"] == "SINGLE_OUTLIER_DOMINATED"
        assert results[4]["computed_outcome_reason"] == "MONOTONE_RANK_FREQUENCY"
        assert results[5]["computed_outcome_reason"] == "REPEATED_EQUAL_VALUES"

    def test_invalid_fixture_results_match_expected_rejections(self) -> None:
        receipt = build_heavy_tail_computation_receipt()
        results = {item["fixture_id"]: item for item in receipt["invalid_fixture_results"]}

        assert len(results) == 4
        assert results["ht-invalid-001"]["rejection_reason"] == "MISSING_REQUIRED_FIELD"
        assert results["ht-invalid-004"]["rejection_reason"] == "INVALID_STATUS_VALUE"
        assert all(item["computation_attempted"] is False for item in results.values())

    def test_not_computable_results_match_expected_reasons(self) -> None:
        receipt = build_heavy_tail_computation_receipt()
        results = {
            item["fixture_id"]: item for item in receipt["not_computable_fixture_results"]
        }

        assert len(results) == 6
        assert results["ht-nc-001"]["not_computable_reason"] == "ALPHA_NOT_POSITIVE"
        assert results["ht-nc-002"]["not_computable_reason"] == "ZERO_SAMPLE_COUNT"
        assert results["ht-nc-003"]["not_computable_reason"] == "EMPTY_SEQUENCE"
        assert results["ht-nc-004"]["not_computable_reason"] == "NON_FINITE_VALUE"
        assert results["ht-nc-005"]["not_computable_reason"] == "NEGATIVE_VALUE"
        assert results["ht-nc-006"]["not_computable_reason"] == "SAMPLE_COUNT_MISMATCH"

    def test_comparison_summary_is_all_match(self) -> None:
        receipt = build_heavy_tail_computation_receipt()
        summary = receipt["comparison_summary"]

        assert summary["all_valid_match"] is True
        assert summary["match_count"] == 6
        assert summary["mismatch_count"] == 0
        assert summary["total_valid_fixtures"] == 6

    def test_build_is_deterministic(self) -> None:
        first = build_heavy_tail_computation_receipt()
        second = build_heavy_tail_computation_receipt()

        assert first["canonical_hash"] == second["canonical_hash"]
        assert first == second

    def test_validate_accepts_built_receipt(self) -> None:
        receipt = build_heavy_tail_computation_receipt()
        validate_heavy_tail_computation_receipt(receipt)

    def test_validate_rejects_hash_mismatch(self) -> None:
        receipt = build_heavy_tail_computation_receipt()
        bad = dict(receipt)
        bad["canonical_hash"] = "0" * 64

        with pytest.raises(ValueError, match="canonical_hash mismatch"):
            validate_heavy_tail_computation_receipt(bad)

    def test_validate_rejects_mismatch_result(self) -> None:
        receipt = build_heavy_tail_computation_receipt()
        bad = json.loads(json.dumps(receipt))
        bad["valid_fixture_results"][0]["comparison_outcome"] = "MISMATCH"

        with pytest.raises(ValueError, match="comparison_outcome must be MATCH"):
            validate_heavy_tail_computation_receipt(bad)

    def test_generated_artifact_matches_builder(self) -> None:
        if not OUT_PATH.exists():
            pytest.skip("generated artifact not yet emitted in this worktree")
        doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        expected = build_heavy_tail_computation_receipt()
        assert doc == expected

    def test_schema_validates_generated_or_built_receipt(self) -> None:
        jsonschema = pytest.importorskip("jsonschema")
        schema = json.loads(
            Path(
                "contracts/canon/heavy_tail_computation_receipt.v1.schema.json"
            ).read_text(encoding="utf-8")
        )
        if OUT_PATH.exists():
            doc = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        else:
            doc = build_heavy_tail_computation_receipt()
        jsonschema.validate(doc, schema)

"""Build the HEAVY_TAIL fixture corpus creation receipt artifact.

This lane materializes the planned Heavy Tail fixture corpus under
`tests/fixtures/heavy_tail/` and emits a receipt confirming the tracked
fixture set, counts, and canonical hashes. The surface remains advisory-only
and shadow-only: no computation, metric emission, or authority escalation.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "HeavyTailFixtureCorpusCreationReceipt.v1"
FIXTURE_SCHEMA_VERSION = "HeavyTailTestVectorFixture.v1"
RECEIPT_ID = "heavy_tail_fixture_corpus_creation_receipt_001"
RECEIPT_STATUS = "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_COMPLETE"
OPERATOR_ID = "HEAVY_TAIL"

SOURCE_AUTHORIZATION_HASH = (
    "988ed40a766a2fb5edf82bd33a0cdcf5540a4a38486bc36b180802b7ef7e2834"
)
SOURCE_FIXTURE_PLAN_HASH = (
    "afed95244608e93da329110e552bc4674d9868c1578821e8af58c36d1a289b31"
)

FIXTURE_BASE_PATH = Path("tests/fixtures/heavy_tail")
CREATED_AT_UTC = "2026-05-31T06:00:00Z"
RECOMMENDED_NEXT_STEP = "HEAVY_TAIL_COMPUTATION_RECEIPT"

VALID_FIXTURE_IDS = (
    "ht-valid-001",
    "ht-valid-002",
    "ht-valid-003",
    "ht-valid-004",
    "ht-valid-005",
    "ht-valid-006",
)
INVALID_FIXTURE_IDS = (
    "ht-invalid-001",
    "ht-invalid-002",
    "ht-invalid-003",
    "ht-invalid-004",
)
NOT_COMPUTABLE_FIXTURE_IDS = (
    "ht-nc-001",
    "ht-nc-002",
    "ht-nc-003",
    "ht-nc-004",
    "ht-nc-005",
    "ht-nc-006",
)
ALL_FIXTURE_IDS = VALID_FIXTURE_IDS + INVALID_FIXTURE_IDS + NOT_COMPUTABLE_FIXTURE_IDS

FORBIDDEN = (
    "executable",
    "callable",
    "runtime",
    "scheduler",
    "cache",
    "forecast",
    "metric-computation",
    "metric-value",
    "gpu-kernel",
)


class HeavyTailFixtureCorpusCreationReceiptError(ValueError):
    pass


def _check_no_forbidden(value: Any) -> None:
    if isinstance(value, dict):
        for item in value.values():
            _check_no_forbidden(item)
    elif isinstance(value, list):
        for item in value:
            _check_no_forbidden(item)
    elif isinstance(value, str) and any(token in value.lower() for token in FORBIDDEN):
        raise HeavyTailFixtureCorpusCreationReceiptError(
            f"forbidden_token_detected_in_string_value: {value!r}"
        )


def _fixture_doc(payload: dict[str, Any]) -> dict[str, Any]:
    _check_no_forbidden(payload)
    return json.loads(
        canonical_dumps({**payload, "canonical_hash": canonical_hash(canonical_dumps(payload))})
    )


def _moment_summary(sequence_values: list[int]) -> dict[str, float | int | str]:
    count = len(sequence_values)
    mean = sum(sequence_values) / count
    variance = sum((value - mean) ** 2 for value in sequence_values) / count
    return {
        "derivation": "CLOSED_FORM_DECLARED",
        "count": count,
        "min": min(sequence_values),
        "max": max(sequence_values),
        "mean": round(mean, 6),
        "variance": round(variance, 6),
    }


def _base_fixture(
    fixture_id: str,
    fixture_label: str,
    fixture_type: str,
    *,
    alpha: float | None,
    sample_count: int | None,
    sequence_values: list[int | None] | None,
    expected_tail_index: float | None,
    expected_moment_summary: dict[str, Any] | None,
    expected_status: str,
    expected_outcome_reason: str,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": FIXTURE_SCHEMA_VERSION,
        "fixture_id": fixture_id,
        "fixture_label": fixture_label,
        "fixture_type": fixture_type,
        "expected_tail_threshold": 1.5,
        "expected_status": expected_status,
        "expected_outcome_reason": expected_outcome_reason,
        "fixture_creation_authorized": True,
        "implementation_authorized": True,
        "metric_value_emitted": False,
        "intended_lane": "SHADOW",
        "source_authorization_hash": SOURCE_AUTHORIZATION_HASH,
        "source_fixture_plan_hash": SOURCE_FIXTURE_PLAN_HASH,
        "created_at_utc": CREATED_AT_UTC,
    }
    if alpha is not None:
        payload["alpha"] = alpha
    if sample_count is not None:
        payload["sample_count"] = sample_count
    if sequence_values is not None:
        payload["sequence_values"] = sequence_values
    if expected_tail_index is not None:
        payload["expected_tail_index"] = expected_tail_index
    if expected_moment_summary is not None:
        payload["expected_moment_summary"] = expected_moment_summary
    return payload


def _valid_fixture_payloads() -> list[tuple[str, dict[str, Any]]]:
    sequences: list[tuple[str, str, float, list[int], float, str]] = [
        (
            "ht_valid_001_bounded_power_law_alpha_2.json",
            "bounded_power_law_alpha_2",
            2.0,
            [500, 125, 56, 31, 20, 14, 10, 8, 6, 5, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1],
            2.0,
            "POWER_LAW_HEAVY_TAIL_DETECTED",
        ),
        (
            "ht_valid_002_bounded_power_law_alpha_3.json",
            "bounded_power_law_alpha_3",
            3.0,
            [500, 63, 19, 8, 4, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            3.0,
            "POWER_LAW_HEAVY_TAIL_DETECTED",
        ),
        (
            "ht_valid_003_light_tail_control_sequence.json",
            "light_tail_control_sequence",
            5.0,
            [500, 250, 125, 63, 31, 16, 8, 4, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            0.8,
            "LIGHT_TAIL_CONTROL",
        ),
        (
            "ht_valid_004_single_large_outlier_sequence.json",
            "single_large_outlier_sequence",
            2.0,
            [1000] + [1] * 19,
            9.5,
            "SINGLE_OUTLIER_DOMINATED",
        ),
        (
            "ht_valid_005_monotone_rank_frequency_sequence.json",
            "monotone_rank_frequency_sequence",
            2.0,
            list(range(20, 0, -1)),
            1.8,
            "MONOTONE_RANK_FREQUENCY",
        ),
        (
            "ht_valid_006_repeated_equal_values_control.json",
            "repeated_equal_values_control",
            2.0,
            [10] * 20,
            0.0,
            "REPEATED_EQUAL_VALUES",
        ),
    ]

    payloads: list[tuple[str, dict[str, Any]]] = []
    for index, (filename, label, alpha, sequence, tail_index, outcome) in enumerate(sequences, start=1):
        payloads.append(
            (
                filename,
                _base_fixture(
                    f"ht-valid-{index:03d}",
                    label,
                    "VALID",
                    alpha=alpha,
                    sample_count=len(sequence),
                    sequence_values=sequence,
                    expected_tail_index=tail_index,
                    expected_moment_summary=_moment_summary(sequence),
                    expected_status="COMPUTABLE",
                    expected_outcome_reason=outcome,
                ),
            )
        )
    return payloads


def _invalid_fixture_payloads() -> list[tuple[str, dict[str, Any]]]:
    base_sequence = [20, 18, 16, 14, 12, 10, 8, 6, 4, 2]
    base_summary = _moment_summary(base_sequence)
    return [
        (
            "ht_invalid_001_missing_alpha.json",
            _base_fixture(
                "ht-invalid-001",
                "missing_alpha",
                "INVALID",
                alpha=None,
                sample_count=len(base_sequence),
                sequence_values=base_sequence,
                expected_tail_index=1.1,
                expected_moment_summary=base_summary,
                expected_status="INVALID_INPUT",
                expected_outcome_reason="MISSING_REQUIRED_FIELD",
            ),
        ),
        (
            "ht_invalid_002_missing_sample_count.json",
            _base_fixture(
                "ht-invalid-002",
                "missing_sample_count",
                "INVALID",
                alpha=2.0,
                sample_count=None,
                sequence_values=base_sequence,
                expected_tail_index=1.1,
                expected_moment_summary=base_summary,
                expected_status="INVALID_INPUT",
                expected_outcome_reason="MISSING_REQUIRED_FIELD",
            ),
        ),
        (
            "ht_invalid_003_missing_sequence_values.json",
            _base_fixture(
                "ht-invalid-003",
                "missing_sequence_values",
                "INVALID",
                alpha=2.0,
                sample_count=len(base_sequence),
                sequence_values=None,
                expected_tail_index=1.1,
                expected_moment_summary=base_summary,
                expected_status="INVALID_INPUT",
                expected_outcome_reason="MISSING_REQUIRED_FIELD",
            ),
        ),
        (
            "ht_invalid_004_invalid_expected_status.json",
            _base_fixture(
                "ht-invalid-004",
                "invalid_expected_status",
                "INVALID",
                alpha=2.0,
                sample_count=len(base_sequence),
                sequence_values=base_sequence,
                expected_tail_index=1.1,
                expected_moment_summary=base_summary,
                expected_status="UNRECOGNIZED_STATUS",
                expected_outcome_reason="INVALID_STATUS_VALUE",
            ),
        ),
    ]


def _not_computable_fixture_payloads() -> list[tuple[str, dict[str, Any]]]:
    return [
        (
            "ht_nc_001_alpha_lte_zero.json",
            _base_fixture(
                "ht-nc-001",
                "alpha_lte_zero",
                "NOT_COMPUTABLE",
                alpha=-1.0,
                sample_count=20,
                sequence_values=[20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1],
                expected_tail_index=0.0,
                expected_moment_summary={"state": "NOT_COMPUTABLE"},
                expected_status="NOT_COMPUTABLE",
                expected_outcome_reason="ALPHA_NOT_POSITIVE",
            ),
        ),
        (
            "ht_nc_002_sample_count_zero.json",
            _base_fixture(
                "ht-nc-002",
                "sample_count_zero",
                "NOT_COMPUTABLE",
                alpha=2.0,
                sample_count=0,
                sequence_values=[],
                expected_tail_index=0.0,
                expected_moment_summary={"state": "NOT_COMPUTABLE"},
                expected_status="NOT_COMPUTABLE",
                expected_outcome_reason="ZERO_SAMPLE_COUNT",
            ),
        ),
        (
            "ht_nc_003_empty_sequence.json",
            _base_fixture(
                "ht-nc-003",
                "empty_sequence",
                "NOT_COMPUTABLE",
                alpha=2.0,
                sample_count=1,
                sequence_values=[],
                expected_tail_index=0.0,
                expected_moment_summary={"state": "NOT_COMPUTABLE"},
                expected_status="NOT_COMPUTABLE",
                expected_outcome_reason="EMPTY_SEQUENCE",
            ),
        ),
        (
            "ht_nc_004_non_finite_sequence_value.json",
            _base_fixture(
                "ht-nc-004",
                "non_finite_sequence_value",
                "NOT_COMPUTABLE",
                alpha=2.0,
                sample_count=20,
                sequence_values=[10, 9, 8, 7, 6, None, 5, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                expected_tail_index=0.0,
                expected_moment_summary={"state": "NOT_COMPUTABLE"},
                expected_status="NOT_COMPUTABLE",
                expected_outcome_reason="NON_FINITE_VALUE",
            ),
        ),
        (
            "ht_nc_005_negative_sequence_value.json",
            _base_fixture(
                "ht-nc-005",
                "negative_sequence_value",
                "NOT_COMPUTABLE",
                alpha=2.0,
                sample_count=20,
                sequence_values=[10, 9, 8, 7, 6, -1, 5, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                expected_tail_index=0.0,
                expected_moment_summary={"state": "NOT_COMPUTABLE"},
                expected_status="NOT_COMPUTABLE",
                expected_outcome_reason="NEGATIVE_VALUE",
            ),
        ),
        (
            "ht_nc_006_sample_count_mismatch.json",
            _base_fixture(
                "ht-nc-006",
                "sample_count_mismatch",
                "NOT_COMPUTABLE",
                alpha=2.0,
                sample_count=20,
                sequence_values=[10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
                expected_tail_index=0.0,
                expected_moment_summary={"state": "NOT_COMPUTABLE"},
                expected_status="NOT_COMPUTABLE",
                expected_outcome_reason="SAMPLE_COUNT_MISMATCH",
            ),
        ),
    ]


def expected_fixture_documents() -> list[tuple[str, dict[str, Any]]]:
    return (
        _valid_fixture_payloads()
        + _invalid_fixture_payloads()
        + _not_computable_fixture_payloads()
    )


def materialize_heavy_tail_fixture_corpus(
    base_path: Path = FIXTURE_BASE_PATH,
) -> list[dict[str, Any]]:
    base_path.mkdir(parents=True, exist_ok=True)
    documents: list[dict[str, Any]] = []
    for filename, payload in expected_fixture_documents():
        document = _fixture_doc(payload)
        (base_path / filename).write_text(canonical_dumps(document) + "\n", encoding="utf-8")
        documents.append(document)
    return documents


def _verify_fixture_hash(fixture_id: str, doc: dict[str, Any]) -> str:
    stored_hash = doc.get("canonical_hash", "")
    if not isinstance(stored_hash, str) or len(stored_hash) != 64:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            f"fixture {fixture_id}: canonical_hash missing or malformed"
        )
    preimage = {key: value for key, value in doc.items() if key != "canonical_hash"}
    computed_hash = canonical_hash(canonical_dumps(preimage))
    if computed_hash != stored_hash:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            f"fixture {fixture_id}: canonical_hash mismatch stored={stored_hash!r} computed={computed_hash!r}"
        )
    return stored_hash


def _build_fixture_manifest(base_path: Path = FIXTURE_BASE_PATH) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    expected = expected_fixture_documents()
    for filename, payload in expected:
        path = base_path / filename
        if not path.exists():
            raise HeavyTailFixtureCorpusCreationReceiptError(
                f"fixture file not found: {path}; run scripts/run_heavy_tail_fixture_corpus_creation_receipt.py first"
            )
        doc = json.loads(path.read_text(encoding="utf-8"))
        fixture_id = payload["fixture_id"]
        if doc.get("fixture_id") != fixture_id:
            raise HeavyTailFixtureCorpusCreationReceiptError(
                f"fixture_id mismatch in {path}: expected {fixture_id!r} got {doc.get('fixture_id')!r}"
            )
        if doc.get("fixture_type") != payload["fixture_type"]:
            raise HeavyTailFixtureCorpusCreationReceiptError(
                f"fixture_type mismatch in {path}: expected {payload['fixture_type']!r}"
            )
        fixture_hash = _verify_fixture_hash(fixture_id, doc)
        manifest.append(
            {
                "fixture_id": fixture_id,
                "fixture_path": path.as_posix(),
                "fixture_type": doc["fixture_type"],
                "canonical_hash": fixture_hash,
            }
        )
    return manifest


def _build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "fixture_files_created": True,
        "computation_executed": False,
        "baseline_pack_updated": False,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def build_heavy_tail_fixture_corpus_creation_receipt(
    base_path: Path = FIXTURE_BASE_PATH,
) -> dict[str, Any]:
    manifest = _build_fixture_manifest(base_path)
    valid_count = sum(1 for item in manifest if item["fixture_type"] == "VALID")
    invalid_count = sum(1 for item in manifest if item["fixture_type"] == "INVALID")
    not_computable_count = sum(
        1 for item in manifest if item["fixture_type"] == "NOT_COMPUTABLE"
    )

    if len(manifest) != 16:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            f"expected 16 fixtures in manifest, got {len(manifest)}"
        )
    if valid_count != 6:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            f"expected 6 VALID fixtures, got {valid_count}"
        )
    if invalid_count != 4:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            f"expected 4 INVALID fixtures, got {invalid_count}"
        )
    if not_computable_count != 6:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            f"expected 6 NOT_COMPUTABLE fixtures, got {not_computable_count}"
        )

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "receipt_status": RECEIPT_STATUS,
        "operator_id": OPERATOR_ID,
        "source_authorization_hash": SOURCE_AUTHORIZATION_HASH,
        "source_fixture_plan_hash": SOURCE_FIXTURE_PLAN_HASH,
        "fixture_manifest": manifest,
        "fixture_count_total": 16,
        "fixture_count_valid": 6,
        "fixture_count_invalid": 4,
        "fixture_count_not_computable": 6,
        "intended_lane": "SHADOW",
        "metric_value_emitted": False,
        "authority_locks": _build_authority_locks(),
        "recommended_next_step": RECOMMENDED_NEXT_STEP,
        "created_at_utc": CREATED_AT_UTC,
    }
    _check_no_forbidden(payload)
    return json.loads(
        canonical_dumps(
            {**payload, "canonical_hash": canonical_hash(canonical_dumps(payload))}
        )
    )


def validate_heavy_tail_fixture_corpus_creation_receipt(receipt: dict[str, Any]) -> None:
    if receipt.get("schema_version") != SCHEMA_VERSION:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if receipt.get("receipt_status") != RECEIPT_STATUS:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            f"receipt_status must be {RECEIPT_STATUS!r}"
        )
    if receipt.get("operator_id") != OPERATOR_ID:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            f"operator_id must be {OPERATOR_ID!r}"
        )
    if receipt.get("source_authorization_hash") != SOURCE_AUTHORIZATION_HASH:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            "source_authorization_hash mismatch"
        )
    if receipt.get("source_fixture_plan_hash") != SOURCE_FIXTURE_PLAN_HASH:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            "source_fixture_plan_hash mismatch"
        )
    if receipt.get("fixture_count_total") != 16:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            "fixture_count_total must be 16"
        )
    if receipt.get("fixture_count_valid") != 6:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            "fixture_count_valid must be 6"
        )
    if receipt.get("fixture_count_invalid") != 4:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            "fixture_count_invalid must be 4"
        )
    if receipt.get("fixture_count_not_computable") != 6:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            "fixture_count_not_computable must be 6"
        )
    if receipt.get("metric_value_emitted") is not False:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            "metric_value_emitted must be False"
        )

    locks = receipt.get("authority_locks", {})
    if locks.get("fixture_files_created") is not True:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            "authority_locks.fixture_files_created must be True"
        )
    for flag in (
        "computation_executed",
        "baseline_pack_updated",
        "emits_metric_values",
        "forecast_influence",
        "p43_surface_lanes_authorized",
        "production_activation",
        "canon_promotion",
        "runtime_mutation",
        "execution_authority",
        "inference_authority",
    ):
        if locks.get(flag) is not False:
            raise HeavyTailFixtureCorpusCreationReceiptError(
                f"authority_locks.{flag} must be False"
            )

    manifest = receipt.get("fixture_manifest", [])
    if len(manifest) != len(ALL_FIXTURE_IDS):
        raise HeavyTailFixtureCorpusCreationReceiptError(
            f"fixture_manifest must have {len(ALL_FIXTURE_IDS)} entries"
        )
    actual_ids = [item["fixture_id"] for item in manifest]
    if actual_ids != list(ALL_FIXTURE_IDS):
        raise HeavyTailFixtureCorpusCreationReceiptError(
            f"fixture_manifest IDs mismatch: got {actual_ids!r}"
        )
    for item in manifest:
        if not isinstance(item.get("canonical_hash"), str) or len(item["canonical_hash"]) != 64:
            raise HeavyTailFixtureCorpusCreationReceiptError(
                f"fixture_manifest entry has malformed canonical_hash: {item!r}"
            )

    stored_hash = receipt.get("canonical_hash", "")
    if not isinstance(stored_hash, str) or len(stored_hash) != 64:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            "canonical_hash must be a 64-char hex string"
        )
    preimage = {key: value for key, value in receipt.items() if key != "canonical_hash"}
    computed_hash = canonical_hash(canonical_dumps(preimage))
    if computed_hash != stored_hash:
        raise HeavyTailFixtureCorpusCreationReceiptError(
            f"canonical_hash mismatch: stored={stored_hash!r} computed={computed_hash!r}"
        )
    _check_no_forbidden(receipt)

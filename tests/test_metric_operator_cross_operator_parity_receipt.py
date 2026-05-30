from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.metric_operator_cross_operator_parity_receipt import (
    MetricOperatorCrossOperatorParityReceiptError,
    build_metric_operator_cross_operator_parity_receipt,
    default_governance_flags,
    default_output_contract,
    default_parity_dimensions,
    serialize_metric_operator_cross_operator_parity_receipt,
)

_ARTIFACT_PATH = Path(
    "out/metric_operator/metric_operator_cross_operator_parity_receipt_001.latest.json"
)


def _payload() -> dict:
    return {
        "receipt_id": "metric_operator_cross_operator_parity_receipt_001",
        "parity_status": "PARITY_CONFIRMED",
        "operators_compared": ["CHAMFER_DISTANCE", "WASSERSTEIN"],
        "parity_dimensions": default_parity_dimensions(),
        "output_contract": default_output_contract(),
        "governance_flags": default_governance_flags(),
        "provenance": {
            "source": "TEST",
            "advisory_only": True,
            "generated_by": "TEST_ONLY",
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_deterministic_hash() -> None:
    first = build_metric_operator_cross_operator_parity_receipt(_payload())
    second = build_metric_operator_cross_operator_parity_receipt(_payload())
    assert first["canonical_hash"] == second["canonical_hash"]


def test_serialize_deterministic() -> None:
    a = build_metric_operator_cross_operator_parity_receipt(_payload())
    b = build_metric_operator_cross_operator_parity_receipt(_payload())
    assert serialize_metric_operator_cross_operator_parity_receipt(a) == serialize_metric_operator_cross_operator_parity_receipt(b)


def test_default_dimensions_count() -> None:
    dims = default_parity_dimensions()
    assert len(dims) == 7


def test_all_default_dimensions_confirmed() -> None:
    for dim in default_parity_dimensions():
        assert dim["parity_confirmed"] is True


def test_dimension_ids_unique() -> None:
    ids = [d["dimension_id"] for d in default_parity_dimensions()]
    assert len(ids) == len(set(ids))


def test_operators_compared_sorted() -> None:
    record = build_metric_operator_cross_operator_parity_receipt(_payload())
    ops = record["operators_compared"]
    assert ops == sorted(ops)


def test_parity_confirmed_when_all_dims_confirmed() -> None:
    record = build_metric_operator_cross_operator_parity_receipt(_payload())
    assert record["parity_status"] == "PARITY_CONFIRMED"


def test_authority_locks_all_false() -> None:
    record = build_metric_operator_cross_operator_parity_receipt(_payload())
    for v in record["governance_flags"].values():
        assert v is False


def test_output_contract_correct() -> None:
    record = build_metric_operator_cross_operator_parity_receipt(_payload())
    assert record["output_contract"]["emits_metric_values"] is False
    assert record["output_contract"]["emits_parity_receipt"] is True


def test_invalid_parity_status_raises() -> None:
    p = _payload()
    p["parity_status"] = "INVALID"
    with pytest.raises(MetricOperatorCrossOperatorParityReceiptError, match="invalid_parity_status"):
        build_metric_operator_cross_operator_parity_receipt(p)


def test_fewer_than_2_operators_raises() -> None:
    p = _payload()
    p["operators_compared"] = ["WASSERSTEIN"]
    with pytest.raises(MetricOperatorCrossOperatorParityReceiptError, match="operators_compared_must_have_at_least_2"):
        build_metric_operator_cross_operator_parity_receipt(p)


def test_confirmed_status_with_unconfirmed_dim_raises() -> None:
    p = _payload()
    p["parity_dimensions"][0]["parity_confirmed"] = False
    with pytest.raises(MetricOperatorCrossOperatorParityReceiptError, match="parity_status_confirmed_but_not_all_dimensions_confirmed"):
        build_metric_operator_cross_operator_parity_receipt(p)


def test_duplicate_dimension_id_raises() -> None:
    p = _payload()
    dup = dict(p["parity_dimensions"][0])
    p["parity_dimensions"].append(dup)
    with pytest.raises(MetricOperatorCrossOperatorParityReceiptError, match="duplicate_dimension_id"):
        build_metric_operator_cross_operator_parity_receipt(p)


def test_authority_flag_true_raises() -> None:
    p = _payload()
    p["governance_flags"]["forecast_influence"] = True
    with pytest.raises(MetricOperatorCrossOperatorParityReceiptError, match="authority_lock_must_be_false"):
        build_metric_operator_cross_operator_parity_receipt(p)


def test_forbidden_provenance_token_raises() -> None:
    p = _payload()
    p["provenance"]["source"] = "executable-system"
    with pytest.raises(MetricOperatorCrossOperatorParityReceiptError, match="forbidden_provenance_reference_detected"):
        build_metric_operator_cross_operator_parity_receipt(p)


def test_schema_version_set_correctly() -> None:
    record = build_metric_operator_cross_operator_parity_receipt(_payload())
    assert record["schema_version"] == "MetricOperatorCrossOperatorParityReceipt.v1"


def test_canonical_hash_64_hex() -> None:
    record = build_metric_operator_cross_operator_parity_receipt(_payload())
    h = record["canonical_hash"]
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_committed_artifact_exists_and_valid() -> None:
    if not _ARTIFACT_PATH.exists():
        pytest.skip("artifact not yet emitted")
    on_disk = json.loads(_ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert on_disk["schema_version"] == "MetricOperatorCrossOperatorParityReceipt.v1"
    assert on_disk["parity_status"] == "PARITY_CONFIRMED"
    h = on_disk["canonical_hash"]
    assert len(h) == 64


def test_committed_artifact_governance_flags_all_false() -> None:
    if not _ARTIFACT_PATH.exists():
        pytest.skip("artifact not yet emitted")
    on_disk = json.loads(_ARTIFACT_PATH.read_text(encoding="utf-8"))
    for v in on_disk["governance_flags"].values():
        assert v is False

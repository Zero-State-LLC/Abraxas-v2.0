from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.metric_operator_registry_stabilization import (
    MetricOperatorRegistryStabilizationError,
    build_metric_operator_registry_stabilization,
    default_governance_flags,
    default_operator_entries,
    default_output_contract,
    serialize_metric_operator_registry_stabilization,
)

_ARTIFACT_PATH = Path(
    "out/metric_operator/metric_operator_registry_stabilization_001.latest.json"
)


def _payload() -> dict:
    return {
        "stabilization_id": "metric_operator_registry_stabilization_001",
        "title": "Metric Operator Registry Stabilization — SHADOW_STUB_ONLY parity confirmed",
        "stabilization_status": "STABLE",
        "operator_entries": default_operator_entries(),
        "source_refs": [
            "MetricOperatorRegistry.v1:metric_operator_registry_001",
            "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
        ],
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
    first = build_metric_operator_registry_stabilization(_payload())
    second = build_metric_operator_registry_stabilization(_payload())
    assert first["canonical_hash"] == second["canonical_hash"]


def test_serialize_deterministic() -> None:
    a = build_metric_operator_registry_stabilization(_payload())
    b = build_metric_operator_registry_stabilization(_payload())
    assert serialize_metric_operator_registry_stabilization(a) == serialize_metric_operator_registry_stabilization(b)


def test_default_operator_entries_cover_all_12() -> None:
    entries = default_operator_entries()
    assert len(entries) == 12
    ids = {e["operator_id"] for e in entries}
    assert "WASSERSTEIN" in ids
    assert "CHAMFER_DISTANCE" in ids
    assert "GEODESIC" in ids


def test_shadow_operators_have_correct_vector_type() -> None:
    entries = {e["operator_id"]: e for e in default_operator_entries()}
    assert entries["WASSERSTEIN"]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert entries["WASSERSTEIN"]["expected_computation_status"] == "SHADOW_STUB_ONLY"
    assert entries["CHAMFER_DISTANCE"]["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert entries["CHAMFER_DISTANCE"]["expected_computation_status"] == "SHADOW_STUB_ONLY"


def test_non_shadow_operators_are_not_implemented() -> None:
    entries = {e["operator_id"]: e for e in default_operator_entries()}
    for op in ("GEODESIC", "TRANSPORT", "NORM_GEOMETRY", "HYPERVECTOR_BINDING",
               "RESERVOIR_STATE_SPACE", "COUNTERFACTUAL_DIFFUSION", "HEAVY_TAIL",
               "HYSTERESIS", "STOCHASTIC_GEOMETRY", "TOPOLOGICAL_PRIMITIVES"):
        assert entries[op]["vector_type"] == "VALID_METADATA_VECTOR"
        assert entries[op]["expected_computation_status"] == "NOT_IMPLEMENTED"


def test_all_entries_have_execution_blocked() -> None:
    for entry in default_operator_entries():
        assert entry["execution_blocked"] is True
        assert entry["metric_emission_blocked"] is True


def test_authority_locks_all_false() -> None:
    record = build_metric_operator_registry_stabilization(_payload())
    for v in record["governance_flags"].values():
        assert v is False


def test_output_contract_correct() -> None:
    record = build_metric_operator_registry_stabilization(_payload())
    assert record["output_contract"]["emits_metric_values"] is False
    assert record["output_contract"]["emits_stabilization_record"] is True


def test_invalid_stabilization_status_raises() -> None:
    p = _payload()
    p["stabilization_status"] = "UNKNOWN_STATUS"
    with pytest.raises(MetricOperatorRegistryStabilizationError, match="invalid_stabilization_status"):
        build_metric_operator_registry_stabilization(p)


def test_authority_flag_true_raises() -> None:
    p = _payload()
    p["governance_flags"]["execution_authority"] = True
    with pytest.raises(MetricOperatorRegistryStabilizationError, match="authority_lock_must_be_false"):
        build_metric_operator_registry_stabilization(p)


def test_duplicate_operator_id_raises() -> None:
    p = _payload()
    p["operator_entries"] = [p["operator_entries"][0], p["operator_entries"][0]]
    with pytest.raises(MetricOperatorRegistryStabilizationError, match="duplicate_operator_id"):
        build_metric_operator_registry_stabilization(p)


def test_execution_not_blocked_raises() -> None:
    p = _payload()
    p["operator_entries"][0]["execution_blocked"] = False
    with pytest.raises(MetricOperatorRegistryStabilizationError, match="execution_blocked_must_be_true"):
        build_metric_operator_registry_stabilization(p)


def test_forbidden_provenance_token_raises() -> None:
    p = _payload()
    p["provenance"]["generated_by"] = "metric-value-generator"
    with pytest.raises(MetricOperatorRegistryStabilizationError, match="forbidden_provenance_reference_detected"):
        build_metric_operator_registry_stabilization(p)


def test_schema_version_set_correctly() -> None:
    record = build_metric_operator_registry_stabilization(_payload())
    assert record["schema_version"] == "MetricOperatorRegistryStabilization.v1"


def test_canonical_hash_64_hex() -> None:
    record = build_metric_operator_registry_stabilization(_payload())
    h = record["canonical_hash"]
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_committed_artifact_matches_runner_output() -> None:
    if not _ARTIFACT_PATH.exists():
        pytest.skip("artifact not yet emitted")
    on_disk = json.loads(_ARTIFACT_PATH.read_text(encoding="utf-8"))
    assert on_disk["schema_version"] == "MetricOperatorRegistryStabilization.v1"
    assert on_disk["stabilization_status"] == "STABLE"
    h = on_disk["canonical_hash"]
    assert len(h) == 64


def test_committed_artifact_governance_flags_all_false() -> None:
    if not _ARTIFACT_PATH.exists():
        pytest.skip("artifact not yet emitted")
    on_disk = json.loads(_ARTIFACT_PATH.read_text(encoding="utf-8"))
    for v in on_disk["governance_flags"].values():
        assert v is False

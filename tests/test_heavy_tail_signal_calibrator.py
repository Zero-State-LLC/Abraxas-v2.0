from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.heavy_tail_signal_calibrator import (
    build_heavy_tail_signal_calibrator,
    compute_heavy_tail_signal_calibrator_hash,
    default_tail_model_declarations,
    serialize_heavy_tail_signal_calibrator,
    validate_heavy_tail_signal_calibrator,
)


def _base() -> dict:
    return build_heavy_tail_signal_calibrator(
        calibrator_id="HTSC-0001",
        source_attachment_refs=["OGSA-0001"],
        source_signal_packet_refs=["GSP-0001"],
        source_metric_registry_refs=["MOR-0001"],
        calibration_scope={"domain": "oracle_shadow", "observation_window": "rolling-30", "signal_family": "heavy_tail", "intended_lane": "SHADOW"},
        tail_model_declarations=default_tail_model_declarations(),
        computation_status="METADATA_ONLY",
        provenance={
            "source": "oracle-shadow-observation",
            "evidence_refs": ["docs/audits/REPO_AUDIT_ORACLE_GEOMETRIC_SIGNAL_ATTACHMENT_v0_1.md"],
            "generated_by": "tests",
            "upstream_schema_refs": [
                "contracts/canon/oracle_geometric_signal_attachment.v1.schema.json",
                "contracts/canon/geometric_signal_packet.v1.schema.json",
                "contracts/canon/metric_operator_registry.v1.schema.json",
            ],
        },
        created_at_utc="2026-05-27T00:00:00Z",
    )


def test_deterministic_hash() -> None:
    assert _base()["canonical_hash"] == _base()["canonical_hash"]


def test_serialization_stable() -> None:
    p = _base()
    assert serialize_heavy_tail_signal_calibrator(p) == serialize_heavy_tail_signal_calibrator(p)


def test_default_declarations_non_empty() -> None:
    a = default_tail_model_declarations()
    b = default_tail_model_declarations()
    assert a and a == b


def test_duplicate_model_id_fails() -> None:
    models = default_tail_model_declarations() * 2
    with pytest.raises(ValueError, match="duplicate model_id"):
        build_heavy_tail_signal_calibrator(calibrator_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], calibration_scope={"domain":"d","observation_window":"w","signal_family":"s","intended_lane":"SHADOW"}, tail_model_declarations=models, computation_status="DECLARED_ONLY", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_intended_lane_fails() -> None:
    with pytest.raises(ValueError, match="unknown intended_lane"):
        build_heavy_tail_signal_calibrator(calibrator_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], calibration_scope={"domain":"d","observation_window":"w","signal_family":"s","intended_lane":"NOPE"}, tail_model_declarations=default_tail_model_declarations(), computation_status="DECLARED_ONLY", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_model_family_fails() -> None:
    m = default_tail_model_declarations()
    m[0]["model_family"] = "NOPE"
    with pytest.raises(ValueError, match="unknown model_family"):
        build_heavy_tail_signal_calibrator(calibrator_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], calibration_scope={"domain":"d","observation_window":"w","signal_family":"s","intended_lane":"SHADOW"}, tail_model_declarations=m, computation_status="DECLARED_ONLY", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_declared_use_fails() -> None:
    m = default_tail_model_declarations()
    m[0]["declared_use"] = "NOPE"
    with pytest.raises(ValueError, match="unknown declared_use"):
        build_heavy_tail_signal_calibrator(calibrator_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], calibration_scope={"domain":"d","observation_window":"w","signal_family":"s","intended_lane":"SHADOW"}, tail_model_declarations=m, computation_status="DECLARED_ONLY", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_evidence_required_fails() -> None:
    m = default_tail_model_declarations()
    m[0]["evidence_required"] = ["NOPE"]
    with pytest.raises(ValueError, match="unknown evidence_required"):
        build_heavy_tail_signal_calibrator(calibrator_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], calibration_scope={"domain":"d","observation_window":"w","signal_family":"s","intended_lane":"SHADOW"}, tail_model_declarations=m, computation_status="DECLARED_ONLY", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_unknown_implementation_status_fails() -> None:
    m = default_tail_model_declarations()
    m[0]["implementation_status"] = "NOPE"
    with pytest.raises(ValueError, match="unknown implementation_status"):
        build_heavy_tail_signal_calibrator(calibrator_id="x", source_attachment_refs=[], source_signal_packet_refs=[], source_metric_registry_refs=[], calibration_scope={"domain":"d","observation_window":"w","signal_family":"s","intended_lane":"SHADOW"}, tail_model_declarations=m, computation_status="DECLARED_ONLY", provenance={"source":"x","evidence_refs":[],"generated_by":"x","upstream_schema_refs":[]}, created_at_utc="x")


def test_policy_threshold_output_locks() -> None:
    p = _base()
    p1 = dict(p)
    p1["anomaly_observation_policy"] = {**p["anomaly_observation_policy"], "no_score_emission": False}
    with pytest.raises(ValueError, match="anomaly_observation_policy.no_score_emission"):
        validate_heavy_tail_signal_calibrator(p1)
    p2 = dict(p)
    p2["threshold_declarations"] = {**p["threshold_declarations"], "thresholds_executable": True}
    with pytest.raises(ValueError, match="threshold_declarations.thresholds_executable"):
        validate_heavy_tail_signal_calibrator(p2)
    p3 = dict(p)
    p3["output_contract"] = {**p["output_contract"], "emits_scores": True}
    with pytest.raises(ValueError, match="output_contract.emits_scores"):
        validate_heavy_tail_signal_calibrator(p3)


def test_governance_flags_cannot_be_true() -> None:
    p = _base()
    bad = dict(p)
    bad["governance_flags"] = {**p["governance_flags"], "runtime_authority": True}
    with pytest.raises(ValueError, match="runtime_authority"):
        validate_heavy_tail_signal_calibrator(bad)


def test_forbidden_provenance_references() -> None:
    p = _base()
    bad = dict(p)
    bad["provenance"] = {**p["provenance"], "source": "runtime threshold-execution scoring"}
    with pytest.raises(ValueError, match="forbidden"):
        validate_heavy_tail_signal_calibrator(bad)


def test_hash_preimage_excludes_hash() -> None:
    p = _base()
    changed = {**p, "canonical_hash": "0" * 64}
    assert compute_heavy_tail_signal_calibrator_hash(changed) == p["canonical_hash"]


def test_hash_changes_on_change() -> None:
    p = _base()
    changed = build_heavy_tail_signal_calibrator(
        calibrator_id="HTSC-0001",
        source_attachment_refs=["OGSA-0002"],
        source_signal_packet_refs=["GSP-0001"],
        source_metric_registry_refs=["MOR-0001"],
        calibration_scope={"domain": "oracle_shadow", "observation_window": "rolling-30", "signal_family": "heavy_tail", "intended_lane": "SHADOW"},
        tail_model_declarations=default_tail_model_declarations(),
        computation_status="METADATA_ONLY",
        provenance=_base()["provenance"],
        created_at_utc="2026-05-27T00:00:00Z",
    )
    assert changed["canonical_hash"] != p["canonical_hash"]


def test_schema_validation_if_available() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/heavy_tail_signal_calibrator.v1.schema.json").read_text())
    jsonschema.validate(_base(), schema)


def test_id_only_references() -> None:
    blob = json.dumps(_base())
    assert "core.oracle_geometric_signal_attachment" not in blob
    assert "core.geometric_signal_packet" not in blob
    assert "core.metric_operator_registry" not in blob

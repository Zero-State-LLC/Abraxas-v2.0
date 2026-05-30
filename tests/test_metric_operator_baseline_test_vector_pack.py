from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.metric_operator_baseline_test_vector_pack import (
    ALLOWED_OPERATOR_IDS,
    _CHAMFER_SHADOW_STUB_EVIDENCE_REFS,
    _GEODESIC_SHADOW_STUB_EVIDENCE_REFS,
    _WASSERSTEIN_SHADOW_STUB_EVIDENCE_REFS,
    build_metric_operator_baseline_test_vector_pack,
    compute_metric_operator_baseline_test_vector_pack_hash,
    default_invalid_vectors,
    default_operator_vectors,
    default_output_contract,
    default_validation_policy,
    serialize_metric_operator_baseline_test_vector_pack,
)


def _payload() -> dict[str, object]:
    return {
        "pack_id": "metric-operator-baseline-test-vectors-001",
        "source_metric_registry_refs": ["MetricOperatorRegistry.v1"],
        "operator_vectors": default_operator_vectors(),
        "invalid_vectors": default_invalid_vectors(),
        "validation_policy": default_validation_policy(),
        "output_contract": default_output_contract(),
        "governance_flags": {
            "production_activation": False,
            "canon_promotion": False,
            "scheduler_mutation": False,
            "runtime_authority": False,
            "runtime_mutation": False,
            "forecast_influence": False,
            "execution_authority": False,
            "token_minting_allowed": False,
            "valid_for_execution": False,
            "activation_approved": False,
            "authorization_granted": False,
        },
        "provenance": {
            "source": "GEOMETRIC_INTELLIGENCE_v0.1_patch11",
            "evidence_refs": ["docs/audits/REPO_AUDIT_GEOMETRIC_INTELLIGENCE_v0_1.md"],
            "generated_by": "ABX-Core",
            "upstream_schema_refs": ["contracts/canon/metric_operator_registry.v1.schema.json"],
        },
        "created_at_utc": "2026-05-27T00:00:00Z",
        "canonical_hash": "",
    }


def test_deterministic_hash_and_serialization() -> None:
    first = build_metric_operator_baseline_test_vector_pack(_payload())
    second = build_metric_operator_baseline_test_vector_pack(_payload())
    assert first["canonical_hash"] == second["canonical_hash"]
    assert serialize_metric_operator_baseline_test_vector_pack(first) == serialize_metric_operator_baseline_test_vector_pack(second)


def test_default_operator_vectors_cover_all_ids() -> None:
    found = {row["operator_id"] for row in default_operator_vectors()}
    assert found == set(ALLOWED_OPERATOR_IDS)


def test_default_invalid_vectors_non_empty() -> None:
    assert default_invalid_vectors()


def test_duplicate_vector_id_fails() -> None:
    payload = _payload()
    payload["invalid_vectors"][0]["vector_id"] = payload["operator_vectors"][0]["vector_id"]
    with pytest.raises(ValueError, match="duplicate_vector_id"):
        build_metric_operator_baseline_test_vector_pack(payload)


def test_unknown_operator_id_fails() -> None:
    payload = _payload()
    payload["operator_vectors"][0]["operator_id"] = "UNKNOWN"
    with pytest.raises(ValueError, match="unknown_operator_id"):
        build_metric_operator_baseline_test_vector_pack(payload)


def test_unknown_vector_type_fails() -> None:
    payload = _payload()
    payload["operator_vectors"][0]["vector_type"] = "UNKNOWN"
    with pytest.raises(ValueError, match="unknown_vector_type"):
        build_metric_operator_baseline_test_vector_pack(payload)


def test_unknown_computation_status_fails() -> None:
    payload = _payload()
    payload["operator_vectors"][0]["expected_computation_status"] = "UNKNOWN"
    with pytest.raises(ValueError, match="unknown_expected_computation_status"):
        build_metric_operator_baseline_test_vector_pack(payload)


def test_expected_authority_state_must_be_advisory_only() -> None:
    payload = _payload()
    payload["operator_vectors"][0]["expected_authority_state"] = "EXECUTION"
    with pytest.raises(ValueError, match="invalid_expected_authority_state"):
        build_metric_operator_baseline_test_vector_pack(payload)


def test_unknown_invalid_reason_fails() -> None:
    payload = _payload()
    payload["invalid_vectors"][0]["invalid_reason"] = "UNKNOWN"
    with pytest.raises(ValueError, match="unknown_invalid_reason"):
        build_metric_operator_baseline_test_vector_pack(payload)


def test_validation_policy_guarantees_locked() -> None:
    payload = _payload()
    payload["validation_policy"]["validates_no_computation"] = False
    with pytest.raises(ValueError, match="invalid_validation_policy"):
        build_metric_operator_baseline_test_vector_pack(payload)


def test_output_contract_must_not_emit_runtime_or_scores() -> None:
    payload = _payload()
    payload["output_contract"]["emits_scores"] = True
    with pytest.raises(ValueError, match="invalid_output_contract"):
        build_metric_operator_baseline_test_vector_pack(payload)


def test_governance_flags_locked_false() -> None:
    payload = _payload()
    payload["governance_flags"]["execution_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_metric_operator_baseline_test_vector_pack(payload)


def test_forbidden_provenance_references_rejected() -> None:
    payload = _payload()
    payload["provenance"]["source"] = "runtime executable bridge"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_metric_operator_baseline_test_vector_pack(payload)


def test_hash_excludes_canonical_hash_from_preimage() -> None:
    packet = build_metric_operator_baseline_test_vector_pack(_payload())
    changed = dict(packet)
    changed["canonical_hash"] = "0" * 64
    assert compute_metric_operator_baseline_test_vector_pack_hash(packet) == compute_metric_operator_baseline_test_vector_pack_hash(changed)


def test_hash_changes_when_payload_changes() -> None:
    a = build_metric_operator_baseline_test_vector_pack(_payload())
    payload = _payload()
    payload["pack_id"] = "metric-operator-baseline-test-vectors-002"
    b = build_metric_operator_baseline_test_vector_pack(payload)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json").read_text(encoding="utf-8"))
    packet = build_metric_operator_baseline_test_vector_pack(_payload())
    jsonschema.validate(packet, schema)


def test_references_registry_ids_only_no_registry_object_import() -> None:
    packet = build_metric_operator_baseline_test_vector_pack(_payload())
    assert packet["source_metric_registry_refs"] == ["MetricOperatorRegistry.v1"]


def test_wasserstein_vector_is_shadow_stub_only() -> None:
    vectors = default_operator_vectors()
    ws = next(v for v in vectors if v["operator_id"] == "WASSERSTEIN")
    assert ws["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert ws["expected_computation_status"] == "SHADOW_STUB_ONLY"
    assert ws["expected_authority_state"] == "ADVISORY_ONLY"


def test_wasserstein_vector_evidence_refs_include_complete_review() -> None:
    vectors = default_operator_vectors()
    ws = next(v for v in vectors if v["operator_id"] == "WASSERSTEIN")
    assert any(
        "wasserstein_expected_values_complete_review_001" in ref
        for ref in ws["evidence_refs"]
    )


def test_wasserstein_shadow_stub_evidence_refs_constant() -> None:
    assert any(
        "wasserstein_expected_values_complete_review_001" in ref
        for ref in _WASSERSTEIN_SHADOW_STUB_EVIDENCE_REFS
    )


def test_non_shadow_vectors_remain_metadata_only() -> None:
    shadow_operators = {"WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY"}
    vectors = default_operator_vectors()
    for v in vectors:
        if v["operator_id"] in shadow_operators:
            continue
        assert v["vector_type"] == "VALID_METADATA_VECTOR", v["operator_id"]
        assert v["expected_computation_status"] == "NOT_IMPLEMENTED", v["operator_id"]


def test_chamfer_distance_vector_is_shadow_stub_only() -> None:
    vectors = default_operator_vectors()
    ch = next(v for v in vectors if v["operator_id"] == "CHAMFER_DISTANCE")
    assert ch["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert ch["expected_computation_status"] == "SHADOW_STUB_ONLY"
    assert ch["expected_authority_state"] == "ADVISORY_ONLY"


def test_chamfer_distance_vector_evidence_refs_include_complete_review() -> None:
    vectors = default_operator_vectors()
    ch = next(v for v in vectors if v["operator_id"] == "CHAMFER_DISTANCE")
    assert any(
        "chamfer_expected_values_complete_review_001" in ref
        for ref in ch["evidence_refs"]
    )


def test_chamfer_shadow_stub_evidence_refs_constant() -> None:
    assert any(
        "chamfer_expected_values_complete_review_001" in ref
        for ref in _CHAMFER_SHADOW_STUB_EVIDENCE_REFS
    )


def test_all_vectors_advisory_only_authority_state() -> None:
    vectors = default_operator_vectors()
    for v in vectors:
        assert v["expected_authority_state"] == "ADVISORY_ONLY"


def test_geodesic_vector_is_shadow_stub_only() -> None:
    vectors = default_operator_vectors()
    geo = next(v for v in vectors if v["operator_id"] == "GEODESIC")
    assert geo["vector_type"] == "VALID_SHADOW_ONLY_VECTOR"
    assert geo["expected_computation_status"] == "SHADOW_STUB_ONLY"
    assert geo["expected_authority_state"] == "ADVISORY_ONLY"


def test_geodesic_vector_evidence_refs_include_closure() -> None:
    vectors = default_operator_vectors()
    geo = next(v for v in vectors if v["operator_id"] == "GEODESIC")
    assert any(
        "geodesic_computation_operator_closure_001" in ref
        for ref in geo["evidence_refs"]
    )


def test_geodesic_vector_evidence_refs_include_promotion_decision() -> None:
    vectors = default_operator_vectors()
    geo = next(v for v in vectors if v["operator_id"] == "GEODESIC")
    assert any(
        "GEODESIC_BASELINE_PROMOTION_DECISION_2026_05_29_001" in ref
        for ref in geo["evidence_refs"]
    )


def test_geodesic_shadow_stub_evidence_refs_constant() -> None:
    assert any(
        "geodesic_computation_operator_closure_001" in ref
        for ref in _GEODESIC_SHADOW_STUB_EVIDENCE_REFS
    )
    assert any(
        "GEODESIC_BASELINE_PROMOTION_DECISION_2026_05_29_001" in ref
        for ref in _GEODESIC_SHADOW_STUB_EVIDENCE_REFS
    )

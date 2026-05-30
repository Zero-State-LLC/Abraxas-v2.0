from __future__ import annotations

import pytest

from core.chamfer_expected_values_gate import (
    INVALID_FIXTURE_IDS,
    NC_FIXTURE_IDS,
    SHADOW_DISTANCE_VALUES,
    SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH,
    SOURCE_COMPUTATION_RECEIPT_HASH,
    SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH,
    VALID_FIXTURE_CASE_FAMILIES,
    ChamferExpectedValuesGateError,
    build_chamfer_expected_values_gate,
    compute_chamfer_expected_values_gate_hash,
    default_authority_locks,
    default_blocked_scopes,
    default_expected_values_gate_checks,
    default_shadow_distance_gate_verification,
    serialize_chamfer_expected_values_gate,
)


def _payload() -> dict:
    return {
        "gate_id": "chamfer_expected_values_gate_001",
        "intended_lane": "SHADOW",
        "gate_stage": "EXPECTED_VALUES_GATE_ONLY",
        "shadow_distance_gate_verification": default_shadow_distance_gate_verification(),
        "expected_values_gate_checks": default_expected_values_gate_checks(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": "CHAMFER_EXPECTED_VALUES_COMPLETE_REVIEW",
        "provenance": {
            "source": "CHAMFER_EXPECTED_VALUES_GATE",
            "evidence_refs": [
                f"ChamferDistanceComputationReceipt.v1:{SOURCE_COMPUTATION_RECEIPT_HASH}",
            ],
            "generated_by": "PATCH_CHAMFER_EXPECTED_VALUES_GATE_001",
            "upstream_schema_refs": [],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_build_valid_packet() -> None:
    packet = build_chamfer_expected_values_gate(_payload())
    assert packet["gate_type"] == "CHAMFER_EXPECTED_VALUES_GATE"
    assert packet["operator_id"] == "CHAMFER_DISTANCE"
    assert "canonical_hash" in packet


def test_hash_deterministic() -> None:
    p1 = build_chamfer_expected_values_gate(_payload())
    p2 = build_chamfer_expected_values_gate(_payload())
    assert p1["canonical_hash"] == p2["canonical_hash"]


def test_hash_function() -> None:
    packet = build_chamfer_expected_values_gate(_payload())
    h = compute_chamfer_expected_values_gate_hash(packet)
    assert h == packet["canonical_hash"]


def test_serialize_produces_string() -> None:
    packet = build_chamfer_expected_values_gate(_payload())
    s = serialize_chamfer_expected_values_gate(packet)
    assert isinstance(s, str)
    assert "CHAMFER_EXPECTED_VALUES_GATE" in s


def test_invalid_lane_raises() -> None:
    p = _payload()
    p["intended_lane"] = "PRODUCTION"
    with pytest.raises(ChamferExpectedValuesGateError):
        build_chamfer_expected_values_gate(p)


def test_invalid_gate_stage_raises() -> None:
    p = _payload()
    p["gate_stage"] = "WRONG"
    with pytest.raises(ChamferExpectedValuesGateError):
        build_chamfer_expected_values_gate(p)


def test_authority_lock_violation_raises() -> None:
    p = _payload()
    al = dict(default_authority_locks())
    al["emits_metric_values"] = True
    p["authority_locks"] = al
    with pytest.raises(ChamferExpectedValuesGateError):
        build_chamfer_expected_values_gate(p)


def test_forbidden_token_raises() -> None:
    p = _payload()
    p["provenance"]["source"] = "forecast_source"
    with pytest.raises(ChamferExpectedValuesGateError, match="forbidden"):
        build_chamfer_expected_values_gate(p)


def test_shadow_distance_values_all_5() -> None:
    assert len(SHADOW_DISTANCE_VALUES) == 5
    assert SHADOW_DISTANCE_VALUES["chamfer.valid.duplicate_points.v1"] == 0.0
    assert SHADOW_DISTANCE_VALUES["chamfer.valid.multidimensional_points.v1"] == 3.0


def test_valid_fixture_case_families_all_5() -> None:
    assert len(VALID_FIXTURE_CASE_FAMILIES) == 5


def test_invalid_fixture_ids_count() -> None:
    assert len(INVALID_FIXTURE_IDS) == 5


def test_nc_fixture_ids_count() -> None:
    assert len(NC_FIXTURE_IDS) == 3


def test_source_hashes_present() -> None:
    assert len(SOURCE_COMPUTATION_RECEIPT_HASH) == 64
    assert len(SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH) == 64
    assert len(SOURCE_EXPECTED_VALUES_ADDITION_RECEIPT_HASH) == 64


def test_shadow_distance_gate_verification_pass() -> None:
    v = default_shadow_distance_gate_verification()
    assert v["all_5_shadow_distances_locked"] is True
    assert v["shadow_distance_gate_status"] == "PASS"


def test_expected_values_gate_checks_pass() -> None:
    c = default_expected_values_gate_checks()
    assert c["gate_checks_status"] == "ALL_CHECKS_PASS"
    assert c["expected_values_present_in_fixtures"] is True
    assert c["no_metric_values_emitted"] is True


def test_authority_locks_defaults() -> None:
    al = default_authority_locks()
    assert al["emits_metric_values"] is False
    assert al["production_activation"] is False


def test_blocked_scopes_all_false() -> None:
    assert all(v is False for v in default_blocked_scopes().values())

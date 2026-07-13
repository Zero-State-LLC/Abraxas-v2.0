"""Tests for core/codegen/oracle_signal/holler_oracle_shadow_measurement.py (HARDENING candidate c8e58552721cbae4)"""

from core.codegen.oracle_signal.holler_oracle_shadow_measurement import build_holler_oracle_shadow_measurement

def test_build_holler_oracle_shadow_measurement():
    holler = {"canonical_hash": "h1", "holler_batch": {"market_count": 5}}
    shadow = {"canonical_hash": "s1", "measurement_run_refs": [1,2], "projected_outcome_comparisons": [{}]}
    readiness = {"canonical_hash": "r1"}
    res = build_holler_oracle_shadow_measurement(
        timestamp="2026-07-12T00:00:00Z",
        holler_intake=holler,
        oracle_shadow_measurement=shadow,
        oracle_measurement_readiness=readiness,
    )
    assert isinstance(res, dict)
    assert "measurement_id" in res
    assert res.get("measurement_status") == "HOLLER_ORACLE_SHADOW_MEASUREMENT_READY_ADVISORY_ONLY"

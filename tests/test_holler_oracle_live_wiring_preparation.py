"""Tests for core/codegen/oracle_signal/holler_oracle_live_wiring_preparation.py (HARDENING candidate 957cff3cea98be36)"""

from core.codegen.oracle_signal.holler_oracle_live_wiring_preparation import build_holler_oracle_live_wiring_preparation

def test_build_holler_oracle_live_wiring_preparation():
    holler_intake = {
        "canonical_hash": "h-intake-123",
        "holler_batch": {"sport": "nba", "market_count": 12}
    }
    prep = {
        "canonical_hash": "prep-456"
    }

    res = build_holler_oracle_live_wiring_preparation(
        timestamp="2026-07-12T00:00:00Z",
        holler_intake=holler_intake,
        oracle_live_wiring_preparation=prep,
    )

    assert isinstance(res, dict)
    assert res["schema_version"] == "HollerOracleLiveWiringPreparation.v1"
    assert res["preparation_status"] == "HOLLER_ORACLE_LIVE_WIRING_PREPARATION_READY_ADVISORY_ONLY"
    assert "holler_connector_templates" in res
    assert len(res["holler_connector_templates"]) >= 1

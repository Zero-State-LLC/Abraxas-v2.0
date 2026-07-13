"""Tests for core/codegen/oracle_signal/holler_oracle_measurement_proposal.py (HARDENING candidate ce11c27339238f90)"""

from core.codegen.oracle_signal.holler_oracle_measurement_proposal import build_holler_oracle_measurement_proposal

def test_build_proposal_shape():
    holler = {"canonical_hash": "h1", "holler_batch": {"market_count": 5}}
    proposal = {"canonical_hash": "p1"}
    shadow = {"canonical_hash": "s1", "measurement_run_refs": [1,2]}
    res = build_holler_oracle_measurement_proposal(
        timestamp="2026-07-12T00:00:00Z",
        holler_intake=holler,
        oracle_measurement_proposal=proposal,
        oracle_shadow_measurement=shadow,
    )
    assert isinstance(res, dict)
    assert res["schema_version"] == "HollerOracleMeasurementProposal.v1"
    assert res["proposal_status"] == "HOLLER_ORACLE_MEASUREMENT_PROPOSAL_READY_ADVISORY_ONLY"
    assert res["advisory_only"] is True
    assert res["valid_for_live_measurement"] is False
    assert res["valid_for_measurement_execution"] is False
    assert "canonical_hash" in res
    assert "holler_review_summary" in res
    assert "authority_locks" in res

def test_authority_locks_all_false():
    holler = {"canonical_hash": "h1", "holler_batch": {"market_count": 1}}
    proposal = {"canonical_hash": "p1"}
    shadow = {"canonical_hash": "s1", "measurement_run_refs": []}
    res = build_holler_oracle_measurement_proposal(
        timestamp="2026-07-12T00:00:00Z",
        holler_intake=holler,
        oracle_measurement_proposal=proposal,
        oracle_shadow_measurement=shadow,
    )
    locks = res["authority_locks"]
    assert all(v is False for v in locks.values())
    assert res["brier_score"] == 0.1

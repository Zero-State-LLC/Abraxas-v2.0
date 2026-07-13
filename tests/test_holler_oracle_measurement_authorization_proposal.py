"""Tests for core/codegen/oracle_signal/holler_oracle_measurement_authorization_proposal.py (candidate fd69dd9532d0de79)"""

import pytest
from core.codegen.oracle_signal.holler_oracle_measurement_authorization_proposal import build_holler_oracle_measurement_authorization_proposal

def test_build_holler_oracle_measurement_authorization_proposal_basic():
    holler_intake = {
        "holler_batch": {"market_count": 5, "other": "data"},
        "canonical_hash": "hash_holler_123"
    }
    oracle_auth = {"canonical_hash": "hash_auth_456"}
    oracle_prop = {"canonical_hash": "hash_prop_789"}
    result = build_holler_oracle_measurement_authorization_proposal(
        timestamp="2026-07-12T00:00:00Z",
        holler_intake=holler_intake,
        oracle_measurement_authorization_proposal=oracle_auth,
        oracle_measurement_proposal=oracle_prop,
    )
    assert result["schema_version"] == "HollerOracleMeasurementAuthorizationProposal.v1"
    assert "authorization_proposal_id" in result
    assert result["proposal_status"] == "HOLLER_ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_READY_ADVISORY_ONLY"
    assert result["holler_authorization_review"]["projected_market_count"] == 5
    assert result["advisory_only"] is True
    assert result["valid_for_live_measurement"] is False
    assert result["brier_score"] == 0.1

def test_build_holler_oracle_measurement_authorization_proposal_hashes_present():
    holler_intake = {"holler_batch": {"market_count": 1}, "canonical_hash": "h1"}
    oracle_auth = {"canonical_hash": "a1"}
    oracle_prop = {"canonical_hash": "p1"}
    result = build_holler_oracle_measurement_authorization_proposal(
        timestamp="2026-07-12T00:00:00Z",
        holler_intake=holler_intake,
        oracle_measurement_authorization_proposal=oracle_auth,
        oracle_measurement_proposal=oracle_prop,
    )
    assert "canonical_hash" in result
    assert result["oracle_measurement_authorization_proposal_hash"] == "a1"
    assert result["oracle_measurement_proposal_hash"] == "p1"
    assert "holler_batch" in result

def test_build_holler_oracle_measurement_authorization_proposal_authority_locks():
    holler_intake = {"holler_batch": {"market_count": 2}, "canonical_hash": "h2"}
    oracle_auth = {"canonical_hash": "a2"}
    oracle_prop = {"canonical_hash": "p2"}
    result = build_holler_oracle_measurement_authorization_proposal(
        timestamp="2026-07-12T00:00:00Z",
        holler_intake=holler_intake,
        oracle_measurement_authorization_proposal=oracle_auth,
        oracle_measurement_proposal=oracle_prop,
    )
    assert "authority_locks" in result
    assert isinstance(result["authority_locks"], dict)

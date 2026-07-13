"""Tests for core/codegen/oracle_signal/holler_oracle_measurement_authorization_proposal.py (candidate fd69dd9532d0de79)"""

import pytest
from core.codegen.oracle_signal.holler_oracle_measurement_authorization_proposal import build_holler_oracle_measurement_authorization_proposal

def test_build_basic_structure():
    proposal = build_holler_oracle_measurement_authorization_proposal(
        timestamp="2026-07-13T00:00:00Z",
        holler_intake={"canonical_hash": "a" * 64, "holler_batch": {"market_count": 42}},
        oracle_measurement_authorization_proposal={"canonical_hash": "b" * 64},
        oracle_measurement_proposal={"canonical_hash": "c" * 64},
    )
    assert proposal["schema_version"] == "HollerOracleMeasurementAuthorizationProposal.v1"
    assert "authorization_proposal_id" in proposal
    assert proposal["proposal_status"] == "HOLLER_ORACLE_MEASUREMENT_AUTHORIZATION_PROPOSAL_READY_ADVISORY_ONLY"
    assert proposal["holler_authorization_review"]["projected_market_count"] == 42
    assert proposal["holler_authorization_review"]["review_mode"] == "OPERATOR_REVIEW_PROPOSAL_ONLY"

def test_build_requires_hashes():
    with pytest.raises(KeyError):
        build_holler_oracle_measurement_authorization_proposal(
            timestamp="2026-07-13T00:00:00Z",
            holler_intake={"holler_batch": {"market_count": 1}},
            oracle_measurement_authorization_proposal={},
            oracle_measurement_proposal={},
        )

def test_build_preserves_holler_batch():
    proposal = build_holler_oracle_measurement_authorization_proposal(
        timestamp="2026-07-13T00:00:00Z",
        holler_intake={"canonical_hash": "a" * 64, "holler_batch": {"market_count": 7, "extra": "data"}},
        oracle_measurement_authorization_proposal={"canonical_hash": "b" * 64},
        oracle_measurement_proposal={"canonical_hash": "c" * 64},
    )
    assert proposal["holler_batch"]["market_count"] == 7
    assert proposal["holler_batch"]["extra"] == "data"

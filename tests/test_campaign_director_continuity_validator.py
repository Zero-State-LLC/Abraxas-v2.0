"""Tests for continuity validator and protected guard."""

from pathlib import Path

from core.campaign_director.state_recovery import recover_campaign_state
from core.campaign_director.continuity_validator import validate_continuity
from core.campaign_director.protected_state_guard import STOP_SIGNAL


CAMPAIGN_ROOT = Path("out/autonomous_structural_engineering_campaign_001")


def test_continuity_on_real_artifacts():
    rec = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    val = validate_continuity(rec, CAMPAIGN_ROOT)
    assert "validation_status" in val
    assert val["protected_state_valid"] is True or rec.protected_state.is_valid()


def test_guard_stops_on_contradiction(monkeypatch):
    rec = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    # Simulate contradiction
    bad_ps = rec.protected_state.__class__(**{**rec.protected_state.to_dict(), "authority_expanded": True})
    from core.campaign_director import protected_state_guard as pg
    # direct
    g = pg.check_protected_state(bad_ps)
    assert g["stop_signal"] == STOP_SIGNAL


def test_deterministic_validation():
    rec1 = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    rec2 = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    v1 = validate_continuity(rec1, CAMPAIGN_ROOT)
    v2 = validate_continuity(rec2, CAMPAIGN_ROOT)
    assert v1["recovery_hash"] == v2["recovery_hash"]
"""Protected state guard tests."""

from pathlib import Path

from core.campaign_director.state_recovery import recover_campaign_state
from core.campaign_director.protected_state_guard import guard_recovery, STOP_SIGNAL, check_protected_state
from core.campaign_director.models import ProtectedState


CAMPAIGN_ROOT = Path("out/autonomous_structural_engineering_campaign_001")


def test_guard_passes_on_current_artifacts():
    rec = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    g = guard_recovery(rec)
    assert g["valid"] is True
    assert g["stop_signal"] is None


def test_guard_detects_violation():
    bad = ProtectedState(authority_expanded=True, policy_reference_count=3)
    g = check_protected_state(bad, "test")
    assert g["stop_signal"] == STOP_SIGNAL
    assert "authority_expanded" in g["violations"]


def test_deterministic_guard():
    rec = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    g1 = guard_recovery(rec)
    g2 = guard_recovery(rec)
    assert g1 == g2
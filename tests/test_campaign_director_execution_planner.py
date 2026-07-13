"""Tests for execution planner invariants."""

from pathlib import Path

from core.campaign_director.state_recovery import recover_campaign_state
from core.campaign_director.mode_resolver import resolve_mode
from core.campaign_director.execution_planner import build_bounded_plan


CAMPAIGN_ROOT = Path("out/autonomous_structural_engineering_campaign_001")


def test_bounded_plan_stop_and_candidate_rules():
    rec = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    dec = resolve_mode(rec, CAMPAIGN_ROOT)
    plan = build_bounded_plan(rec, dec)
    # stop boundary explicit
    assert plan.stop_before_cycle == rec.latest_completed_cycle + len(plan.cycle_range) + 1
    # no authority expansion baked in
    assert "authority_expanded" not in str(plan.protected_state_required) or not plan.protected_state_required.get("authority_expanded", True)
    # primary or empty ok for phase1
    assert isinstance(plan.primary_candidates, list)
"""Tests for mode resolver and execution planner (Phase 1)."""

from pathlib import Path

from core.campaign_director.state_recovery import recover_campaign_state
from core.campaign_director.mode_resolver import resolve_mode
from core.campaign_director.execution_planner import build_bounded_plan
from core.campaign_director.protected_state_guard import guard_before_plan


CAMPAIGN_ROOT = Path("out/autonomous_structural_engineering_campaign_001")


def test_mode_resolution_defaults_to_a_when_eligible():
    rec = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    dec = resolve_mode(rec, CAMPAIGN_ROOT)
    assert "MODE_A" in dec.mode or dec.mode == "MODE_A_STANDARD_SINGLE_CANDIDATE_BATCH"
    g = guard_before_plan(rec)
    if g["valid"]:
        assert dec.authorized is True


def test_plan_is_bounded():
    rec = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    dec = resolve_mode(rec, CAMPAIGN_ROOT)
    plan = build_bounded_plan(rec, dec)
    assert len(plan.cycle_range) <= 3
    assert plan.stop_before_cycle > rec.latest_completed_cycle
    assert plan.maximum_lifecycle_count <= 3
    assert "plan_hash" in plan.to_dict() and plan.plan_hash


def test_plan_enforces_no_companions_phase1():
    rec = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    dec = resolve_mode(rec, CAMPAIGN_ROOT)
    plan = build_bounded_plan(rec, dec)
    assert plan.companion_candidates == []
"""Deterministic replay tests for full read-only pipeline."""

from pathlib import Path

from core.campaign_director.state_recovery import recover_campaign_state
from core.campaign_director.mode_resolver import resolve_mode
from core.campaign_director.execution_planner import build_bounded_plan
from core.campaign_director.continuation_emitter import emit_continuation


CAMPAIGN_ROOT = Path("out/autonomous_structural_engineering_campaign_001")


def test_full_pipeline_replay_identical():
    rec1 = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    dec1 = resolve_mode(rec1, CAMPAIGN_ROOT)
    plan1 = build_bounded_plan(rec1, dec1)
    cont1 = emit_continuation(rec1, plan1)

    rec2 = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    dec2 = resolve_mode(rec2, CAMPAIGN_ROOT)
    plan2 = build_bounded_plan(rec2, dec2)
    cont2 = emit_continuation(rec2, plan2)

    assert rec1.recovery_hash == rec2.recovery_hash
    assert dec1.decision_hash == dec2.decision_hash
    assert plan1.plan_hash == plan2.plan_hash
    assert cont1.continuation_hash == cont2.continuation_hash
    assert plan1.cycle_range == plan2.cycle_range
    assert plan1.stop_before_cycle == plan2.stop_before_cycle

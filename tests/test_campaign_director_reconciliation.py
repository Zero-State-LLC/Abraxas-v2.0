"""Stub reconciliation and batch sealer tests (Phase 1 read-only)."""

from pathlib import Path

from core.campaign_director.state_recovery import recover_campaign_state
from core.campaign_director.continuation_emitter import emit_continuation
from core.campaign_director.mode_resolver import resolve_mode
from core.campaign_director.execution_planner import build_bounded_plan


CAMPAIGN_ROOT = Path("out/autonomous_structural_engineering_campaign_001")


def test_continuation_emission_deterministic():
    rec = recover_campaign_state(CAMPAIGN_ROOT, validate_schema=False)
    dec = resolve_mode(rec, CAMPAIGN_ROOT)
    plan = build_bounded_plan(rec, dec)
    c1 = emit_continuation(rec, plan)
    c2 = emit_continuation(rec, plan)
    assert c1.continuation_hash == c2.continuation_hash
    assert c1.next_bounded_action["batch_id"] == rec.next_batch
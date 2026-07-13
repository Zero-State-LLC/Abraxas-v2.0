"""Execution Planner.

Converts recovery + fresh (stub) intel + mode into one bounded plan.
Phase 1: MODE_A , exactly bounded 3-cycle or less, explicit stop.
No stale, no unauthorized companions, no authority expansion.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import List, Optional

from .models import (
    CampaignRecoveryResult,
    BoundedExecutionPlan,
    ModeDecision,
)


def build_bounded_plan(
    recovery: CampaignRecoveryResult,
    mode_decision: ModeDecision,
    oracle_candidates: Optional[List[str]] = None,
    campaign_root: Optional[Path] = None,
) -> BoundedExecutionPlan:
    """Build one bounded plan. Enforce invariants."""
    if not mode_decision.authorized or mode_decision.mode != "MODE_A_STANDARD_SINGLE_CANDIDATE_BATCH":
        # For Phase 1 fall back to minimal read plan
        mode = "MODE_A_STANDARD_SINGLE_CANDIDATE_BATCH"
    else:
        mode = mode_decision.mode

    batch_id = recovery.next_batch
    cycle_range = recovery.next_cycles[:3]  # enforce max 3
    stop_before = recovery.latest_completed_cycle + len(cycle_range) + 1

    # Primary from oracle if present, else empty (plan will note)
    primaries = []
    if recovery.oracle_primary_id:
        primaries = [recovery.oracle_primary_id]
    if oracle_candidates:
        # prefer provided, dedupe
        seen = set(primaries)
        for c in oracle_candidates[:2]:
            if c not in seen:
                primaries.append(c)
                seen.add(c)
        primaries = primaries[:1]  # Phase 1 single primary focus

    plan = BoundedExecutionPlan(
        plan_id=f"ABX_CAMPAIGN_PLAN_{hashlib.sha256((recovery.campaign_id + batch_id).encode()).hexdigest()[:12]}",
        campaign_id=recovery.campaign_id,
        mode=mode,
        batch_id=batch_id,
        cycle_range=cycle_range,
        primary_candidates=primaries,
        companion_candidates=[],  # Phase 1: none
        maximum_lifecycle_count=min(3, len(cycle_range)),
        maximum_candidate_count=1 if primaries else 0,
        stop_before_cycle=stop_before,
        protected_state_required=recovery.protected_state.to_dict(),
    )
    # attach computed hash
    plan_hash = plan.compute_hash()
    # Rebuild frozen (dataclasses frozen have no __dict__ for mutation)
    return BoundedExecutionPlan(
        plan_id=plan.plan_id,
        campaign_id=plan.campaign_id,
        mode=plan.mode,
        batch_id=plan.batch_id,
        cycle_range=plan.cycle_range,
        primary_candidates=plan.primary_candidates,
        companion_candidates=plan.companion_candidates,
        maximum_lifecycle_count=plan.maximum_lifecycle_count,
        maximum_candidate_count=plan.maximum_candidate_count,
        stop_before_cycle=plan.stop_before_cycle,
        protected_state_required=plan.protected_state_required,
        plan_hash=plan_hash,
    )


if __name__ == "__main__":
    from .state_recovery import recover_campaign_state
    from .mode_resolver import resolve_mode
    rec = recover_campaign_state()
    dec = resolve_mode(rec)
    plan = build_bounded_plan(rec, dec)
    print(plan.to_dict())
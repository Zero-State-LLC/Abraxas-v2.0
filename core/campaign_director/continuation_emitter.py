"""Continuation Emitter.

Generates compact, repository-derived next instruction artifact.
Sufficient to resume without long prompt.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

from .models import CampaignRecoveryResult, BoundedExecutionPlan, ContinuationArtifact, stable_hash


def emit_continuation(
    recovery: CampaignRecoveryResult,
    plan: BoundedExecutionPlan,
    oracle_handoff: Dict[str, Any] | None = None,
) -> ContinuationArtifact:
    """Emit deterministic continuation."""
    if oracle_handoff is None:
        oracle_handoff = {
            "candidate_id": recovery.oracle_primary_id,
            "status": "HANDOFF_ONLY" if recovery.oracle_primary_id else "NO_PRIMARY",
        }

    next_action = {
        "batch_id": plan.batch_id,
        "cycles": plan.cycle_range,
        "maximum_lifecycle_count": plan.maximum_lifecycle_count,
        "stop_before_cycle": plan.stop_before_cycle,
    }

    cont = ContinuationArtifact(
        campaign_id=recovery.campaign_id,
        latest_sealed_batch=recovery.latest_sealed_batch,
        latest_completed_cycle=recovery.latest_completed_cycle,
        authorized_mode=plan.mode,
        next_bounded_action=next_action,
        oracle_handoff=oracle_handoff,
    )
    h = stable_hash(cont.to_dict())
    # Rebuild frozen
    return ContinuationArtifact(
        campaign_id=cont.campaign_id,
        latest_sealed_batch=cont.latest_sealed_batch,
        latest_completed_cycle=cont.latest_completed_cycle,
        authorized_mode=cont.authorized_mode,
        next_bounded_action=cont.next_bounded_action,
        oracle_handoff=cont.oracle_handoff,
        continuation_hash=h,
    )


def write_continuation_artifact(
    cont: ContinuationArtifact,
    out_dir: Path,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "campaign_director_continuation.v1.json"
    with open(p, "w") as f:
        import json
        json.dump(cont.to_dict(), f, indent=2, sort_keys=True)
    return p


if __name__ == "__main__":
    from .state_recovery import recover_campaign_state
    from .mode_resolver import resolve_mode
    from .execution_planner import build_bounded_plan
    rec = recover_campaign_state()
    dec = resolve_mode(rec)
    plan = build_bounded_plan(rec, dec)
    c = emit_continuation(rec, plan)
    print(c.to_dict())
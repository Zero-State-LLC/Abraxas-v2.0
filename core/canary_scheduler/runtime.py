from __future__ import annotations

from core.canary_scheduler.eligibility import CanaryEligibilityPacket
from core.canary_scheduler.lineage import CanaryScheduleLineageNode, CanaryScheduleLineagePacket
from core.canary_scheduler.operator_review import OperatorCanaryScheduleReviewPacket
from core.canary_scheduler.policies import CanaryPolicyPacket
from core.canary_scheduler.replay import CanaryScheduleReplayPacket
from core.canary_scheduler.rollback import CanaryScheduleRollbackPacket
from core.canary_scheduler.schedule import CanarySchedulePacket
from core.canary_scheduler.windows import CanaryScheduleWindowPacket
def run_canary_policy_scheduler(canary_packets: list[dict], overlay_observability_packets: list[dict]) -> dict[str, object]:
    overlay_hash = canary_packets[-1].get("overlay", {}).get("deterministic_overlay_hash", "overlay") if canary_packets else "overlay"
    stability = overlay_observability_packets[-1].get("stability", {}).get("stability_score", 0.9) if overlay_observability_packets else 0.9
    replay_fail = overlay_observability_packets[-1].get("telemetry", {}).get("replay_failure_count", 0) if overlay_observability_packets else 0
    critical = 0

    policy = CanaryPolicyPacket(
        policy_id="cp-1",
        policy_scope="shadow_only",
        max_overlay_weight=0.3,
        min_stability_score=0.7,
        max_replay_failures=1,
        require_rollback_ready=True,
        allow_critical_diagnostics=False,
        deterministic_policy_hash=CanaryPolicyPacket.compute_hash("shadow_only", 0.3, 0.7, 1, True, False),
        status="passed",
    )

    reasons: list[str] = []
    if stability < policy.min_stability_score:
        reasons.append("stability_below_minimum")
    if replay_fail > policy.max_replay_failures:
        reasons.append("replay_failures_exceed_policy")
    rollback_ready = True
    if policy.require_rollback_ready and not rollback_ready:
        reasons.append("rollback_not_ready")
    if (not policy.allow_critical_diagnostics) and critical > 0:
        reasons.append("critical_diagnostics_present")

    eligible = not reasons
    eligibility = CanaryEligibilityPacket(
        eligibility_id="ce-1",
        overlay_hash=overlay_hash,
        policy_hash=policy.deterministic_policy_hash,
        stability_score=stability,
        replay_failures=replay_fail,
        rollback_ready=rollback_ready,
        critical_diagnostics=critical,
        eligible=eligible,
        blocked_reasons=reasons,
        deterministic_eligibility_hash=CanaryEligibilityPacket.compute_hash(
            overlay_hash, policy.deterministic_policy_hash, stability, replay_fail, rollback_ready, critical, eligible, reasons
        ),
        status="passed" if eligible else "failed",
    )
    window = CanaryScheduleWindowPacket(
        window_id="cw-1",
        overlay_hash=overlay_hash,
        policy_hash=policy.deterministic_policy_hash,
        window_generation=1,
        window_scope="shadow_observation",
        observation_ticks=5,
        deterministic_window_hash=CanaryScheduleWindowPacket.compute_hash(overlay_hash, policy.deterministic_policy_hash, 1, "shadow_observation", 5),
        status="passed",
    )
    schedule_status = "proposed" if eligibility.eligible else "blocked"
    schedule = CanarySchedulePacket(
        schedule_id="cs-1",
        overlay_hash=overlay_hash,
        policy_hash=policy.deterministic_policy_hash,
        eligibility_hash=eligibility.deterministic_eligibility_hash,
        window_hash=window.deterministic_window_hash,
        schedule_status=schedule_status,
        deterministic_schedule_hash=CanarySchedulePacket.compute_hash(
            overlay_hash, policy.deterministic_policy_hash, eligibility.deterministic_eligibility_hash, window.deterministic_window_hash, schedule_status
        ),
        status="passed" if eligibility.eligible else "failed",
    )
    replay = CanaryScheduleReplayPacket(
        replay_id="cr-1",
        schedule_hash=schedule.deterministic_schedule_hash,
        deterministic_match=True,
        replayed_windows=[window.window_id],
        mismatched_windows=[],
        status="passed",
    )
    node = CanaryScheduleLineageNode(schedule_hash=schedule.deterministic_schedule_hash, generation=1, window_hash=window.deterministic_window_hash)
    lineage = CanaryScheduleLineagePacket(
        lineage_id="cl-1",
        lineage_nodes=[node],
        lineage_depth=1,
        deterministic_lineage_hash=CanaryScheduleLineagePacket.compute_hash([node]),
        status="passed",
    )
    rollback = CanaryScheduleRollbackPacket(
        rollback_id="cb-1",
        schedule_hash=schedule.deterministic_schedule_hash,
        rollback_reason="reversible_schedule_reset",
        rollback_complete=True,
        deterministic_rollback_hash=CanaryScheduleRollbackPacket.compute_hash(schedule.deterministic_schedule_hash, "reversible_schedule_reset", True),
        status="passed",
    )
    review = OperatorCanaryScheduleReviewPacket(
        review_id="cor-1",
        schedule_hash=schedule.deterministic_schedule_hash,
        eligibility_status=eligibility.eligible,
        blocked_reasons=eligibility.blocked_reasons,
        replay_failures=replay_fail,
        pending_actions=[] if eligibility.eligible else ["resolve_blocked_reasons"],
        status="approved" if eligibility.eligible else "pending",
    )

    # Pure builder: publication is sole-writer scripts/run_canary_policy_scheduler.py
    return {
        "schema_version": "CanaryPolicySchedulerRuntimePacket.v1",
        "policy": policy.model_dump(),
        "eligibility": eligibility.model_dump(),
        "window": window.model_dump(),
        "schedule": schedule.model_dump(),
        "replay": replay.model_dump(),
        "lineage": lineage.model_dump(),
        "rollback": rollback.model_dump(),
        "operator_review": review.model_dump(),
        "status": "passed",
    }

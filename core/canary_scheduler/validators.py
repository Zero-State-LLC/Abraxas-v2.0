from __future__ import annotations

from core.canary_scheduler.eligibility import CanaryEligibilityPacket
from core.canary_scheduler.policies import CanaryPolicyPacket
from core.canary_scheduler.replay import CanaryScheduleReplayPacket
from core.canary_scheduler.schedule import CanarySchedulePacket


def validate_canary_schedule(
    policy: CanaryPolicyPacket,
    eligibility: CanaryEligibilityPacket,
    schedule: CanarySchedulePacket,
    replay_packet: CanaryScheduleReplayPacket,
    autonomous_attempt: bool = False,
) -> dict[str, object]:
    if policy.policy_scope not in {"shadow_only", "replay_only", "diagnostic_only"}:
        return {"status": "failed", "reason": "production scope invalid"}
    if not eligibility.eligible or schedule.schedule_status == "blocked":
        return {"status": "failed", "reason": "eligibility false blocks schedule"}
    if replay_packet.deterministic_match is False:
        return {"status": "failed", "reason": "replay mismatch blocks validation"}
    if policy.require_rollback_ready and not eligibility.rollback_ready:
        return {"status": "failed", "reason": "missing rollback readiness"}
    if (not policy.allow_critical_diagnostics) and eligibility.critical_diagnostics > 0:
        return {"status": "failed", "reason": "critical diagnostics block schedule"}
    if autonomous_attempt:
        return {"status": "failed", "reason": "autonomous scheduling attempts fail closed"}
    return {"status": "passed", "reason": "schedule validated"}

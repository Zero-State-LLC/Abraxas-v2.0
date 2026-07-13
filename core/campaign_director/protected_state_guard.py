"""Protected State Guard.

Runs at recovery, before planning, before/after mutation (Phase 1: read checks only).
Emits CAMPAIGN_DIRECTOR_PROTECTED_STATE_STOP on violation. No auto-repair.
"""

from __future__ import annotations

from typing import Dict, Any

from .models import ProtectedState, CampaignRecoveryResult


STOP_SIGNAL = "CAMPAIGN_DIRECTOR_PROTECTED_STATE_STOP"


def check_protected_state(
    protected: ProtectedState,
    context: str = "recovery",
) -> Dict[str, Any]:
    """Return guard result. Stop if invalid."""
    valid = protected.is_valid()
    result = {
        "context": context,
        "protected_state": protected.to_dict(),
        "valid": valid,
        "stop_signal": None if valid else STOP_SIGNAL,
        "violations": [] if valid else [
            k for k, v in protected.to_dict().items()
            if (k != "policy_reference_count" and v is True) or (k == "policy_reference_count" and v != 3)
        ],
    }
    return result


def guard_recovery(recovery: CampaignRecoveryResult) -> Dict[str, Any]:
    guard = check_protected_state(recovery.protected_state, "recovery")
    if guard["stop_signal"]:
        guard["terminal"] = STOP_SIGNAL
    return guard


def guard_before_plan(recovery: CampaignRecoveryResult) -> Dict[str, Any]:
    return check_protected_state(recovery.protected_state, "pre_plan")


# Additional entrypoints for future phases (before_lifecycle, after_lifecycle, pre_seal, post_seal)
def guard_point(context: str, protected: ProtectedState) -> Dict[str, Any]:
    return check_protected_state(protected, context)


if __name__ == "__main__":
    from .state_recovery import recover_campaign_state
    rec = recover_campaign_state()
    print(guard_recovery(rec))
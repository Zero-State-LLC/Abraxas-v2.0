"""Mode Resolver.

Chooses fastest authorized execution mode from repository authority artifacts only.
No inference from success rates, enthusiasm, etc.

Phase 1: supports MODE_A if eligible + protected valid.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .models import CampaignRecoveryResult, ModeDecision, stable_hash, EXECUTION_MODES
from .protected_state_guard import guard_before_plan

import hashlib
import json


def _load_mode_authorization(campaign_root: Path) -> Optional[str]:
    """Look for explicit mode authorization artifacts (future: acceleration gates etc)."""
    candidates = [
        campaign_root / "acceleration_authorization.v1.json",
        campaign_root / "mode_authorization.v1.json",
        Path("out/campaign_director/mode_authorization.latest.json"),
    ]
    for p in candidates:
        if p.exists():
            data = json.loads(p.read_text())
            if "authorized_mode" in data:
                return data["authorized_mode"]
    return None


def resolve_mode(
    recovery: CampaignRecoveryResult,
    campaign_root: Optional[Path] = None,
) -> ModeDecision:
    """Resolve mode. Emit deterministic decision receipt."""
    if campaign_root is None:
        campaign_root = Path("out/autonomous_structural_engineering_campaign_001")

    guard = guard_before_plan(recovery)
    if guard.get("stop_signal"):
        return ModeDecision(
            director_run_id=f"ABX_DIRECTOR_DECISION_{recovery.campaign_id[:8]}",
            campaign_id=recovery.campaign_id,
            mode="MODE_F_OPERATOR_DECISION_REQUIRED",
            authorized=False,
            reason="PROTECTED_STATE_CONTRADICTION",
            decision_hash=stable_hash({"stop": guard}),
        )

    explicit = _load_mode_authorization(Path(campaign_root))
    if explicit and explicit in EXECUTION_MODES:
        mode = explicit
        authorized = True
        reason = "EXPLICIT_REPOSITORY_AUTHORIZATION"
    elif recovery.continuous_execution_eligible and recovery.protected_state.is_valid():
        mode = "MODE_A_STANDARD_SINGLE_CANDIDATE_BATCH"
        authorized = True
        reason = "ELIGIBLE_STANDARD_MODE_A"
    else:
        mode = "MODE_F_OPERATOR_DECISION_REQUIRED"
        authorized = False
        reason = "NO_VALID_AUTHORIZATION_OR_ELIGIBILITY"

    base = {
        "director_run_id": f"ABX_DIRECTOR_DECISION_{hashlib.sha256(recovery.recovery_hash.encode()).hexdigest()[:12]}",
        "campaign_id": recovery.campaign_id,
        "mode": mode,
        "authorized": authorized,
        "reason": reason,
    }
    h = stable_hash({**base, "decision_hash_placeholder": True})
    return ModeDecision(
        director_run_id=base["director_run_id"],
        campaign_id=base["campaign_id"],
        mode=base["mode"],
        authorized=base["authorized"],
        reason=base["reason"],
        decision_hash=h,
    )


if __name__ == "__main__":
    from .state_recovery import recover_campaign_state
    rec = recover_campaign_state()
    dec = resolve_mode(rec)
    print(dec.to_dict())
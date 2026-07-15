"""Campaign Director package - read-only Phase 1 core.

Deterministic coordinator for Abraxas structural engineering campaigns.
"""

from .models import (
    CampaignRecoveryResult,
    BoundedExecutionPlan,
    ProtectedState,
    ModeDecision,
    DirectorReceipt,
    ContinuationArtifact,
)
from .state_recovery import recover_campaign_state
from .continuity_validator import validate_continuity
from .protected_state_guard import guard_recovery, check_protected_state
from .mode_resolver import resolve_mode
from .execution_planner import build_bounded_plan
from .continuation_emitter import emit_continuation, write_continuation_artifact
from .stabilization_campaign import (
    CampaignClass,
    StabilizationEntryDecision,
    StabilizationPhase,
    route_stabilization_campaign,
)

__all__ = [
    "recover_campaign_state",
    "validate_continuity",
    "guard_recovery",
    "resolve_mode",
    "build_bounded_plan",
    "emit_continuation",
    "write_continuation_artifact",
    "CampaignRecoveryResult",
    "BoundedExecutionPlan",
    "ProtectedState",
    "ModeDecision",
    "CampaignClass",
    "StabilizationEntryDecision",
    "StabilizationPhase",
    "route_stabilization_campaign",
]

from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class OverlayFirewallDiagnosticPacket(BaseModel):
    schema_version: Literal["OverlayFirewallDiagnosticPacket.v1"] = (
        "OverlayFirewallDiagnosticPacket.v1"
    )
    diagnostic_id: str
    overlay_hash: str
    code: Literal[
        "readiness_below_threshold",
        "rollback_not_ready",
        "governance_unsafe",
        "containment_restricted",
        "continuity_broken",
        "replay_invalid",
        "authority_violation",
        "auto_approval_attempted",
        "forbidden_status_detected",
    ]
    severity: Literal["critical", "warning"]
    resolved: bool = False
    status: Literal["passed", "failed", "not_computable"] = "passed"

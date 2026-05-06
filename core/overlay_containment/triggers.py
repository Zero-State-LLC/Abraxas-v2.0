from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class OverlayContainmentTriggerPacket(BaseModel):
    schema_version: Literal["OverlayContainmentTriggerPacket.v1"] = "OverlayContainmentTriggerPacket.v1"
    trigger_id: str
    active_triggers: list[Literal["aggregate_risk_above_threshold", "propagation_depth_above_threshold", "coupling_score_above_threshold", "rollback_not_ready", "critical_diagnostics", "authority_violation"]]
    status: Literal["passed", "failed", "not_computable"]

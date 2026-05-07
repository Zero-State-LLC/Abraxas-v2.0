from __future__ import annotations
from typing import Literal
from pydantic import BaseModel

class ProposalSandboxDiagnosticPacket(BaseModel):
    schema_version: Literal["ProposalSandboxDiagnosticPacket.v1"] = "ProposalSandboxDiagnosticPacket.v1"
    diagnostic_id: str
    diagnostic_type: Literal["forbidden_route_type","forbidden_route_status","forbidden_lane_type","forbidden_action","replay_mismatch","authority_violation","governance_violation","lineage_cycle","continuity_break","production_routing_attempted","auto_execution_attempted"]
    severity: Literal["info", "warning", "critical"]
    resolved: bool
    status: Literal["passed","failed","not_computable"]

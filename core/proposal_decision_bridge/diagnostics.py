from __future__ import annotations
from typing import Literal
from pydantic import BaseModel

class ProposalDecisionDiagnosticPacket(BaseModel):
    schema_version: Literal["ProposalDecisionDiagnosticPacket.v1"] = "ProposalDecisionDiagnosticPacket.v1"
    diagnostic_id: str
    severity: Literal["info", "warning", "critical"]
    resolved: bool
    message: str
    status: Literal["passed", "failed", "not_computable"]

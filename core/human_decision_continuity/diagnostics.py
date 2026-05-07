from __future__ import annotations
from typing import Literal
from pydantic import BaseModel
class HumanDecisionContinuityDiagnosticPacket(BaseModel):
    schema_version: Literal["HumanDecisionContinuityDiagnosticPacket.v1"] = "HumanDecisionContinuityDiagnosticPacket.v1"
    diagnostic_id: str
    severity: Literal["info","warning","critical"]
    resolved: bool
    status: Literal["passed","failed","not_computable"]

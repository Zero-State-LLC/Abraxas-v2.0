from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ExternalActionProposalDiagnosticPacket(BaseModel):
    schema_version: Literal["ExternalActionProposalDiagnosticPacket.v1"] = "ExternalActionProposalDiagnosticPacket.v1"
    diagnostic_id: str
    severity: Literal["info", "warning", "critical"]
    resolved: bool
    message: str
    status: Literal["passed", "failed", "not_computable"]

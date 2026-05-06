from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class OverlayGovernanceDiagnosticPacket(BaseModel):
    schema_version: Literal["OverlayGovernanceDiagnosticPacket.v1"] = "OverlayGovernanceDiagnosticPacket.v1"
    diagnostic_id: str
    ledger_hash: str
    diagnostic_type: Literal[
        "missing_event",
        "replay_mismatch",
        "lineage_break",
        "authority_violation",
        "continuity_gap",
        "operator_review_backlog",
    ]
    severity: Literal["info", "warning", "critical"]
    diagnostic_message: str
    deterministic_diagnostic_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(ledger_hash: str, diagnostic_type: str, severity: str, diagnostic_message: str) -> str:
        return hashlib.sha256(f"{ledger_hash}|{diagnostic_type}|{severity}|{diagnostic_message}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayGovernanceDiagnosticPacket":
        self.authority.assert_locked()
        self.authority
        if self.deterministic_diagnostic_hash != self.compute_hash(self.ledger_hash, self.diagnostic_type, self.severity, self.diagnostic_message):
            raise ValueError("diagnostic hash")
        return self

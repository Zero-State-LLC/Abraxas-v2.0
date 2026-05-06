from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryPromotionDiagnosticPacket(BaseModel):
    schema_version: Literal["CanaryPromotionDiagnosticPacket.v1"] = "CanaryPromotionDiagnosticPacket.v1"
    diagnostic_id: str
    candidate_hash: str
    diagnostic_type: Literal[
        "replay_instability",
        "rollback_unavailable",
        "bounded_influence_violation",
        "critical_overlay_diagnostic",
        "review_backlog",
        "authority_violation",
    ]
    severity: Literal["info", "warning", "critical"]
    diagnostic_message: str
    deterministic_diagnostic_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(candidate_hash: str, diagnostic_type: str, severity: str, diagnostic_message: str) -> str:
        return hashlib.sha256(f"{candidate_hash}|{diagnostic_type}|{severity}|{diagnostic_message}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "CanaryPromotionDiagnosticPacket":
        self.authority.assert_locked()
        if self.deterministic_diagnostic_hash != self.compute_hash(
            self.candidate_hash,
            self.diagnostic_type,
            self.severity,
            self.diagnostic_message,
        ):
            raise ValueError("hash")
        return self

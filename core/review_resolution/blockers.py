from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class ReviewResolutionBlockerPacket(BaseModel):
    schema_version: Literal["ReviewResolutionBlockerPacket.v1"] = "ReviewResolutionBlockerPacket.v1"
    blocker_id: str
    posture_hash: str
    blocker_type: Literal["unresolved_diagnostic", "firewall_block", "containment_restriction", "replay_mismatch", "governance_violation", "authority_violation", "missing_rationale", "continuity_break"]
    blocker_reason: str
    severity: Literal["info", "warning", "critical"]
    deterministic_blocker_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(posture_hash: str, blocker_type: str, blocker_reason: str, severity: str) -> str:
        return hashlib.sha256(f"{posture_hash}|{blocker_type}|{blocker_reason}|{severity}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ReviewResolutionBlockerPacket":
        self.authority.assert_locked()
        if self.deterministic_blocker_hash != self.compute_hash(self.posture_hash, self.blocker_type, self.blocker_reason, self.severity):
            raise ValueError("blocker hash")
        return self

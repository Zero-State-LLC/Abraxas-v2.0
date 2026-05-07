from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

ALLOWED_POSTURES = {"unresolved", "denied", "deferred", "review_only_resolved", "blocked"}
FORBIDDEN_POSTURES = {"executed", "activated", "deployed", "production_live"}

class ReviewResolutionPosturePacket(BaseModel):
    schema_version: Literal["ReviewResolutionPosturePacket.v1"] = "ReviewResolutionPosturePacket.v1"
    posture_id: str
    request_hash: str
    queue_hash: str
    continuity_hash: str
    firewall_hash: str
    resolution_posture: str
    unresolved_blockers: list[str]
    deterministic_posture_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(request_hash: str, queue_hash: str, continuity_hash: str, firewall_hash: str, resolution_posture: str, unresolved_blockers: list[str]) -> str:
        return hashlib.sha256(f"{request_hash}|{queue_hash}|{continuity_hash}|{firewall_hash}|{resolution_posture}|{'|'.join(sorted(unresolved_blockers))}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ReviewResolutionPosturePacket":
        self.authority.assert_locked()
        if self.resolution_posture in FORBIDDEN_POSTURES or self.resolution_posture not in ALLOWED_POSTURES:
            raise ValueError("forbidden resolution posture")
        if self.deterministic_posture_hash != self.compute_hash(self.request_hash, self.queue_hash, self.continuity_hash, self.firewall_hash, self.resolution_posture, self.unresolved_blockers):
            raise ValueError("posture hash")
        return self

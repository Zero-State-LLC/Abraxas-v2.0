from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

ALLOWED_REQUEST_STATUS = {"pending_review", "deferred", "denied", "approved_for_manual_execution_review"}
FORBIDDEN_REQUEST_STATUS = {"activated", "executing", "live", "production_ready"}


class OperatorApprovalRequestPacket(BaseModel):
    schema_version: Literal["OperatorApprovalRequestPacket.v1"] = "OperatorApprovalRequestPacket.v1"
    request_id: str
    overlay_hash: str
    firewall_hash: str
    readiness_hash: str
    governance_hash: str
    replay_hash: str
    rollback_hash: str
    request_status: str
    request_priority: Literal["low", "normal", "high", "critical"] = "normal"
    request_reason: str
    deterministic_request_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(overlay_hash: str, firewall_hash: str, readiness_hash: str, governance_hash: str, replay_hash: str, rollback_hash: str, request_status: str, request_priority: str, request_reason: str) -> str:
        return hashlib.sha256(f"{overlay_hash}|{firewall_hash}|{readiness_hash}|{governance_hash}|{replay_hash}|{rollback_hash}|{request_status}|{request_priority}|{request_reason}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        if self.request_status in FORBIDDEN_REQUEST_STATUS or self.request_status not in ALLOWED_REQUEST_STATUS:
            raise ValueError("invalid request_status")
        if self.deterministic_request_hash != self.compute_hash(self.overlay_hash, self.firewall_hash, self.readiness_hash, self.governance_hash, self.replay_hash, self.rollback_hash, self.request_status, self.request_priority, self.request_reason):
            raise ValueError("request hash mismatch")
        return self

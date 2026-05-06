from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

ALLOWED_FIREWALL_STATUS = {
    "blocked",
    "hold",
    "review_required",
    "eligible_for_operator_review",
}
FORBIDDEN_FIREWALL_STATUS = {
    "approved",
    "activated",
    "live",
    "executing",
    "production_ready",
}


class OverlayExecutionReadinessFirewallPacket(BaseModel):
    schema_version: Literal["OverlayExecutionReadinessFirewallPacket.v1"] = (
        "OverlayExecutionReadinessFirewallPacket.v1"
    )
    firewall_id: str
    overlay_hash: str
    readiness_hash: str
    governance_hash: str
    containment_hash: str
    resolution_hash: str
    firewall_status: str
    blocked_reasons: list[str]
    deterministic_firewall_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(
        overlay_hash: str,
        readiness_hash: str,
        governance_hash: str,
        containment_hash: str,
        resolution_hash: str,
        firewall_status: str,
        blocked_reasons: list[str],
    ) -> str:
        return hashlib.sha256(
            f"{overlay_hash}|{readiness_hash}|{governance_hash}|{containment_hash}|{resolution_hash}|{firewall_status}|{'|'.join(blocked_reasons)}".encode()
        ).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayExecutionReadinessFirewallPacket":
        self.authority.assert_locked()
        if (
            self.firewall_status in FORBIDDEN_FIREWALL_STATUS
            or self.firewall_status not in ALLOWED_FIREWALL_STATUS
        ):
            raise ValueError("forbidden firewall status")
        if self.firewall_status in {"blocked", "hold"} and not self.blocked_reasons:
            raise ValueError("blocked reasons required")
        h = self.compute_hash(
            self.overlay_hash,
            self.readiness_hash,
            self.governance_hash,
            self.containment_hash,
            self.resolution_hash,
            self.firewall_status,
            self.blocked_reasons,
        )
        if h != self.deterministic_firewall_hash:
            raise ValueError("firewall hash mismatch")
        return self

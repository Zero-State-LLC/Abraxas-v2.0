from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class OverlayFirewallContainmentPacket(BaseModel):
    schema_version: Literal["OverlayFirewallContainmentPacket.v1"] = (
        "OverlayFirewallContainmentPacket.v1"
    )
    containment_firewall_id: str
    overlay_hash: str
    containment_restrictions: list[str]
    critical_recommendations: list[str]
    containment_safe: bool
    deterministic_containment_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(
        overlay_hash: str, restrictions: list[str], critical: list[str], safe: bool
    ) -> str:
        return hashlib.sha256(
            f"{overlay_hash}|{'|'.join(restrictions)}|{'|'.join(critical)}|{safe}".encode()
        ).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        if self.containment_safe != (len(self.critical_recommendations) == 0):
            raise ValueError("containment safety invalid")
        if self.deterministic_containment_hash != self.compute_hash(
            self.overlay_hash,
            self.containment_restrictions,
            self.critical_recommendations,
            self.containment_safe,
        ):
            raise ValueError("containment hash mismatch")
        return self

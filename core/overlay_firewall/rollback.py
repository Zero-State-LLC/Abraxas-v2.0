from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class OverlayFirewallRollbackPacket(BaseModel):
    schema_version: Literal["OverlayFirewallRollbackPacket.v1"] = (
        "OverlayFirewallRollbackPacket.v1"
    )
    rollback_firewall_id: str
    overlay_hash: str
    rollback_ready: bool
    rollback_blockers: list[str]
    deterministic_rollback_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(overlay_hash: str, ready: bool, blockers: list[str]) -> str:
        return hashlib.sha256(
            f"{overlay_hash}|{ready}|{'|'.join(blockers)}".encode()
        ).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        if self.rollback_ready and self.rollback_blockers:
            raise ValueError("rollback blockers present")
        if self.deterministic_rollback_hash != self.compute_hash(
            self.overlay_hash, self.rollback_ready, self.rollback_blockers
        ):
            raise ValueError("rollback hash mismatch")
        return self

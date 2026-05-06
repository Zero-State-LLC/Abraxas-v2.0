from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanarySchedulePacket(BaseModel):
    schema_version: Literal["CanarySchedulePacket.v1"] = "CanarySchedulePacket.v1"
    schedule_id: str
    overlay_hash: str
    policy_hash: str
    eligibility_hash: str
    window_hash: str
    schedule_status: Literal["proposed", "blocked", "replay_validated", "operator_review_required", "rejected", "archived"]
    deterministic_schedule_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(overlay_hash: str, policy_hash: str, eligibility_hash: str, window_hash: str, schedule_status: str) -> str:
        return hashlib.sha256(f"{overlay_hash}|{policy_hash}|{eligibility_hash}|{window_hash}|{schedule_status}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "CanarySchedulePacket":
        self.authority.assert_locked()
        if self.deterministic_schedule_hash != self.compute_hash(self.overlay_hash, self.policy_hash, self.eligibility_hash, self.window_hash, self.schedule_status):
            raise ValueError("hash")
        return self

from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryScheduleWindowPacket(BaseModel):
    schema_version: Literal["CanaryScheduleWindowPacket.v1"] = "CanaryScheduleWindowPacket.v1"
    window_id: str
    overlay_hash: str
    policy_hash: str
    window_generation: int
    window_scope: Literal["shadow_observation", "replay_observation", "diagnostic_observation"]
    observation_ticks: int
    deterministic_window_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(overlay_hash: str, policy_hash: str, generation: int, scope: str, ticks: int) -> str:
        return hashlib.sha256(f"{overlay_hash}|{policy_hash}|{generation}|{scope}|{ticks}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "CanaryScheduleWindowPacket":
        self.authority.assert_locked()
        if self.observation_ticks <= 0:
            raise ValueError("positive")
        if self.deterministic_window_hash != self.compute_hash(self.overlay_hash, self.policy_hash, self.window_generation, self.window_scope, self.observation_ticks):
            raise ValueError("hash")
        return self

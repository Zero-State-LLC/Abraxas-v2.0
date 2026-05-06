from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class SandboxConvergencePacket(BaseModel):
    schema_version: Literal["SandboxConvergencePacket.v1"] = "SandboxConvergencePacket.v1"
    convergence_id: str
    branch_hash: str
    compared_runs: int
    deterministic_replays: int
    convergence_score: float
    divergence_events: int
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_score(compared_runs: int, deterministic_replays: int, divergence_events: int) -> float:
        if compared_runs <= 0:
            return 0.0
        return round(max(0.0, (deterministic_replays - divergence_events) / compared_runs), 6)

    @model_validator(mode="after")
    def _validate(self) -> "SandboxConvergencePacket":
        self.authority.assert_locked()
        if self.convergence_score != self.compute_score(self.compared_runs, self.deterministic_replays, self.divergence_events):
            raise ValueError("deterministic convergence calculation required")
        return self

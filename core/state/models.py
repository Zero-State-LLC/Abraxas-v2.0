from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class GovernedStateSnapshot(BaseModel):
    schema_version: Literal["GovernedStateSnapshot.v1"] = "GovernedStateSnapshot.v1"
    snapshot_id: str
    pipeline_id: str
    state_hash: str
    parent_state_hash: str | None = None
    execution_hash: str
    replay_hash: str | None = None
    topology_hash: str
    telemetry_hash: str
    authority: Authority = Authority()
    stabilization_state: str = "unstable"
    status: str = "pending"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "GovernedStateSnapshot":
        self.authority.assert_locked()
        if self.parent_state_hash and self.parent_state_hash == self.state_hash:
            raise ValueError("parent_state_hash must differ from state_hash")
        if self.pipeline_id == "projection_only" and self.execution_hash:
            raise ValueError("projection-only snapshots forbidden from execution authority")
        return self

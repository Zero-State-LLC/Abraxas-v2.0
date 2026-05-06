from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class WeightOverlayPacket(BaseModel):
    schema_version: Literal["WeightOverlayPacket.v1"] = "WeightOverlayPacket.v1"
    overlay_id: str
    proposal_hash: str
    overlay_generation: int
    overlay_weight: float
    deterministic_overlay_hash: str
    authority: Authority = Authority()
    status: str = "simulated"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(proposal_hash: str, overlay_generation: int, overlay_weight: float) -> str:
        return hashlib.sha256(f"{proposal_hash}|{overlay_generation}|{overlay_weight:.6f}".encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> "WeightOverlayPacket":
        self.authority.assert_locked()
        if not 0 <= self.overlay_weight <= 1:
            raise ValueError("invalid overlay weights fail closed")
        if self.deterministic_overlay_hash != self.compute_hash(self.proposal_hash, self.overlay_generation, self.overlay_weight):
            raise ValueError("deterministic overlay generation")
        return self

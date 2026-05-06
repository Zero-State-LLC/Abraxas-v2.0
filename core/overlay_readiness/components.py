from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from core.governance.authority import Authority

class OverlayReadinessComponentPacket(BaseModel):
    schema_version: Literal["OverlayReadinessComponentPacket.v1"] = "OverlayReadinessComponentPacket.v1"
    component_id: str
    overlay_hash: str
    component_type: Literal["governance","risk","topology","containment","resolution","replay","rollback","operator_load"]
    component_score: float = Field(ge=0, le=1)
    component_reason: str
    deterministic_component_hash: str
    authority: Authority = Authority()
    status: Literal["passed","failed","not_computable"]

    @staticmethod
    def compute_hash(overlay_hash: str, component_type: str, component_score: float, component_reason: str) -> str:
        return hashlib.sha256(f"{overlay_hash}|{component_type}|{component_score:.8f}|{component_reason}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayReadinessComponentPacket":
        self.authority.assert_locked()
        if self.deterministic_component_hash != self.compute_hash(self.overlay_hash, self.component_type, self.component_score, self.component_reason):
            raise ValueError("component hash")
        return self

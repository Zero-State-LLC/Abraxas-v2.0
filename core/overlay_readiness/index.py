from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from core.governance.authority import Authority

class OverlayReadinessIndexPacket(BaseModel):
    schema_version: Literal["OverlayReadinessIndexPacket.v1"] = "OverlayReadinessIndexPacket.v1"
    readiness_id: str
    overlay_hash: str
    governance_score: float = Field(ge=0, le=1)
    risk_score: float = Field(ge=0, le=1)
    topology_score: float = Field(ge=0, le=1)
    containment_score: float = Field(ge=0, le=1)
    resolution_score: float = Field(ge=0, le=1)
    replay_score: float = Field(ge=0, le=1)
    rollback_score: float = Field(ge=0, le=1)
    operator_load_score: float = Field(ge=0, le=1)
    aggregate_readiness_score: float = Field(ge=0, le=1)
    readiness_band: Literal["blocked","watch","review_ready","stable_candidate"]
    deterministic_readiness_hash: str
    authority: Authority = Authority()
    status: Literal["passed","failed","not_computable"]

    @staticmethod
    def compute_hash(overlay_hash: str, values: list[float], aggregate: float, readiness_band: str) -> str:
        scores = "|".join(f"{v:.8f}" for v in values)
        return hashlib.sha256(f"{overlay_hash}|{scores}|{aggregate:.8f}|{readiness_band}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayReadinessIndexPacket":
        self.authority.assert_locked()
        vals=[self.governance_score,self.risk_score,self.topology_score,self.containment_score,self.resolution_score,self.replay_score,self.rollback_score,self.operator_load_score]
        if self.deterministic_readiness_hash != self.compute_hash(self.overlay_hash, vals, self.aggregate_readiness_score, self.readiness_band):
            raise ValueError("readiness hash")
        return self

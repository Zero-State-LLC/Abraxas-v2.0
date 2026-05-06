from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class OverlayExposurePacket(BaseModel):
    schema_version: Literal["OverlayExposurePacket.v1"] = "OverlayExposurePacket.v1"
    exposure_id: str
    rollback_dependency_count: int = Field(ge=0)
    replay_dependency_count: int = Field(ge=0)
    governance_dependency_depth: int = Field(ge=0)
    operator_review_load: int = Field(ge=0)
    exposure_score: float = Field(ge=0, le=1)
    deterministic_exposure_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(rollback_dependency_count: int, replay_dependency_count: int, governance_dependency_depth: int, operator_review_load: int, exposure_score: float) -> str:
        return hashlib.sha256(f"{rollback_dependency_count}|{replay_dependency_count}|{governance_dependency_depth}|{operator_review_load}|{exposure_score:.8f}".encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> "OverlayExposurePacket":
        if self.deterministic_exposure_hash != self.compute_hash(self.rollback_dependency_count, self.replay_dependency_count, self.governance_dependency_depth, self.operator_review_load, self.exposure_score):
            raise ValueError('exposure hash')
        return self

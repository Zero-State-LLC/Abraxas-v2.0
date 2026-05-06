from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class OverlayGovernanceSaturationPacket(BaseModel):
    schema_version: Literal["OverlayGovernanceSaturationPacket.v1"] = "OverlayGovernanceSaturationPacket.v1"
    saturation_id: str
    pending_review_count: int = Field(ge=0)
    governance_backlog: int = Field(ge=0)
    unresolved_diagnostics: int = Field(ge=0)
    overlay_density: float = Field(ge=0, le=1)
    review_saturation_pressure: float = Field(ge=0, le=1)
    saturation_score: float = Field(ge=0, le=1)
    deterministic_saturation_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(pending_review_count: int, governance_backlog: int, unresolved_diagnostics: int, overlay_density: float, review_saturation_pressure: float, saturation_score: float) -> str:
        return hashlib.sha256(f"{pending_review_count}|{governance_backlog}|{unresolved_diagnostics}|{overlay_density:.8f}|{review_saturation_pressure:.8f}|{saturation_score:.8f}".encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> "OverlayGovernanceSaturationPacket":
        if self.deterministic_saturation_hash != self.compute_hash(self.pending_review_count, self.governance_backlog, self.unresolved_diagnostics, self.overlay_density, self.review_saturation_pressure, self.saturation_score):
            raise ValueError('saturation hash')
        return self

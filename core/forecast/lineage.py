from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class ForecastLineageNode(BaseModel):
    forecast_hash: str
    parent_hash: str | None = None
    generation: int
    calibration_hash: str | None = None


class ForecastLineagePacket(BaseModel):
    schema_version: Literal["ForecastLineagePacket.v1"] = "ForecastLineagePacket.v1"
    lineage_id: str
    lineage_depth: int
    lineage_nodes: list[ForecastLineageNode]
    deterministic_lineage_hash: str
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(nodes: list[ForecastLineageNode]) -> str:
        return hashlib.sha256("|".join(f"{n.forecast_hash}:{n.parent_hash}:{n.generation}:{n.calibration_hash}" for n in nodes).encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ForecastLineagePacket":
        self.authority.assert_locked()
        if self.lineage_depth != len(self.lineage_nodes):
            raise ValueError("lineage deterministic")
        seen = set()
        for n in self.lineage_nodes:
            if n.forecast_hash in seen:
                raise ValueError("cyclic lineage fail closed")
            seen.add(n.forecast_hash)
        if self.compute_hash(self.lineage_nodes) != self.deterministic_lineage_hash:
            raise ValueError("lineage deterministic")
        return self

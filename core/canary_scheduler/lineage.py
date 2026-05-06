from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryScheduleLineageNode(BaseModel):
    schedule_hash: str
    parent_hash: str | None = None
    generation: int
    window_hash: str | None = None


class CanaryScheduleLineagePacket(BaseModel):
    schema_version: Literal["CanaryScheduleLineagePacket.v1"] = "CanaryScheduleLineagePacket.v1"
    lineage_id: str
    lineage_nodes: list[CanaryScheduleLineageNode]
    lineage_depth: int
    deterministic_lineage_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(nodes: list[CanaryScheduleLineageNode]) -> str:
        return hashlib.sha256("|".join(f"{n.schedule_hash}:{n.parent_hash}:{n.generation}:{n.window_hash}" for n in nodes).encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "CanaryScheduleLineagePacket":
        self.authority.assert_locked()
        seen: set[str] = set()
        for n in self.lineage_nodes:
            if n.schedule_hash in seen or n.parent_hash == n.schedule_hash:
                raise ValueError("cyclic lineage fail closed")
            seen.add(n.schedule_hash)
        if self.lineage_depth != len(self.lineage_nodes):
            raise ValueError("deterministic ordering")
        if self.deterministic_lineage_hash != self.compute_hash(self.lineage_nodes):
            raise ValueError("deterministic ordering")
        return self

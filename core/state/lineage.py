from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class StateLineageNode(BaseModel):
    state_hash: str
    parent_hash: str | None = None
    generation: int
    transition_hash: str | None = None


class StateLineagePacket(BaseModel):
    schema_version: Literal["StateLineagePacket.v1"] = "StateLineagePacket.v1"
    lineage_id: str
    lineage_depth: int
    lineage_nodes: list[StateLineageNode]
    deterministic_lineage_hash: str
    authority: Authority = Authority()
    status: str = "pending"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(nodes: list[StateLineageNode]) -> str:
        parts = [f"{n.state_hash}:{n.parent_hash}:{n.generation}:{n.transition_hash}" for n in nodes]
        return hashlib.sha256("|".join(parts).encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "StateLineagePacket":
        self.authority.assert_locked()
        by_hash = {n.state_hash: n for n in self.lineage_nodes}
        for n in self.lineage_nodes:
            if n.parent_hash and n.parent_hash not in by_hash:
                raise ValueError("invalid parent reference")
        seen = set()
        for n in self.lineage_nodes:
            cur = n
            path = set()
            while cur.parent_hash:
                if cur.state_hash in path:
                    raise ValueError("cyclic lineage fail closed")
                path.add(cur.state_hash)
                cur = by_hash[cur.parent_hash]
            seen |= path
        if self.deterministic_lineage_hash != self.compute_hash(self.lineage_nodes):
            raise ValueError("lineage hash mismatch")
        return self

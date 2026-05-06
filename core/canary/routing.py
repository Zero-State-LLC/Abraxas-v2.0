from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryRoutingPacket(BaseModel):
    schema_version: Literal["CanaryRoutingPacket.v1"] = "CanaryRoutingPacket.v1"
    routing_id: str
    overlay_hashes: list[str]
    replay_routes: list[str]
    sandbox_routes: list[str]
    blocked_routes: list[str]
    deterministic_routing_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(overlay_hashes: list[str], replay_routes: list[str], sandbox_routes: list[str], blocked_routes: list[str]) -> str:
        return hashlib.sha256("|".join([";".join(sorted(overlay_hashes)), ";".join(sorted(replay_routes)), ";".join(sorted(sandbox_routes)), ";".join(sorted(blocked_routes))]).encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "CanaryRoutingPacket":
        self.authority.assert_locked()
        if any("production" in r for r in [*self.replay_routes, *self.sandbox_routes]):
            raise ValueError("no production routing")
        if self.deterministic_routing_hash != self.compute_hash(self.overlay_hashes, self.replay_routes, self.sandbox_routes, self.blocked_routes):
            raise ValueError("routing hash mismatch")
        return self

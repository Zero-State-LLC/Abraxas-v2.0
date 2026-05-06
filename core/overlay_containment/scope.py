from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field


class OverlayContainmentScopePacket(BaseModel):
    schema_version: Literal["OverlayContainmentScopePacket.v1"] = "OverlayContainmentScopePacket.v1"
    scope_id: str
    affected_overlays: list[str]
    affected_routes: list[str]
    affected_scheduler_windows: list[str]
    affected_promotion_candidates: list[str]
    containment_scope_depth: int
    scope_score: float = Field(ge=0, le=1)
    status: Literal["passed", "failed", "not_computable"]

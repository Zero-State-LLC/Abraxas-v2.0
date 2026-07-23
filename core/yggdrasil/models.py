"""YGGDRASIL route graph models for ABRAXAS v2.0."""

from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, field_validator, model_validator

from core.governance.authority import Authority
from core.governance.doctrine import SCHEMA_VERSION_YGGDRASIL


class NodeType(str, Enum):
    subsystem = "subsystem"
    pipeline = "pipeline"
    rune = "rune"
    artifact = "artifact"
    review_gate = "review_gate"


class EdgeType(str, Enum):
    depends_on = "depends_on"
    routes_to = "routes_to"
    emits = "emits"
    validates = "validates"
    reviews = "reviews"
    projects = "projects"


class AuthorityBoundary(str, Enum):
    none = "none"
    lane_crossing = "lane_crossing"
    promotion_boundary = "promotion_boundary"
    forecast_boundary = "forecast_boundary"
    runtime_boundary = "runtime_boundary"


class YggdrasilNode(BaseModel):
    node_id: str
    node_type: NodeType
    lane: str
    rune_id: Optional[str] = None  # additive hygiene; required only for explicit bindings

    model_config = {"frozen": True}


class YggdrasilEdge(BaseModel):
    source: str
    target: str
    edge_type: EdgeType
    authority_boundary: AuthorityBoundary = AuthorityBoundary.none
    validation_required: bool = False

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _boundary_requires_validation(self) -> "YggdrasilEdge":
        if self.authority_boundary != AuthorityBoundary.none and not self.validation_required:
            raise ValueError(
                f"Edge {self.source!r}->{self.target!r}: "
                "authority_boundary != 'none' requires validation_required=True"
            )
        return self


class YggdrasilRouteGraph(BaseModel):
    """Route/dependency topology for a single pipeline."""

    schema_version: Literal["YggdrasilRouteGraph.v1"] = SCHEMA_VERSION_YGGDRASIL
    pipeline_id: str
    nodes: list[YggdrasilNode]
    edges: list[YggdrasilEdge]
    authority: Authority

    model_config = {"frozen": True}

    @field_validator("nodes")
    @classmethod
    def _nodes_not_empty(cls, v: list[YggdrasilNode]) -> list[YggdrasilNode]:
        if not v:
            raise ValueError("nodes cannot be empty")
        return v

    @field_validator("edges")
    @classmethod
    def _edges_not_empty(cls, v: list[YggdrasilEdge]) -> list[YggdrasilEdge]:
        if not v:
            raise ValueError("edges cannot be empty")
        return v

    @model_validator(mode="after")
    def _validate_edge_refs_and_authority(self) -> "YggdrasilRouteGraph":
        node_ids = {n.node_id for n in self.nodes}
        for edge in self.edges:
            if edge.source not in node_ids:
                raise ValueError(f"Edge source {edge.source!r} not in nodes")
            if edge.target not in node_ids:
                raise ValueError(f"Edge target {edge.target!r} not in nodes")
        self.authority.assert_locked()
        return self

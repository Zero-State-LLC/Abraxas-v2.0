"""Pipeline contract models for ABRAXAS v2.0."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator

from core.governance.authority import Authority
from core.governance.doctrine import SCHEMA_VERSION_PIPELINE


class PipelineLane(str, Enum):
    SHADOW = "SHADOW"
    FORECAST_GATED = "FORECAST_GATED"
    GOVERNANCE = "GOVERNANCE"
    GOVERNANCE_SHADOW = "GOVERNANCE_SHADOW"
    PROJECTION = "PROJECTION"


class FinalState(str, Enum):
    hold = "hold"
    repair = "repair"
    reject = "reject"
    eligible_for_shadow_stabilization = "eligible_for_shadow_stabilization"
    eligible_for_operator_review = "eligible_for_operator_review"
    not_computable = "not_computable"


class PipelineContractV11(BaseModel):
    """Tier-1 pipeline automation contract (schema v1.1)."""

    schema_version: Literal["AbraxasPipelineAutomationContract.v1.1"] = SCHEMA_VERSION_PIPELINE
    pipeline_id: str
    trigger: str
    owner_subsystem: str
    lane: PipelineLane
    typed_ir_schema: str
    required_runes: list[str]
    yggdrasil_nodes: list[str]
    required_artifacts: list[str]
    final_state_policy: list[FinalState]
    authority: Authority

    model_config = {"frozen": True}

    @field_validator("required_runes")
    @classmethod
    def _runes_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("required_runes cannot be empty")
        return v

    @field_validator("yggdrasil_nodes")
    @classmethod
    def _nodes_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("yggdrasil_nodes cannot be empty")
        return v

    @field_validator("trigger")
    @classmethod
    def _trigger_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("trigger cannot be empty")
        return v

    @field_validator("typed_ir_schema")
    @classmethod
    def _schema_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("typed_ir_schema cannot be empty")
        return v

    @model_validator(mode="after")
    def _authority_locked(self) -> "PipelineContractV11":
        self.authority.assert_locked()
        return self

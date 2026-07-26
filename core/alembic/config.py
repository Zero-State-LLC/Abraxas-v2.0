"""Versioned Alembic configuration loading and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator

from core.alembic.constants import DEFAULT_SCORE_WEIGHTS, SCORE_COMPONENTS
from core.canonical.json import canonical_hash


class RouterPolicy(BaseModel):
    model_config = {"frozen": True, "extra": "forbid"}

    schema_version: str = "AlembicRouterPolicy.v1"
    policy_id: str = "alembic.router_policy.v1"
    score_weight_version: str = "alembic.weights.v1"
    score_weights: dict[str, float] = Field(
        default_factory=lambda: dict(DEFAULT_SCORE_WEIGHTS)
    )
    tie_epsilon: float = 1e-9
    require_calibration_when_flagged: bool = True
    max_selected_candidates: int = 3
    allow_hybrid: bool = True
    default_fusion_method: str = "deterministic_evidence_union"
    eligibility: dict[str, Any] = Field(default_factory=dict)
    shadow: dict[str, Any] = Field(
        default_factory=lambda: {
            "promotion_allowed": False,
            "policy_mutation_allowed": False,
            "may_influence_active": False,
        }
    )
    resource_ceilings: dict[str, float] = Field(default_factory=dict)
    operator_gate_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _validate_weights(self) -> RouterPolicy:
        missing = sorted(set(SCORE_COMPONENTS) - set(self.score_weights))
        unknown = sorted(set(self.score_weights) - set(SCORE_COMPONENTS))
        if missing:
            raise ValueError(f"score_weights missing components: {missing}")
        if unknown:
            raise ValueError(f"score_weights unknown components: {unknown}")
        total = sum(self.score_weights.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"score_weights must sum to 1.0, got {total}")
        for key, value in self.score_weights.items():
            if value < 0.0 or value > 1.0:
                raise ValueError(f"score weight out of bounds: {key}={value}")
        shadow = self.shadow
        if shadow.get("promotion_allowed") is True:
            raise ValueError("shadow.promotion_allowed must be false")
        if shadow.get("policy_mutation_allowed") is True:
            raise ValueError("shadow.policy_mutation_allowed must be false")
        if shadow.get("may_influence_active") is True:
            raise ValueError("shadow.may_influence_active must be false")
        return self


def load_router_policy(path: str | Path) -> RouterPolicy:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return RouterPolicy.model_validate(payload)


def policy_hash(policy: RouterPolicy) -> str:
    return canonical_hash(policy.model_dump(mode="python"))


def default_router_policy() -> RouterPolicy:
    return RouterPolicy()

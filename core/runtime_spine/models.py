from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class RuntimePosture(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    BLOCKED = "BLOCKED"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"


class RuntimeLane(str, Enum):
    SHADOW = "SHADOW"
    FORECAST = "FORECAST"
    PROJECTION = "PROJECTION"
    CANON = "CANON"
    OPERATOR = "OPERATOR"
    GOVERNANCE = "GOVERNANCE"


class RuntimeScope(str, Enum):
    OBSERVATION = "OBSERVATION"
    DIAGNOSE = "DIAGNOSE"
    ANNOTATE = "ANNOTATE"
    FORECAST = "FORECAST"
    INFERENCE = "INFERENCE"
    RENDER = "RENDER"
    DOCTRINE = "DOCTRINE"
    REGISTRY = "REGISTRY"
    CANON = "CANON"
    APPROVE = "APPROVE"
    DENY = "DENY"
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"
    OPERATOR = "OPERATOR"
    GOVERNANCE = "GOVERNANCE"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"


class RuntimeState(str, Enum):
    SHADOW_ONLY = "SHADOW_ONLY"
    CANARY = "CANARY"
    LIMITED_PROMOTION = "LIMITED_PROMOTION"
    CANON_ACTIVE = "CANON_ACTIVE"
    ARCHIVED = "ARCHIVED"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"


_VALID_LANES: frozenset[str] = frozenset(e.value for e in RuntimeLane)
_VALID_SCOPES: frozenset[str] = frozenset(e.value for e in RuntimeScope)
_VALID_STATES: frozenset[str] = frozenset(e.value for e in RuntimeState)


@dataclass(frozen=True)
class RuntimeRoute:
    subsystem_id: str
    lane: str
    promotion_state: str
    authority_scope: str

    def __post_init__(self) -> None:
        if self.lane not in _VALID_LANES:
            raise ValueError(f"invalid_lane: {self.lane!r} is not a recognized RuntimeLane value")
        if self.authority_scope not in _VALID_SCOPES:
            raise ValueError(f"invalid_scope: {self.authority_scope!r} is not a recognized RuntimeScope value")
        if self.promotion_state not in _VALID_STATES:
            raise ValueError(f"invalid_state: {self.promotion_state!r} is not a recognized RuntimeState value")



@dataclass(frozen=True)
class RuntimeInvocation:
    route: RuntimeRoute
    payload: Mapping[str, Any]
    canon_attestation: str | None = None
    outcome_binding: str | None = None


@dataclass(frozen=True)
class RuntimeDecision:
    posture: RuntimePosture
    decision_hash: str
    reason: str


@dataclass(frozen=True)
class RuntimeReceipt:
    invocation_hash: str
    decision_hash: str
    posture: RuntimePosture


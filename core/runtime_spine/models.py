from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class RuntimePosture(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    BLOCKED = "BLOCKED"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"


@dataclass(frozen=True)
class RuntimeRoute:
    subsystem_id: str
    lane: str
    promotion_state: str
    authority_scope: str


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


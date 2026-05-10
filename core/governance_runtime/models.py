from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping


class GovernanceLane(str, Enum):
    SHADOW = "SHADOW"
    FORECAST = "FORECAST"
    PROJECTION = "PROJECTION"
    CANON = "CANON"
    OPERATOR = "OPERATOR"


class PromotionState(str, Enum):
    SHADOW_ONLY = "SHADOW_ONLY"
    CANARY = "CANARY"
    LIMITED_PROMOTION = "LIMITED_PROMOTION"
    CANON_ACTIVE = "CANON_ACTIVE"
    ARCHIVED = "ARCHIVED"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"


class AuthorityScope(str, Enum):
    OBSERVATION = "OBSERVATION"
    DIAGNOSE = "DIAGNOSE"
    ANNOTATE = "ANNOTATE"
    FORECAST = "FORECAST"
    INFERENCE = "INFERENCE"
    RENDER = "RENDER"
    DOCTRINE = "DOCTRINE"
    REGISTRY = "REGISTRY"
    APPROVE = "APPROVE"
    DENY = "DENY"
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"
    OPERATOR = "OPERATOR"
    CANON = "CANON"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"


@dataclass(frozen=True)
class ValidationFinding:
    code: str
    message: str
    severity: str = "error"
    source_lane: str | None = None
    target_scope: str | None = None


@dataclass(frozen=True)
class ValidationReport:
    status: str
    findings: tuple[ValidationFinding, ...]
    receipt_hash: str


@dataclass(frozen=True)
class GovernanceReceipt:
    runtime: str
    status: str
    payload: Mapping[str, Any]
    canonical_payload_json: str
    sha256: str

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["payload"] = dict(self.payload)
        return data

"""Stabilization readiness models — deterministic dataclasses."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def stable_hash(obj: Any) -> str:
    digest = hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


@dataclass(frozen=True, slots=True)
class StabilizationScope:
    python: bool = True
    typescript: bool = True
    schemas: bool = True
    artifacts: bool = True
    cli: bool = True
    runtime_activation: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StabilizationCampaignState:
    campaign_id: str
    campaign_class: str
    phase: str
    scope: StabilizationScope
    feature_expansion_allowed: bool
    terminal_decisions: List[str]
    work_order_id: str = "WO-ABX-STABILIZATION-SKILL-FOUNDATION-001"
    state_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "campaign_id": self.campaign_id,
            "campaign_class": self.campaign_class,
            "phase": self.phase,
            "scope": self.scope.to_dict(),
            "feature_expansion_allowed": self.feature_expansion_allowed,
            "terminal_decisions": list(self.terminal_decisions),
            "work_order_id": self.work_order_id,
        }
        if self.state_hash:
            d["state_hash"] = self.state_hash
        return d

    def compute_hash(self) -> str:
        payload = self.to_dict()
        payload.pop("state_hash", None)
        return stable_hash(payload)


@dataclass(frozen=True, slots=True)
class ContractRecord:
    contract_id: str
    language: str
    surface: str
    classification: str
    consumers: List[str] = field(default_factory=list)
    validators: List[str] = field(default_factory=list)
    schemas: List[str] = field(default_factory=list)
    compatibility_policy: str = "BACKWARD_COMPATIBLE"
    evidence_complete: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ConformanceCase:
    case_id: str
    input_payload: Dict[str, Any]
    expected: Dict[str, Any]
    comparison_mode: str
    implementations: List[str]
    allowed_variance: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["input"] = d.pop("input_payload")
        return d


@dataclass(frozen=True, slots=True)
class ReproducibilityFinding:
    surface: str
    classification: str
    evidence_refs: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StabilizationGateDecision:
    decision: str
    python_ready: bool
    typescript_ready: bool
    contract_inventory_complete: bool
    conformance_corpus_ready: bool
    reproducibility_ready: bool
    canonical_artifact_safety_ready: bool
    full_suite_confidence: str
    blocking_findings: List[str] = field(default_factory=list)
    bounded_exceptions: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    operator_action_required: bool = True
    decision_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.decision_hash:
            d["decision_hash"] = self.decision_hash
        return d

    def compute_hash(self) -> str:
        payload = self.to_dict()
        payload.pop("decision_hash", None)
        return stable_hash(payload)


@dataclass(frozen=True, slots=True)
class StabilizationWorkPacket:
    packet_id: str
    phase: str
    priority_rank: int
    title: str
    bounded_scope: List[str]
    entry_criteria: List[str]
    exit_criteria: List[str]
    feature_expansion_allowed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StabilizationDirectorReceipt:
    rune: str
    campaign_state_hash: str
    phase: str
    selected_packets: List[str]
    residual_risks: List[str]
    next_phase: str
    boundary: str
    receipt_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.receipt_hash:
            d["receipt_hash"] = self.receipt_hash
        return d

    def compute_hash(self) -> str:
        payload = self.to_dict()
        payload.pop("receipt_hash", None)
        return stable_hash(payload)
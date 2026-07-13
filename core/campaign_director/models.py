"""Campaign Director models - deterministic dataclasses for state, plans, receipts.

Follows Governance V3: frozen where possible, canonical serialization, no wall-clock in hashes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# Supported execution modes per spec
EXECUTION_MODES = [
    "MODE_A_STANDARD_SINGLE_CANDIDATE_BATCH",
    "MODE_B_FAMILY_AWARE_BOUNDED_BATCH",
    "MODE_C_MULTI_GAP_RECONCILIATION",
    "MODE_D_ACCELERATION_TOOLING",
    "MODE_E_ACCELERATION_AUTHORIZATION_GATE",
    "MODE_F_OPERATOR_DECISION_REQUIRED",
]

RECOVERY_STATUSES = ["VALID", "PARTIAL_RESUMABLE", "BROKEN_CONTINUITY", "HASH_MISMATCH", "CYCLE_GAP", "NOT_COMPUTABLE"]

PROTECTED_STATE_KEYS = [
    "authority_expanded",
    "canon_mutated",
    "production_activated",
    "promoted",
    "runtime_transitioned",
    "policy_reference_count",
]


def canonical_json(obj: Any) -> str:
    """Deterministic JSON with sorted keys, no whitespace variation."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def stable_hash(obj: Any) -> str:
    """SHA256 of canonical JSON, short display form for IDs."""
    digest = hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def short_id(digest: str) -> str:
    return digest[:16] if len(digest) > 16 else digest


@dataclass(frozen=True, slots=True)
class ProtectedState:
    authority_expanded: bool = False
    canon_mutated: bool = False
    production_activated: bool = False
    promoted: bool = False
    runtime_transitioned: bool = False
    policy_reference_count: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def is_valid(self) -> bool:
        return (
            not self.authority_expanded
            and not self.canon_mutated
            and not self.production_activated
            and not self.promoted
            and not self.runtime_transitioned
            and self.policy_reference_count == 3
        )

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ProtectedState":
        return cls(
            authority_expanded=d.get("authority_expanded", False),
            canon_mutated=d.get("canon_mutated", False),
            production_activated=d.get("production_activated", False),
            promoted=d.get("promoted", False),
            runtime_transitioned=d.get("runtime_transitioned", False),
            policy_reference_count=d.get("policy_reference_count", 3),
        )


@dataclass(frozen=True, slots=True)
class CampaignRecoveryResult:
    campaign_id: str
    latest_sealed_batch: str
    latest_completed_cycle: int
    completed_cycle_count: int
    continuation_mode: str
    next_batch: str
    next_cycles: List[int]
    candidate_count: int
    global_actionable_count: int
    oracle_primary_id: Optional[str]
    continuous_execution_eligible: bool
    protected_state: ProtectedState
    partial_artifacts: List[str] = field(default_factory=list)
    recovery_status: str = "VALID"
    recovery_hash: str = ""
    raw_artifacts: Dict[str, Any] = field(default_factory=dict, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["protected_state"] = self.protected_state.to_dict()
        if self.recovery_hash:
            d["recovery_hash"] = self.recovery_hash
        return d

    def compute_hash(self) -> str:
        payload = {
            "campaign_id": self.campaign_id,
            "latest_sealed_batch": self.latest_sealed_batch,
            "latest_completed_cycle": self.latest_completed_cycle,
            "completed_cycle_count": self.completed_cycle_count,
            "next_batch": self.next_batch,
            "next_cycles": self.next_cycles,
            "oracle_primary_id": self.oracle_primary_id,
            "protected_state": self.protected_state.to_dict(),
            "recovery_status": self.recovery_status,
        }
        return stable_hash(payload)


@dataclass(frozen=True, slots=True)
class BoundedExecutionPlan:
    plan_id: str
    campaign_id: str
    mode: str
    batch_id: str
    cycle_range: List[int]
    primary_candidates: List[str]
    companion_candidates: List[str] = field(default_factory=list)
    maximum_lifecycle_count: int = 3
    maximum_candidate_count: int = 3
    stop_before_cycle: int = 0
    protected_state_required: Dict[str, Any] = field(default_factory=dict)
    plan_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def compute_hash(self) -> str:
        payload = {
            "plan_id": self.plan_id,
            "campaign_id": self.campaign_id,
            "mode": self.mode,
            "batch_id": self.batch_id,
            "cycle_range": self.cycle_range,
            "primary_candidates": self.primary_candidates,
            "companion_candidates": self.companion_candidates,
            "stop_before_cycle": self.stop_before_cycle,
        }
        return stable_hash(payload)


@dataclass(frozen=True, slots=True)
class ModeDecision:
    director_run_id: str
    campaign_id: str
    mode: str
    authorized: bool
    reason: str
    decision_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DirectorReceipt:
    director_run_id: str
    campaign_id: str
    recovery_hash: str
    mode_decision_hash: str
    plan_hash: str
    executed_lifecycle_count: int = 0
    primary_candidates_completed: int = 0
    companion_candidates_completed: int = 0
    collateral_candidates_completed: int = 0
    distinct_gaps_closed: int = 0
    validation_failures: int = 0
    reconciliation_repairs: int = 0
    protected_state_changes: int = 0
    terminal_status: str = "CAMPAIGN_DIRECTOR_READ_ONLY_READY"
    continuation_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def compute_hash(self) -> str:
        return stable_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class ContinuationArtifact:
    campaign_id: str
    latest_sealed_batch: str
    latest_completed_cycle: int
    authorized_mode: str
    next_bounded_action: Dict[str, Any]
    oracle_handoff: Dict[str, Any]
    continuation_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.continuation_hash:
            d["continuation_hash"] = self.continuation_hash
        return d


# Candidate family and duplicate models (Phase 1/3 observation only)
@dataclass(frozen=True, slots=True)
class CandidateFamily:
    family_id: str
    family_type: str
    canonical_class: str
    governance_layer: int
    change_shape: str
    validation_risk: str
    shared_contract: str
    member_candidate_ids: List[str]
    execution_authority: str = "OBSERVATION_ONLY"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DuplicateGap:
    fingerprint: str
    classification: str  # UNIQUE_GAP, EXACT_DUPLICATE, LIKELY_DUPLICATE, ...
    candidate_ids: List[str]
    target_path: Optional[str] = None


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj: Any, indent: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=indent, sort_keys=True, default=str)
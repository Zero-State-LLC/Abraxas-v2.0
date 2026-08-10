from __future__ import annotations

from dataclasses import dataclass

from core.contract_validation import (
    ContractValidationFinding as ReplayLedgerValidationFinding,
    ContractValidationReport as ReplayLedgerValidationReport,
)

__all__ = [
    "ReplayDiffInputRef",
    "ReplayDivergenceFinding",
    "ReplayLedger",
    "ReplayLedgerEntry",
    "ReplayLedgerValidationFinding",
    "ReplayLedgerValidationReport",
    "ReplayLineageRef",
    "ReplayTemporalDiff",
    "ReplayTemporalStabilityScore",
]


@dataclass(frozen=True)
class ReplayLedgerEntry:
    entry_id: str
    replay_id: str
    replay_hash: str
    replay_status: str
    authorization_id: str
    authorization_hash: str
    determinism_report_hash: str
    rollback_plan_hash: str
    entry_index: int
    entry_policy: str


@dataclass(frozen=True)
class ReplayLineageRef:
    lineage_id: str
    parent_replay_id: str
    relation_policy: str


@dataclass(frozen=True)
class ReplayLedger:
    schema_version: str
    ledger_id: str
    entries: tuple[ReplayLedgerEntry, ...]
    lineage_refs: tuple[ReplayLineageRef, ...]
    ledger_status: str
    ledger_policy: str
    created_by_lane: str
    authority_ref: dict | None
    live_execution_allowed: bool
    mutation_allowed: bool
    routing_change_allowed: bool
    ledger_hash: str


@dataclass(frozen=True)
class ReplayDiffInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class ReplayDivergenceFinding:
    finding_id: str
    divergence_type: str
    severity: str
    base_value_policy: str
    candidate_value_policy: str
    finding_summary: str


@dataclass(frozen=True)
class ReplayTemporalStabilityScore:
    score_id: str
    run_count: int
    stable_run_count: int
    divergence_count: int
    stability_ratio: float
    stability_posture: str
    mutation_allowed: bool


@dataclass(frozen=True)
class ReplayTemporalDiff:
    schema_version: str
    diff_id: str
    base_replay_id: str
    base_replay_hash: str
    candidate_replay_id: str
    candidate_replay_hash: str
    input_refs: tuple[ReplayDiffInputRef, ...]
    divergence_findings: tuple[ReplayDivergenceFinding, ...]
    stability_score: ReplayTemporalStabilityScore
    diff_status: str
    created_by_lane: str
    authority_ref: dict | None
    live_execution_allowed: bool
    mutation_allowed: bool
    routing_change_allowed: bool
    diff_hash: str

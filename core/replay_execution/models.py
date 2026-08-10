from __future__ import annotations

from dataclasses import dataclass

from core.contract_validation import (
    ContractValidationFinding as ReplayValidationFinding,
    ContractValidationReport as ReplayValidationReport,
)

__all__ = [
    "AuthorityRef",
    "ReplayDeterminismReport",
    "ReplayExecutionEnvelope",
    "ReplayExecutionReceipt",
    "ReplayInputRef",
    "ReplayMutationPlan",
    "ReplayRollbackPlan",
    "ReplayValidationFinding",
    "ReplayValidationReport",
]


@dataclass(frozen=True)
class ReplayInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class ReplayMutationPlan:
    mutation_plan_id: str
    target_scope: str
    target_artifacts: tuple[str, ...]
    planned_operations: tuple[str, ...]
    operation_count: int
    live_apply_allowed: bool


@dataclass(frozen=True)
class ReplayRollbackPlan:
    rollback_plan_id: str
    rollback_available: bool
    rollback_operations: tuple[str, ...]
    rollback_operation_count: int
    rollback_verification_policy: str
    rollback_verified_in_replay: bool


@dataclass(frozen=True)
class ReplayExecutionReceipt:
    receipt_id: str
    sandbox_policy: str
    simulated_operation_hashes: tuple[str, ...]
    live_side_effects_detected: bool
    receipt_hash: str


@dataclass(frozen=True)
class ReplayDeterminismReport:
    report_id: str
    run_count: int
    all_runs_identical: bool
    canonical_output_hashes: tuple[str, ...]
    nondeterminism_detected: bool
    determinism_policy: str


@dataclass(frozen=True)
class AuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class ReplayExecutionEnvelope:
    schema_version: str
    replay_id: str
    authorization_id: str
    authorization_hash: str
    authorization_audit_closure_id: str
    authorization_audit_closure_hash: str
    input_refs: tuple[ReplayInputRef, ...]
    mutation_plan: ReplayMutationPlan
    rollback_plan: ReplayRollbackPlan
    execution_receipt: ReplayExecutionReceipt
    determinism_report: ReplayDeterminismReport
    replay_status: str
    created_by_lane: str
    authority_ref: AuthorityRef | None
    live_execution_allowed: bool
    mutation_allowed: bool
    routing_change_allowed: bool
    adapter_activation_allowed: bool
    replay_hash: str

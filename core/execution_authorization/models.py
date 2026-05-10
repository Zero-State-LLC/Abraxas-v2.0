from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionAuthorizationScope:
    scope_type: str
    scope_id: str


@dataclass(frozen=True)
class ExecutionAuthorityRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class ExecutionReplayGuard:
    replay_guard_id: str
    idempotency_key: str
    input_hashes: tuple[str, ...]
    single_use_policy: bool
    replay_policy: str


@dataclass(frozen=True)
class ExecutionExpiryPolicy:
    expiry_policy_id: str
    expiry_mode: str
    max_execution_window_count: int
    expired_behavior: str


@dataclass(frozen=True)
class ExecutionRollbackRequirement:
    rollback_required: bool
    rollback_plan_ref: str
    rollback_artifact_refs: tuple[str, ...]
    rollback_verification_required: bool


@dataclass(frozen=True)
class AuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class ExecutionAuthorizationPacket:
    schema_version: str
    authorization_id: str
    decision_packet_id: str
    decision_packet_hash: str
    proposal_id: str
    proposal_hash: str
    scope: ExecutionAuthorizationScope
    authority_refs: tuple[ExecutionAuthorityRef, ...]
    replay_guard: ExecutionReplayGuard
    expiry_policy: ExecutionExpiryPolicy
    rollback_requirement: ExecutionRollbackRequirement
    authorization_status: str
    created_by_lane: str
    authority_ref: AuthorityRef | None
    execution_authorized: bool
    mutation_allowed: bool
    routing_change_allowed: bool
    authorization_hash: str


@dataclass(frozen=True)
class ExecutionAuthorizationValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class ExecutionAuthorizationValidationReport:
    status: str
    findings: tuple[ExecutionAuthorizationValidationFinding, ...]
    receipt_hash: str

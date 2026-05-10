from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthorizationAuditInputRef:
    source_type: str
    source_id: str
    source_hash: str


@dataclass(frozen=True)
class AuthorizationLineageCheck:
    check_id: str
    status: str
    findings: tuple[str, ...]
    required_refs_present: bool
    policy: str


@dataclass(frozen=True)
class AuthorizationReplayGuardCheck:
    check_id: str
    status: str
    findings: tuple[str, ...]
    required_refs_present: bool
    policy: str


@dataclass(frozen=True)
class AuthorizationRollbackCheck:
    check_id: str
    status: str
    findings: tuple[str, ...]
    required_refs_present: bool
    policy: str


@dataclass(frozen=True)
class AuthorizationScopeCheck:
    check_id: str
    status: str
    findings: tuple[str, ...]
    required_refs_present: bool
    policy: str


@dataclass(frozen=True)
class AuthorizationInvariantCheck:
    check_id: str
    status: str
    findings: tuple[str, ...]
    required_refs_present: bool
    policy: str


@dataclass(frozen=True)
class AuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class AuthorizationAuditClosure:
    schema_version: str
    closure_id: str
    authorization_id: str
    authorization_hash: str
    input_refs: tuple[AuthorizationAuditInputRef, ...]
    lineage_check: AuthorizationLineageCheck
    replay_guard_check: AuthorizationReplayGuardCheck
    rollback_check: AuthorizationRollbackCheck
    scope_check: AuthorizationScopeCheck
    invariant_check: AuthorizationInvariantCheck
    closure_status: str
    closure_summary: str
    created_by_lane: str
    authority_ref: AuthorityRef | None
    execution_allowed: bool
    mutation_allowed: bool
    routing_change_allowed: bool
    closure_hash: str


@dataclass(frozen=True)
class AuthorizationAuditValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class AuthorizationAuditValidationReport:
    status: str
    findings: tuple[AuthorizationAuditValidationFinding, ...]
    receipt_hash: str

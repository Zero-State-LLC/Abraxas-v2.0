from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import ExecutionAuthorizationScope, ExecutionAuthorityRef, ExecutionReplayGuard, ExecutionExpiryPolicy, ExecutionRollbackRequirement, AuthorityRef, ExecutionAuthorizationPacket, ExecutionAuthorizationValidationFinding, ExecutionAuthorizationValidationReport


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _to_packet(x: ExecutionAuthorizationPacket | Mapping[str, Any]) -> ExecutionAuthorizationPacket:
    if isinstance(x, ExecutionAuthorizationPacket):
        return x
    d = dict(x)
    return ExecutionAuthorizationPacket(d["schema_version"], d["authorization_id"], d["decision_packet_id"], d["decision_packet_hash"], d["proposal_id"], d["proposal_hash"], ExecutionAuthorizationScope(**d["scope"]), tuple(ExecutionAuthorityRef(**r) for r in d["authority_refs"]), ExecutionReplayGuard(**d["replay_guard"]), ExecutionExpiryPolicy(**d["expiry_policy"]), ExecutionRollbackRequirement(**d["rollback_requirement"]), d["authorization_status"], d["created_by_lane"], AuthorityRef(**d["authority_ref"]) if d.get("authority_ref") else None, d["execution_authorized"], d["mutation_allowed"], d["routing_change_allowed"], d["authorization_hash"])


def validate_execution_authorization_packet(packet: ExecutionAuthorizationPacket | Mapping[str, Any]) -> ExecutionAuthorizationValidationReport:
    p = _to_packet(packet)
    findings=[]
    status="PASS"
    if p.schema_version!="ExecutionAuthorizationPacket.v1":
        findings.append(ExecutionAuthorizationValidationFinding("SCHEMA_VERSION_INVALID","not_computable","schema_version must be ExecutionAuthorizationPacket.v1."))
        status="NOT_COMPUTABLE"
    if not p.decision_packet_id or not p.decision_packet_hash or not p.proposal_id or not p.proposal_hash:
        findings.append(ExecutionAuthorizationValidationFinding("REFS_REQUIRED","not_computable","Missing decision/proposal refs or hashes."))
        status="NOT_COMPUTABLE" if status!="BLOCKED" else status
    if p.execution_authorized:
        findings.append(ExecutionAuthorizationValidationFinding("EXECUTION_FORBIDDEN","error","execution_authorized must be false."))
        status="BLOCKED"
    if p.mutation_allowed:
        findings.append(ExecutionAuthorizationValidationFinding("MUTATION_FORBIDDEN","error","mutation_allowed must be false."))
        status="BLOCKED"
    if p.routing_change_allowed:
        findings.append(ExecutionAuthorizationValidationFinding("ROUTING_CHANGE_FORBIDDEN","error","routing_change_allowed must be false."))
        status="BLOCKED"
    if p.replay_guard.single_use_policy is not True:
        findings.append(ExecutionAuthorizationValidationFinding("SINGLE_USE_REQUIRED","error","single_use_policy must be true."))
        status="BLOCKED"
    if p.replay_guard.replay_policy != "REPLAY_BLOCKED_WITHOUT_OPERATOR_REVIEW":
        findings.append(ExecutionAuthorizationValidationFinding("REPLAY_POLICY_INVALID","error","replay_policy invalid."))
        status="BLOCKED"
    if p.expiry_policy.expired_behavior != "BLOCK_EXECUTION":
        findings.append(ExecutionAuthorizationValidationFinding("EXPIRED_BEHAVIOR_INVALID","error","expired_behavior must be BLOCK_EXECUTION."))
        status="BLOCKED"
    if not p.rollback_requirement.rollback_required:
        findings.append(ExecutionAuthorizationValidationFinding("ROLLBACK_REQUIRED","error","rollback_required must be true."))
        status="BLOCKED"
    if not p.rollback_requirement.rollback_verification_required:
        findings.append(ExecutionAuthorizationValidationFinding("ROLLBACK_VERIFY_REQUIRED","error","rollback_verification_required must be true."))
        status="BLOCKED"
    if p.scope.scope_type == "GLOBAL":
        findings.append(ExecutionAuthorizationValidationFinding("GLOBAL_SCOPE_FORBIDDEN","error","scope must not be GLOBAL."))
        status="BLOCKED"
    if p.authorization_status=="AUTHORIZED_FOR_FUTURE_EXECUTION" and (not p.authority_refs or not p.rollback_requirement.rollback_plan_ref):
        findings.append(ExecutionAuthorizationValidationFinding("AUTHORIZED_CONTENT_REQUIRED","not_computable","Authorized status requires refs/policies/rollback."))
        status="NOT_COMPUTABLE" if status!="BLOCKED" else status
    if p.created_by_lane=="SHADOW" and p.authorization_status in {"READY_FOR_EXECUTION_REVIEW","AUTHORIZED_FOR_FUTURE_EXECUTION"}:
        findings.append(ExecutionAuthorizationValidationFinding("SHADOW_FINALIZE_BLOCKED","error","SHADOW may draft but cannot mark ready/authorized."))
        status="BLOCKED"
    if p.created_by_lane=="FORECAST" and p.authorization_status=="AUTHORIZED_FOR_FUTURE_EXECUTION":
        findings.append(ExecutionAuthorizationValidationFinding("FORECAST_AUTH_BLOCKED","error","FORECAST may submit ready but cannot authorize."))
        status="BLOCKED"
    if p.created_by_lane=="PROJECTION" and p.authority_ref is not None:
        findings.append(ExecutionAuthorizationValidationFinding("PROJECTION_AUTHORITY_BLOCKED","error","PROJECTION cannot create execution authority."))
        status="BLOCKED"
    if p.created_by_lane=="CANON" and p.authorization_status in {"READY_FOR_EXECUTION_REVIEW","AUTHORIZED_FOR_FUTURE_EXECUTION","DENIED","HELD"}:
        findings.append(ExecutionAuthorizationValidationFinding("CANON_FINALIZE_BLOCKED","error","CANON may define schema/contracts only."))
        status="BLOCKED"
    receipt_hash=_sha256_text(_canonical_json({"status":status,"findings":[asdict(f) for f in findings],"authorization_id":p.authorization_id}))
    return ExecutionAuthorizationValidationReport(status, tuple(findings), receipt_hash)

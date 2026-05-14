from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import AuthorizationAuditInputRef, AuthorizationLineageCheck, AuthorizationReplayGuardCheck, AuthorizationRollbackCheck, AuthorizationScopeCheck, AuthorizationInvariantCheck, AuthorityRef, AuthorizationAuditClosure, AuthorizationAuditValidationFinding, AuthorizationAuditValidationReport


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _to_closure(x: AuthorizationAuditClosure | Mapping[str, Any]) -> AuthorizationAuditClosure:
    if isinstance(x, AuthorizationAuditClosure):
        return x
    d = dict(x)
    return AuthorizationAuditClosure(d["schema_version"], d["closure_id"], d["authorization_id"], d["authorization_hash"], tuple(AuthorizationAuditInputRef(**r) for r in d["input_refs"]), AuthorizationLineageCheck(**d["lineage_check"]), AuthorizationReplayGuardCheck(**d["replay_guard_check"]), AuthorizationRollbackCheck(**d["rollback_check"]), AuthorizationScopeCheck(**d["scope_check"]), AuthorizationInvariantCheck(**d["invariant_check"]), d["closure_status"], d["closure_summary"], d["created_by_lane"], AuthorityRef(**d["authority_ref"]) if d.get("authority_ref") else None, d["execution_allowed"], d["mutation_allowed"], d["routing_change_allowed"], d["closure_hash"])


def validate_authorization_audit_closure(closure: AuthorizationAuditClosure | Mapping[str, Any]) -> AuthorizationAuditValidationReport:
    c=_to_closure(closure)
    findings=[]
    status="PASS"
    checks=[c.lineage_check,c.replay_guard_check,c.rollback_check,c.scope_check,c.invariant_check]
    sts=[x.status for x in checks]
    if c.schema_version!="AuthorizationAuditClosure.v1":
        findings.append(AuthorizationAuditValidationFinding("SCHEMA_VERSION_INVALID","not_computable","schema_version must be AuthorizationAuditClosure.v1."))
        status="NOT_COMPUTABLE"
    if c.execution_allowed or c.mutation_allowed or c.routing_change_allowed:
        findings.append(AuthorizationAuditValidationFinding("NON_EXECUTION_FLAGS_INVALID","error","execution/mutation/routing flags must be false."))
        status="BLOCKED"
    if c.closure_status=="PASS" and any(s!="PASS" for s in sts):
        findings.append(AuthorizationAuditValidationFinding("PASS_REQUIRES_ALL_PASS","error","PASS requires all checks PASS."))
        status="BLOCKED"
    if c.closure_status=="BLOCKED" and "BLOCKED" not in sts:
        findings.append(AuthorizationAuditValidationFinding("BLOCKED_REQUIRES_BLOCKED_CHECK","error","BLOCKED closure requires blocked check."))
        status="BLOCKED"
    if c.closure_status=="NOT_COMPUTABLE" and "NOT_COMPUTABLE" not in sts:
        findings.append(AuthorizationAuditValidationFinding("NC_REQUIRES_NC_CHECK","error","NOT_COMPUTABLE closure requires not-computable check."))
        status="BLOCKED"
    if c.closure_status=="WARN" and ("WARN" not in sts or "BLOCKED" in sts or "NOT_COMPUTABLE" in sts):
        findings.append(AuthorizationAuditValidationFinding("WARN_REQUIRES_WARN_ONLY","error","WARN requires warn check and no blocked/not-computable checks."))
        status="BLOCKED"
    if c.created_by_lane=="SHADOW" and c.closure_status=="PASS":
        findings.append(AuthorizationAuditValidationFinding("SHADOW_PASS_BLOCKED","error","SHADOW may draft but cannot mark PASS."))
        status="BLOCKED"
    if c.created_by_lane=="FORECAST" and c.closure_status=="PASS":
        findings.append(AuthorizationAuditValidationFinding("FORECAST_PASS_BLOCKED","error","FORECAST may submit diagnostics but cannot mark PASS."))
        status="BLOCKED"
    if c.created_by_lane=="OPERATOR" and c.closure_status=="PASS" and c.authority_ref is None:
        findings.append(AuthorizationAuditValidationFinding("OPERATOR_AUTHORITY_REQUIRED","not_computable","OPERATOR PASS requires authority_ref."))
        status="NOT_COMPUTABLE" if status!="BLOCKED" else status
    if c.created_by_lane=="PROJECTION" and c.authority_ref is not None:
        findings.append(AuthorizationAuditValidationFinding("PROJECTION_AUTHORITY_BLOCKED","error","PROJECTION cannot create audit closure authority."))
        status="BLOCKED"
    if c.created_by_lane=="CANON" and c.closure_status in {"PASS","WARN","BLOCKED"}:
        findings.append(AuthorizationAuditValidationFinding("CANON_FINALIZE_BLOCKED","error","CANON may define schema/contracts only."))
        status="BLOCKED"
    receipt_hash=_sha256_text(_canonical_json({"status":status,"findings":[asdict(f) for f in findings],"closure_id":c.closure_id}))
    return AuthorizationAuditValidationReport(status, tuple(findings), receipt_hash)

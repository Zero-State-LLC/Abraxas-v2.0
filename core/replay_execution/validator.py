from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import ReplayInputRef, ReplayMutationPlan, ReplayRollbackPlan, ReplayExecutionReceipt, ReplayDeterminismReport, AuthorityRef, ReplayExecutionEnvelope, ReplayValidationFinding, ReplayValidationReport


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _to_env(x: ReplayExecutionEnvelope | Mapping[str, Any]) -> ReplayExecutionEnvelope:
    if isinstance(x, ReplayExecutionEnvelope):
        return x
    d=dict(x)
    return ReplayExecutionEnvelope(d["schema_version"],d["replay_id"],d["authorization_id"],d["authorization_hash"],d["authorization_audit_closure_id"],d["authorization_audit_closure_hash"],tuple(ReplayInputRef(**r) for r in d["input_refs"]),ReplayMutationPlan(**d["mutation_plan"]),ReplayRollbackPlan(**d["rollback_plan"]),ReplayExecutionReceipt(**d["execution_receipt"]),ReplayDeterminismReport(**d["determinism_report"]),d["replay_status"],d["created_by_lane"],AuthorityRef(**d["authority_ref"]) if d.get("authority_ref") else None,d["live_execution_allowed"],d["mutation_allowed"],d["routing_change_allowed"],d["adapter_activation_allowed"],d["replay_hash"])


def validate_replay_execution_envelope(envelope: ReplayExecutionEnvelope | Mapping[str, Any]) -> ReplayValidationReport:
    e=_to_env(envelope)
    findings=[]
    status="PASS"
    if e.schema_version!="ReplayExecutionEnvelope.v1":
        findings.append(ReplayValidationFinding("SCHEMA_VERSION_INVALID","not_computable","schema_version must be ReplayExecutionEnvelope.v1."))
        status="NOT_COMPUTABLE"
    if not e.authorization_id or not e.authorization_hash or not e.authorization_audit_closure_id or not e.authorization_audit_closure_hash:
        findings.append(ReplayValidationFinding("AUTH_REFS_REQUIRED","not_computable","Missing authorization/closure refs."))
        status="NOT_COMPUTABLE" if status!="BLOCKED" else status
    if e.live_execution_allowed:
        findings.append(ReplayValidationFinding("LIVE_EXEC_FORBIDDEN","error","live_execution_allowed must be false."))
        status="BLOCKED"
    if e.mutation_allowed:
        findings.append(ReplayValidationFinding("MUTATION_FORBIDDEN","error","mutation_allowed must be false."))
        status="BLOCKED"
    if e.routing_change_allowed:
        findings.append(ReplayValidationFinding("ROUTING_FORBIDDEN","error","routing_change_allowed must be false."))
        status="BLOCKED"
    if e.adapter_activation_allowed:
        findings.append(ReplayValidationFinding("ADAPTER_FORBIDDEN","error","adapter_activation_allowed must be false."))
        status="BLOCKED"
    if e.mutation_plan.live_apply_allowed:
        findings.append(ReplayValidationFinding("LIVE_APPLY_FORBIDDEN","error","mutation_plan.live_apply_allowed must be false."))
        status="BLOCKED"
    if e.execution_receipt.live_side_effects_detected:
        findings.append(ReplayValidationFinding("LIVE_SIDE_EFFECTS_FORBIDDEN","error","live_side_effects_detected must be false."))
        status="BLOCKED"
    if e.replay_status=="REPLAY_READY" and (not e.input_refs or not e.rollback_plan.rollback_plan_id):
        findings.append(ReplayValidationFinding("REPLAY_READY_CONTENT_REQUIRED","not_computable","REPLAY_READY requires refs/plans/reports."))
        status="NOT_COMPUTABLE" if status!="BLOCKED" else status
    if e.replay_status=="REPLAY_PASSED" and (not e.determinism_report.all_runs_identical or e.determinism_report.nondeterminism_detected or not e.rollback_plan.rollback_verified_in_replay or e.execution_receipt.live_side_effects_detected):
        findings.append(ReplayValidationFinding("REPLAY_PASSED_CONDITIONS_INVALID","error","REPLAY_PASSED requires deterministic identical runs, rollback verified, no side effects."))
        status="BLOCKED"
    if e.replay_status=="BLOCKED_BY_ROLLBACK" and e.rollback_plan.rollback_available and e.rollback_plan.rollback_verified_in_replay:
        findings.append(ReplayValidationFinding("ROLLBACK_BLOCK_CONDITION_INVALID","error","BLOCKED_BY_ROLLBACK requires rollback unavailable or unverified."))
        status="BLOCKED"
    if e.replay_status=="BLOCKED_BY_NONDETERMINISM" and not e.determinism_report.nondeterminism_detected:
        findings.append(ReplayValidationFinding("NONDETERMINISM_BLOCK_CONDITION_INVALID","error","BLOCKED_BY_NONDETERMINISM requires nondeterminism_detected=true."))
        status="BLOCKED"
    if e.created_by_lane=="SHADOW" and e.replay_status=="REPLAY_PASSED":
        findings.append(ReplayValidationFinding("SHADOW_PASS_BLOCKED","error","SHADOW may draft but cannot mark REPLAY_PASSED."))
        status="BLOCKED"
    if e.created_by_lane=="FORECAST" and e.replay_status=="REPLAY_PASSED":
        findings.append(ReplayValidationFinding("FORECAST_PASS_BLOCKED","error","FORECAST may submit diagnostics but cannot mark REPLAY_PASSED."))
        status="BLOCKED"
    if e.created_by_lane=="PROJECTION" and e.authority_ref is not None:
        findings.append(ReplayValidationFinding("PROJECTION_AUTHORITY_BLOCKED","error","PROJECTION cannot create replay authority."))
        status="BLOCKED"
    if e.created_by_lane=="CANON" and e.replay_status in {"REPLAY_READY","REPLAY_PASSED","REPLAY_FAILED","BLOCKED_BY_AUTHORIZATION","BLOCKED_BY_ROLLBACK","BLOCKED_BY_NONDETERMINISM"}:
        findings.append(ReplayValidationFinding("CANON_FINALIZE_BLOCKED","error","CANON may define schema/contracts only."))
        status="BLOCKED"
    receipt_hash=_sha256_text(_canonical_json({"status":status,"findings":[asdict(f) for f in findings],"replay_id":e.replay_id}))
    return ReplayValidationReport(status, tuple(findings), receipt_hash)

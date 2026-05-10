from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import *

SCHEMA_VERSION = "AuthorizationAuditClosure.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_authorization_audit_closure_json(closure: AuthorizationAuditClosure | Mapping[str, Any]) -> str:
    payload = asdict(closure) if isinstance(closure, AuthorizationAuditClosure) else dict(closure)
    payload.pop("closure_hash", None)
    return _canonical_json(payload)


def authorization_audit_closure_hash(closure: AuthorizationAuditClosure | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_authorization_audit_closure_json(closure))


def _rollup_status(statuses: list[str]) -> str:
    if "BLOCKED" in statuses:
        return "BLOCKED"
    if "NOT_COMPUTABLE" in statuses:
        return "NOT_COMPUTABLE"
    if "WARN" in statuses:
        return "WARN"
    return "PASS"


def build_authorization_audit_closure(
    closure_id: str,
    authorization_id: str,
    authorization_hash: str,
    input_refs: tuple[AuthorizationAuditInputRef, ...],
    lineage_check: AuthorizationLineageCheck,
    replay_guard_check: AuthorizationReplayGuardCheck,
    rollback_check: AuthorizationRollbackCheck,
    scope_check: AuthorizationScopeCheck,
    invariant_check: AuthorizationInvariantCheck,
    closure_status: str,
    closure_summary: str,
    created_by_lane: str,
    authority_ref: AuthorityRef | None,
) -> AuthorizationAuditClosure:
    draft = AuthorizationAuditClosure(SCHEMA_VERSION, closure_id, authorization_id, authorization_hash, input_refs, lineage_check, replay_guard_check, rollback_check, scope_check, invariant_check, closure_status, closure_summary, created_by_lane, authority_ref, False, False, False, "PENDING")
    return replace(draft, closure_hash=authorization_audit_closure_hash(draft))


def derive_authorization_audit_closure_from_packet(packet: Mapping[str, Any]) -> AuthorizationAuditClosure:
    p = dict(packet)
    auth_status = str(p.get("authorization_status", "NOT_COMPUTABLE"))
    findings_lineage=[]
    req_lineage = bool(p.get("decision_packet_id") and p.get("decision_packet_hash") and p.get("proposal_id") and p.get("proposal_hash"))
    if not req_lineage:
        findings_lineage.append("Missing decision/proposal refs.")
    if auth_status == "AUTHORIZED_FOR_FUTURE_EXECUTION" and not p.get("authority_refs"):
        findings_lineage.append("Future authorization missing authority refs.")
    lineage_status = "PASS" if req_lineage and not findings_lineage else ("BLOCKED" if findings_lineage else "NOT_COMPUTABLE")

    rg = dict(p.get("replay_guard", {}))
    replay_find=[]
    replay_req = bool(rg.get("idempotency_key")) and bool(rg.get("input_hashes"))
    if rg.get("single_use_policy") is not True: replay_find.append("single_use_policy must be true.")
    if rg.get("replay_policy") != "REPLAY_BLOCKED_WITHOUT_OPERATOR_REVIEW": replay_find.append("replay_policy invalid.")
    if not rg.get("idempotency_key"): replay_find.append("idempotency_key missing.")
    if not rg.get("input_hashes"): replay_find.append("input_hashes missing.")
    replay_status = "PASS" if not replay_find else ("BLOCKED" if replay_req else "NOT_COMPUTABLE")

    rb = dict(p.get("rollback_requirement", {}))
    rb_find=[]
    rb_req = bool(rb.get("rollback_plan_ref"))
    if rb.get("rollback_required") is not True: rb_find.append("rollback_required must be true.")
    if rb.get("rollback_verification_required") is not True: rb_find.append("rollback_verification_required must be true.")
    if not rb.get("rollback_plan_ref"): rb_find.append("rollback_plan_ref missing.")
    if auth_status == "AUTHORIZED_FOR_FUTURE_EXECUTION" and not rb.get("rollback_artifact_refs"): rb_find.append("rollback_artifact_refs required for future authorization.")
    rollback_status = "PASS" if not rb_find else ("BLOCKED" if rb_req else "NOT_COMPUTABLE")

    sc = dict(p.get("scope", {})); scope_find=[]
    allowed = {"DOMAIN", "SOURCE", "SUBSYSTEM", "MODEL_FAMILY", "RUNTIME_ROUTE", "FIXTURE_ONLY", "NOT_COMPUTABLE"}
    if not sc: scope_find.append("scope missing.")
    if sc.get("scope_type") == "GLOBAL": scope_find.append("GLOBAL scope blocked.")
    if sc.get("scope_type") and sc.get("scope_type") not in allowed: scope_find.append("scope type invalid.")
    scope_status = "PASS" if not scope_find else ("BLOCKED" if "GLOBAL scope blocked." in scope_find else "NOT_COMPUTABLE")

    inv_find=[]
    if p.get("execution_authorized") is not False: inv_find.append("execution_authorized must be false.")
    if p.get("mutation_allowed") is not False: inv_find.append("mutation_allowed must be false.")
    if p.get("routing_change_allowed") is not False: inv_find.append("routing_change_allowed must be false.")
    if p.get("adapter_activation_allowed") is True: inv_find.append("adapter activation forbidden.")
    inv_status = "PASS" if not inv_find else "BLOCKED"

    statuses=[lineage_status,replay_status,rollback_status,scope_status,inv_status]
    closure_status=_rollup_status(statuses)
    return build_authorization_audit_closure(
        closure_id=f"auth-closure:{p.get('authorization_id','unknown')}",
        authorization_id=str(p.get("authorization_id", "")),
        authorization_hash=str(p.get("authorization_hash", "")),
        input_refs=(AuthorizationAuditInputRef("EXECUTION_AUTHORIZATION_PACKET", str(p.get("authorization_id", "")), str(p.get("authorization_hash", ""))),),
        lineage_check=AuthorizationLineageCheck("lineage", lineage_status, tuple(findings_lineage), req_lineage, "LINEAGE_REQUIRED_V1"),
        replay_guard_check=AuthorizationReplayGuardCheck("replay", replay_status, tuple(replay_find), replay_req, "REPLAY_GUARD_REQUIRED_V1"),
        rollback_check=AuthorizationRollbackCheck("rollback", rollback_status, tuple(rb_find), rb_req, "ROLLBACK_REQUIRED_V1"),
        scope_check=AuthorizationScopeCheck("scope", scope_status, tuple(scope_find), bool(sc), "NON_GLOBAL_SCOPE_V1"),
        invariant_check=AuthorizationInvariantCheck("invariants", inv_status, tuple(inv_find), True, "NON_EXECUTION_INVARIANTS_V1"),
        closure_status=closure_status,
        closure_summary=f"Derived closure status {closure_status} from authorization packet status {auth_status}.",
        created_by_lane="FORECAST",
        authority_ref=None,
    )


def write_authorization_audit_closure_contract_audit(base_dir: Path | str = ".") -> str:
    packet = {
        "authorization_id": "auth-1", "authorization_hash": "ah1", "decision_packet_id": "dp-1", "decision_packet_hash": "dph1", "proposal_id": "proposal-1", "proposal_hash": "ph1", "authorization_status": "BLOCKED",
        "scope": {"scope_type": "SUBSYSTEM", "scope_id": "forecast-runtime"},
        "authority_refs": [{"source_type": "PROMOTION_DECISION_PACKET", "source_id": "dp-1", "source_hash": "dph1"}],
        "replay_guard": {"idempotency_key": "idem-1", "input_hashes": ["dph1"], "single_use_policy": True, "replay_policy": "REPLAY_BLOCKED_WITHOUT_OPERATOR_REVIEW"},
        "expiry_policy": {"expired_behavior": "BLOCK_EXECUTION"},
        "rollback_requirement": {"rollback_required": True, "rollback_verification_required": True, "rollback_plan_ref": "rb1", "rollback_artifact_refs": ["runtime/forecast"]},
        "execution_authorized": False, "mutation_allowed": False, "routing_change_allowed": False,
    }
    closure = derive_authorization_audit_closure_from_packet(packet)
    from .validator import validate_authorization_audit_closure
    report = validate_authorization_audit_closure(closure)
    payload = {"status": report.status, "closure_hash": closure.closure_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": closure.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/authorization_audit_closure.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)

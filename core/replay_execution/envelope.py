from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import *

SCHEMA_VERSION = "ReplayExecutionEnvelope.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_replay_execution_envelope_json(envelope: ReplayExecutionEnvelope | Mapping[str, Any]) -> str:
    payload = asdict(envelope) if isinstance(envelope, ReplayExecutionEnvelope) else dict(envelope)
    payload.pop("replay_hash", None)
    return _canonical_json(payload)


def replay_execution_envelope_hash(envelope: ReplayExecutionEnvelope | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_replay_execution_envelope_json(envelope))


def replay_execution_receipt_hash(receipt: ReplayExecutionReceipt | Mapping[str, Any]) -> str:
    payload = asdict(receipt) if isinstance(receipt, ReplayExecutionReceipt) else dict(receipt)
    payload.pop("receipt_hash", None)
    return _sha256_text(_canonical_json(payload))


def build_replay_execution_envelope(
    replay_id: str,
    authorization_id: str,
    authorization_hash: str,
    authorization_audit_closure_id: str,
    authorization_audit_closure_hash: str,
    input_refs: tuple[ReplayInputRef, ...],
    mutation_plan: ReplayMutationPlan,
    rollback_plan: ReplayRollbackPlan,
    execution_receipt: ReplayExecutionReceipt,
    determinism_report: ReplayDeterminismReport,
    replay_status: str,
    created_by_lane: str,
    authority_ref: AuthorityRef | None,
) -> ReplayExecutionEnvelope:
    draft = ReplayExecutionEnvelope(SCHEMA_VERSION, replay_id, authorization_id, authorization_hash, authorization_audit_closure_id, authorization_audit_closure_hash, input_refs, mutation_plan, rollback_plan, execution_receipt, determinism_report, replay_status, created_by_lane, authority_ref, False, False, False, False, "PENDING")
    return replace(draft, replay_hash=replay_execution_envelope_hash(draft))


def derive_replay_execution_envelope_from_authorization(authorization_packet: Mapping[str, Any], authorization_closure: Mapping[str, Any]) -> ReplayExecutionEnvelope:
    ap = dict(authorization_packet); ac = dict(authorization_closure)
    closure_status = str(ac.get("closure_status", "NOT_COMPUTABLE"))
    replay_status = "NOT_COMPUTABLE"
    rollback_available = bool(ap.get("rollback_requirement", {}).get("rollback_available", True))
    rollback_verified = True
    nondeterministic = False
    if closure_status == "BLOCKED":
        replay_status = "BLOCKED_BY_AUTHORIZATION"
    elif closure_status == "NOT_COMPUTABLE":
        replay_status = "NOT_COMPUTABLE"
    elif closure_status in {"PASS", "WARN"} and rollback_available:
        replay_status = "REPLAY_READY"
    if nondeterministic:
        replay_status = "BLOCKED_BY_NONDETERMINISM"
    if (not rollback_available) or (not rollback_verified):
        replay_status = "BLOCKED_BY_ROLLBACK"

    receipt = ReplayExecutionReceipt("receipt-1", "SANDBOX_REPLAY_ONLY", ("op-hash-1",), False, "PENDING")
    receipt = replace(receipt, receipt_hash=replay_execution_receipt_hash(receipt))
    return build_replay_execution_envelope(
        replay_id=f"replay:{ap.get('authorization_id', 'unknown')}",
        authorization_id=str(ap.get("authorization_id", "")),
        authorization_hash=str(ap.get("authorization_hash", "")),
        authorization_audit_closure_id=str(ac.get("closure_id", "")),
        authorization_audit_closure_hash=str(ac.get("closure_hash", "")),
        input_refs=(ReplayInputRef("EXECUTION_AUTHORIZATION_PACKET", str(ap.get("authorization_id", "")), str(ap.get("authorization_hash", ""))), ReplayInputRef("AUTHORIZATION_AUDIT_CLOSURE", str(ac.get("closure_id", "")), str(ac.get("closure_hash", "")))),
        mutation_plan=ReplayMutationPlan("mp-1", "SUBSYSTEM", ("runtime/forecast",), ("simulate_canary_apply",), 1, False),
        rollback_plan=ReplayRollbackPlan("rb-1", rollback_available, ("simulate_rollback",), 1, "ROLLBACK_VERIFY_REPLAY_V1", rollback_verified),
        execution_receipt=receipt,
        determinism_report=ReplayDeterminismReport("det-1", 2, True, ("out-hash-1", "out-hash-1"), nondeterministic, "IDENTICAL_OUTPUT_HASH_V1"),
        replay_status=replay_status,
        created_by_lane="FORECAST",
        authority_ref=None,
    )


def write_replay_execution_envelope_contract_audit(base_dir: Path | str = ".") -> str:
    ap = {"authorization_id": "auth-1", "authorization_hash": "ah1", "rollback_requirement": {"rollback_available": True}}
    ac = {"closure_id": "closure-1", "closure_hash": "ch1", "closure_status": "BLOCKED"}
    env = derive_replay_execution_envelope_from_authorization(ap, ac)
    from .validator import validate_replay_execution_envelope
    report = validate_replay_execution_envelope(env)
    payload = {"status": report.status, "replay_hash": env.replay_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": env.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/replay_execution_envelope_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)

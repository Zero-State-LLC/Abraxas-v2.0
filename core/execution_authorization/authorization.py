from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import ExecutionAuthorizationScope, ExecutionAuthorityRef, ExecutionReplayGuard, ExecutionExpiryPolicy, ExecutionRollbackRequirement, AuthorityRef, ExecutionAuthorizationPacket

SCHEMA_VERSION = "ExecutionAuthorizationPacket.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_execution_authorization_packet_json(packet: ExecutionAuthorizationPacket | Mapping[str, Any]) -> str:
    payload = asdict(packet) if isinstance(packet, ExecutionAuthorizationPacket) else dict(packet)
    payload.pop("authorization_hash", None)
    return _canonical_json(payload)


def execution_authorization_packet_hash(packet: ExecutionAuthorizationPacket | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_execution_authorization_packet_json(packet))


def build_execution_authorization_packet(
    authorization_id: str,
    decision_packet_id: str,
    decision_packet_hash: str,
    proposal_id: str,
    proposal_hash: str,
    scope: ExecutionAuthorizationScope,
    authority_refs: tuple[ExecutionAuthorityRef, ...],
    replay_guard: ExecutionReplayGuard,
    expiry_policy: ExecutionExpiryPolicy,
    rollback_requirement: ExecutionRollbackRequirement,
    authorization_status: str,
    created_by_lane: str,
    authority_ref: AuthorityRef | None,
) -> ExecutionAuthorizationPacket:
    draft = ExecutionAuthorizationPacket(SCHEMA_VERSION, authorization_id, decision_packet_id, decision_packet_hash, proposal_id, proposal_hash, scope, authority_refs, replay_guard, expiry_policy, rollback_requirement, authorization_status, created_by_lane, authority_ref, False, False, False, "PENDING")
    return replace(draft, authorization_hash=execution_authorization_packet_hash(draft))


def derive_execution_authorization_packet_from_decision(decision_packet: Mapping[str, Any], proposal: Mapping[str, Any] | None = None) -> ExecutionAuthorizationPacket:
    d = dict(decision_packet)
    p = dict(proposal or {})
    st = str(d.get("packet_status", "NOT_COMPUTABLE"))
    posture = str(d.get("decision_posture", {}).get("posture", "NOT_COMPUTABLE"))
    auth_status = "NOT_COMPUTABLE"
    if d.get("decision_packet_hash") and (p.get("proposal_hash") or d.get("proposal_hash")):
        if st == "OPERATOR_APPROVED_FOR_FUTURE_EXECUTION" and posture in {"PROMOTION_RECOMMENDED", "ROLLBACK_RECOMMENDED"}:
            auth_status = "AUTHORIZED_FOR_FUTURE_EXECUTION"
        elif st == "READY_FOR_OPERATOR_DECISION":
            auth_status = "READY_FOR_EXECUTION_REVIEW"
        elif st == "OPERATOR_DENIED":
            auth_status = "DENIED"

    return build_execution_authorization_packet(
        authorization_id=f"exec-auth:{d.get('decision_packet_id', 'unknown')}",
        decision_packet_id=str(d.get("decision_packet_id", "")),
        decision_packet_hash=str(d.get("decision_packet_hash", "")),
        proposal_id=str(p.get("proposal_id", d.get("proposal_id", ""))),
        proposal_hash=str(p.get("proposal_hash", d.get("proposal_hash", ""))),
        scope=ExecutionAuthorizationScope("SUBSYSTEM", "forecast-runtime"),
        authority_refs=(ExecutionAuthorityRef("PROMOTION_DECISION_PACKET", str(d.get("decision_packet_id", "")), str(d.get("decision_packet_hash", ""))),),
        replay_guard=ExecutionReplayGuard("replay-1", "idem-key-1", (str(d.get("decision_packet_hash", "")),), True, "REPLAY_BLOCKED_WITHOUT_OPERATOR_REVIEW"),
        expiry_policy=ExecutionExpiryPolicy("expiry-1", "WINDOW_COUNT", 1, "BLOCK_EXECUTION"),
        rollback_requirement=ExecutionRollbackRequirement(True, "rollback:1", ("runtime/forecast",), True),
        authorization_status=auth_status,
        created_by_lane="FORECAST",
        authority_ref=None,
    )


def write_execution_authorization_packet_contract_audit(base_dir: Path | str = ".") -> str:
    decision = {"decision_packet_id": "dp-1", "decision_packet_hash": "dph1", "proposal_id": "proposal-1", "proposal_hash": "ph1", "packet_status": "OPERATOR_APPROVED_FOR_FUTURE_EXECUTION", "decision_posture": {"posture": "PROMOTION_RECOMMENDED"}}
    packet = derive_execution_authorization_packet_from_decision(decision)
    from .validator import validate_execution_authorization_packet
    report = validate_execution_authorization_packet(packet)
    payload = {"status": report.status, "authorization_hash": packet.authorization_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": packet.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/execution_authorization_packet_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)

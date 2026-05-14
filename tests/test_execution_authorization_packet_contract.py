import hashlib
import json
from dataclasses import asdict, replace

from core.execution_authorization.authorization import canonical_execution_authorization_packet_json, derive_execution_authorization_packet_from_decision, execution_authorization_packet_hash, write_execution_authorization_packet_contract_audit
from core.execution_authorization.models import AuthorityRef
from core.execution_authorization.validator import validate_execution_authorization_packet


def _decision(status="OPERATOR_APPROVED_FOR_FUTURE_EXECUTION", posture="PROMOTION_RECOMMENDED"):
    return {"decision_packet_id": "dp-1", "decision_packet_hash": "dph1", "proposal_id": "proposal-1", "proposal_hash": "ph1", "packet_status": status, "decision_posture": {"posture": posture}}


def test_derivation_statuses_and_non_execution():
    a = derive_execution_authorization_packet_from_decision(_decision())
    assert a.authorization_status == "AUTHORIZED_FOR_FUTURE_EXECUTION" and (not a.execution_authorized)
    r = derive_execution_authorization_packet_from_decision(_decision("READY_FOR_OPERATOR_DECISION", "HOLD_RECOMMENDED"))
    assert r.authorization_status == "READY_FOR_EXECUTION_REVIEW"
    d = derive_execution_authorization_packet_from_decision(_decision("OPERATOR_DENIED", "DENIAL_RECOMMENDED"))
    assert d.authorization_status == "DENIED"


def test_missing_refs_and_flag_constraints():
    a = derive_execution_authorization_packet_from_decision(_decision())
    assert validate_execution_authorization_packet(replace(a, proposal_id="")).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_execution_authorization_packet(replace(a, execution_authorized=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_execution_authorization_packet(replace(a, mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_execution_authorization_packet(replace(a, routing_change_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_execution_authorization_packet(replace(a, replay_guard=replace(a.replay_guard, single_use_policy=False))).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_execution_authorization_packet(replace(a, replay_guard=replace(a.replay_guard, replay_policy="ALLOW_REPLAY"))).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_execution_authorization_packet(replace(a, expiry_policy=replace(a.expiry_policy, expired_behavior="ALLOW_EXECUTION"))).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_execution_authorization_packet(replace(a, rollback_requirement=replace(a.rollback_requirement, rollback_required=False))).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_execution_authorization_packet(replace(a, rollback_requirement=replace(a.rollback_requirement, rollback_verification_required=False))).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_lane_constraints_and_hash_schema_audit(tmp_path):
    a = derive_execution_authorization_packet_from_decision(_decision())
    sh = replace(a, created_by_lane="SHADOW")
    assert validate_execution_authorization_packet(sh).status in {"BLOCKED", "NOT_COMPUTABLE"}
    fc = replace(a, created_by_lane="FORECAST")
    assert validate_execution_authorization_packet(fc).status in {"BLOCKED", "NOT_COMPUTABLE"}
    proj = replace(a, created_by_lane="PROJECTION", authority_ref=AuthorityRef("MANUAL_RECEIPT", "id", "label"))
    assert validate_execution_authorization_packet(proj).status in {"BLOCKED", "NOT_COMPUTABLE"}

    alt = dict(asdict(a))
    alt["authorization_hash"] = "other"
    assert execution_authorization_packet_hash(a) == execution_authorization_packet_hash(alt)
    assert canonical_execution_authorization_packet_json(a) == canonical_execution_authorization_packet_json(a)

    schema = json.loads(open("contracts/execution_authorization/execution_authorization_packet.v1.schema.json", encoding="utf-8").read())
    req = set(schema["required"])
    obj = asdict(a)
    assert req.issubset(set(obj.keys()))
    bad = dict(obj)
    bad.pop("authorization_id")
    assert not req.issubset(set(bad.keys()))

    h = write_execution_authorization_packet_contract_audit(tmp_path)
    p = tmp_path / "out/audit/execution_authorization_packet_contract.latest.json"
    text = p.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert h == hashlib.sha256(text.encode("utf-8")).hexdigest()

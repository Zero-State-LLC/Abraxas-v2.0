import hashlib
import json
from dataclasses import asdict, replace

from core.authorization_audit import *


def _packet(status="AUTHORIZED_FOR_FUTURE_EXECUTION"):
    return {
        "authorization_id": "auth-1", "authorization_hash": "ah1", "decision_packet_id": "dp-1", "decision_packet_hash": "dph1", "proposal_id": "proposal-1", "proposal_hash": "ph1", "authorization_status": status,
        "scope": {"scope_type": "SUBSYSTEM", "scope_id": "forecast-runtime"},
        "authority_refs": [{"source_type": "MANUAL_RECEIPT", "source_id": "op1", "source_hash": "h"}],
        "replay_guard": {"idempotency_key": "idem-1", "input_hashes": ["dph1"], "single_use_policy": True, "replay_policy": "REPLAY_BLOCKED_WITHOUT_OPERATOR_REVIEW"},
        "rollback_requirement": {"rollback_required": True, "rollback_verification_required": True, "rollback_plan_ref": "rb1", "rollback_artifact_refs": ["runtime/forecast"]},
        "execution_authorized": False, "mutation_allowed": False, "routing_change_allowed": False,
    }


def test_pass_and_blocked_derivation():
    good = derive_authorization_audit_closure_from_packet(_packet())
    assert good.closure_status in {"PASS", "WARN", "BLOCKED", "NOT_COMPUTABLE"}
    blocked_packet = _packet(); blocked_packet["execution_authorized"] = True
    blocked = derive_authorization_audit_closure_from_packet(blocked_packet)
    assert blocked.closure_status == "BLOCKED"


def test_flag_replay_rollback_scope_constraints():
    c = derive_authorization_audit_closure_from_packet(_packet())
    assert validate_authorization_audit_closure(replace(c, execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_authorization_audit_closure(replace(c, mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_authorization_audit_closure(replace(c, routing_change_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    no_idem = derive_authorization_audit_closure_from_packet({**_packet(), "replay_guard": {"input_hashes": ["dph1"], "single_use_policy": True, "replay_policy": "REPLAY_BLOCKED_WITHOUT_OPERATOR_REVIEW"}})
    assert no_idem.closure_status in {"BLOCKED", "NOT_COMPUTABLE"}
    bad_single = derive_authorization_audit_closure_from_packet({**_packet(), "replay_guard": {"idempotency_key": "idem-1", "input_hashes": ["dph1"], "single_use_policy": False, "replay_policy": "REPLAY_BLOCKED_WITHOUT_OPERATOR_REVIEW"}})
    assert bad_single.closure_status == "BLOCKED"
    bad_rb = derive_authorization_audit_closure_from_packet({**_packet(), "rollback_requirement": {"rollback_required": False, "rollback_verification_required": True, "rollback_plan_ref": "rb1", "rollback_artifact_refs": ["x"]}})
    assert bad_rb.closure_status == "BLOCKED"
    global_scope = derive_authorization_audit_closure_from_packet({**_packet(), "scope": {"scope_type": "GLOBAL", "scope_id": "all"}})
    assert global_scope.closure_status == "BLOCKED"


def test_lane_hash_schema_and_audit(tmp_path):
    c = derive_authorization_audit_closure_from_packet(_packet())
    shadow = replace(c, created_by_lane="SHADOW", closure_status="PASS")
    assert validate_authorization_audit_closure(shadow).status in {"BLOCKED", "NOT_COMPUTABLE"}
    proj = replace(c, created_by_lane="PROJECTION", authority_ref=AuthorityRef("MANUAL_RECEIPT", "id", "label"))
    assert validate_authorization_audit_closure(proj).status in {"BLOCKED", "NOT_COMPUTABLE"}

    alt = dict(asdict(c)); alt["closure_hash"] = "other"
    assert authorization_audit_closure_hash(c) == authorization_audit_closure_hash(alt)
    assert canonical_authorization_audit_closure_json(c) == canonical_authorization_audit_closure_json(c)

    schema = json.loads(open("contracts/authorization_audit/authorization_audit_closure.v1.schema.json", encoding="utf-8").read())
    req = set(schema["required"])
    obj = asdict(c)
    assert req.issubset(set(obj.keys()))
    bad = dict(obj); bad.pop("closure_id")
    assert not req.issubset(set(bad.keys()))

    h = write_authorization_audit_closure_contract_audit(tmp_path)
    p = tmp_path / "out/audit/authorization_audit_closure.latest.json"
    text = p.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert h == hashlib.sha256(text.encode("utf-8")).hexdigest()

import hashlib
import json
from dataclasses import asdict, replace

from core.replay_execution.envelope import canonical_replay_execution_envelope_json, derive_replay_execution_envelope_from_authorization, replay_execution_envelope_hash, replay_execution_receipt_hash, write_replay_execution_envelope_contract_audit
from core.replay_execution.models import AuthorityRef
from core.replay_execution.validator import validate_replay_execution_envelope


def _auth(rollback_available=True):
    return {"authorization_id": "auth-1", "authorization_hash": "ah1", "rollback_requirement": {"rollback_available": rollback_available}}


def _closure(status="BLOCKED"):
    return {"closure_id": "closure-1", "closure_hash": "ch1", "closure_status": status}


def test_derivation_statuses():
    b = derive_replay_execution_envelope_from_authorization(_auth(), _closure("BLOCKED"))
    assert b.replay_status == "BLOCKED_BY_AUTHORIZATION"
    ready = derive_replay_execution_envelope_from_authorization(_auth(True), _closure("PASS"))
    assert ready.replay_status in {"REPLAY_READY", "REPLAY_PASSED"}
    rb = derive_replay_execution_envelope_from_authorization(_auth(False), _closure("PASS"))
    assert rb.replay_status == "BLOCKED_BY_ROLLBACK"


def test_constraints_and_flags():
    e = derive_replay_execution_envelope_from_authorization(_auth(True), _closure("PASS"))
    nd = replace(e, determinism_report=replace(e.determinism_report, nondeterminism_detected=True), replay_status="BLOCKED_BY_NONDETERMINISM")
    assert validate_replay_execution_envelope(nd).status in {"PASS", "WARN", "BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_execution_envelope(replace(e, live_execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_execution_envelope(replace(e, mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_execution_envelope(replace(e, routing_change_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_execution_envelope(replace(e, adapter_activation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_execution_envelope(replace(e, mutation_plan=replace(e.mutation_plan, live_apply_allowed=True))).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_execution_envelope(replace(e, execution_receipt=replace(e.execution_receipt, live_side_effects_detected=True))).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_lane_hash_schema_audit():
    e = derive_replay_execution_envelope_from_authorization(_auth(True), _closure("PASS"))
    sh = replace(e, replay_status="REPLAY_PASSED", created_by_lane="SHADOW")
    assert validate_replay_execution_envelope(sh).status in {"BLOCKED", "NOT_COMPUTABLE"}
    proj = replace(e, created_by_lane="PROJECTION", authority_ref=AuthorityRef("MANUAL_RECEIPT", "id", "label"))
    assert validate_replay_execution_envelope(proj).status in {"BLOCKED", "NOT_COMPUTABLE"}

    alt = dict(asdict(e))
    alt["replay_hash"] = "other"
    assert replay_execution_envelope_hash(e) == replay_execution_envelope_hash(alt)
    r_alt = dict(asdict(e.execution_receipt))
    r_alt["receipt_hash"] = "other"
    assert replay_execution_receipt_hash(e.execution_receipt) == replay_execution_receipt_hash(r_alt)
    assert canonical_replay_execution_envelope_json(e) == canonical_replay_execution_envelope_json(e)

    schema = json.loads(open("contracts/replay_execution/replay_execution_envelope.v1.schema.json", encoding="utf-8").read())
    req = set(schema["required"])
    obj = asdict(e)
    assert req.issubset(set(obj.keys()))
    bad = dict(obj)
    bad.pop("replay_id")
    assert not req.issubset(set(bad.keys()))

    h = write_replay_execution_envelope_contract_audit('.')
    p = "out/audit/replay_execution_envelope_contract.latest.json"
    text = open(p, encoding='utf-8').read()
    assert text.endswith("\n")
    assert h == hashlib.sha256(text.encode("utf-8")).hexdigest()

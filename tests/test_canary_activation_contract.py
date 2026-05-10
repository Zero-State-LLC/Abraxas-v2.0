import hashlib
import json
from dataclasses import asdict, replace

from core.canary_activation import *


def _activation(status="READY_FOR_CANARY", lane="FORECAST", receipt_ref="receipt://operator/review/1", scope_type="SUBSYSTEM"):
    return build_canary_activation(
        activation_id="act-1",
        proposal_id="proposal-1",
        proposal_hash="proposal-hash-1",
        scope=CanaryScope(scope_type, "forecast-runtime"),
        duration_policy=CanaryDurationPolicy("dur-1", "ON_OPERATOR_START", "ON_WINDOW_LIMIT", 3, "EXPIRE_ON_WINDOW_LIMIT"),
        guardrails=(CanaryGuardrail("g1", "BRIER_DELTA", {"max_delta": 0.03}, "HALT_AND_REVIEW", True),),
        evidence_requirements=CanaryEvidenceRequirement(True, True, True, True, 3, 3),
        rollback_link=CanaryRollbackLink("rb-1", True, ("runtime/forecast",), "ROLLBACK_ON_BREACH"),
        operator_approval_ref=CanaryOperatorApprovalRef(receipt_ref, "queue://operator/review/1", "OPERATOR_RECEIPT_REQUIRED"),
        activation_status=status,
        created_by_lane=lane,
        authority_ref=AuthorityRef("MANUAL_RECEIPT", "receipt://operator/approval/1", "Operator approval") if lane == "OPERATOR" else None,
    )


def test_deterministic_ready_for_canary_passes():
    a1 = _activation()
    a2 = _activation()
    assert a1.activation_hash == a2.activation_hash
    assert validate_canary_activation(a1).status == "PASS"


def test_ready_for_canary_requires_operator_approval_ref():
    a = _activation(receipt_ref="")
    a_bad = replace(a, operator_approval_ref=CanaryOperatorApprovalRef("", "", "OPERATOR_RECEIPT_REQUIRED"))
    assert validate_canary_activation(a_bad).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_flag_constraints_blocked():
    a = _activation()
    assert validate_canary_activation(replace(a, global_activation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_canary_activation(replace(a, mutation_limited_to_scope=False)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_canary_activation(replace(a, auto_promote=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_canary_activation(replace(a, auto_rollback=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_canary_active_constraints():
    a = _activation(status="CANARY_ACTIVE", lane="OPERATOR", receipt_ref="")
    assert validate_canary_activation(a).status in {"BLOCKED", "NOT_COMPUTABLE"}
    no_rb = replace(a, rollback_link=replace(a.rollback_link, rollback_available=False), operator_approval_ref=CanaryOperatorApprovalRef("receipt://operator/review/1", "queue://operator/review/1", "OPERATOR_RECEIPT_REQUIRED"))
    assert validate_canary_activation(no_rb).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bad_scope = _activation(status="CANARY_ACTIVE", lane="OPERATOR", scope_type="GLOBAL")
    assert validate_canary_activation(bad_scope).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_canary_failed_requires_breach_reason():
    a = _activation(status="CANARY_FAILED")
    broken_guard = replace(a, guardrails=(replace(a.guardrails[0], breach_action="UNKNOWN"),))
    assert validate_canary_activation(broken_guard).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_lane_constraints():
    sh = _activation(status="READY_FOR_CANARY", lane="SHADOW")
    assert validate_canary_activation(sh).status in {"BLOCKED", "NOT_COMPUTABLE"}
    fc = _activation(status="CANARY_ACTIVE", lane="FORECAST")
    assert validate_canary_activation(fc).status in {"BLOCKED", "NOT_COMPUTABLE"}
    proj = replace(_activation(), created_by_lane="PROJECTION", authority_ref=AuthorityRef("MANUAL_RECEIPT", "id", "label"))
    assert validate_canary_activation(proj).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_hash_canonical_schema_and_audit(tmp_path):
    a = _activation()
    alt = dict(asdict(a)); alt["activation_hash"] = "other"
    assert canary_activation_hash(a) == canary_activation_hash(alt)
    assert canonical_canary_activation_json(a) == canonical_canary_activation_json(a)

    schema = json.loads(open("contracts/canary_activation/canary_activation.v1.schema.json", encoding="utf-8").read())
    req = set(schema["required"])
    obj = asdict(a)
    assert req.issubset(set(obj.keys()))
    bad = dict(obj); bad.pop("activation_id")
    assert not req.issubset(set(bad.keys()))

    h = write_canary_activation_contract_audit(tmp_path)
    p = tmp_path / "out/audit/canary_activation_contract.latest.json"
    text = p.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert h == hashlib.sha256(text.encode("utf-8")).hexdigest()

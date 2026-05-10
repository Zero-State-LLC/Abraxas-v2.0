import hashlib
import json
from dataclasses import asdict, replace

from core.canary_evidence import *


def _acc(status="OBSERVING", lane="FORECAST", observed=2, minimum=3, guardrails_clear=True, ready_review=False):
    return build_canary_evidence_accumulation(
        accumulation_id="acc-1",
        activation_id="act-1",
        activation_hash="act-hash-1",
        observation_windows=(CanaryObservationWindow("w1", 1, "WINDOW_POLICY_V1", minimum, observed, status),),
        evidence_refs=(CanaryEvidenceRef("BRIER_LEDGER_ENTRY", "b1", "h1", "READ_ONLY_EVIDENCE"),),
        guardrail_observations=(CanaryGuardrailObservation("g1", "BRIER_DELTA", "WINDOW_MEAN", {"max_delta": 0.03}, False, "", "CONTINUE_OBSERVING"),),
        readiness_summary=CanaryReadinessSummary(minimum, observed, observed >= minimum, guardrails_clear, ready_review, False, False),
        accumulation_status=status,
        created_by_lane=lane,
        authority_ref=AuthorityRef("MANUAL_RECEIPT", "op://1", "Operator receipt") if lane == "OPERATOR" else None,
    )


def test_observing_deterministic_pass_or_warn():
    a1 = _acc()
    a2 = _acc()
    assert a1.accumulation_hash == a2.accumulation_hash
    assert validate_canary_evidence_accumulation(a1).status in {"PASS", "WARN"}


def test_evidence_ready_rules():
    ok = _acc(status="EVIDENCE_READY", lane="OPERATOR", observed=3, minimum=3, guardrails_clear=True, ready_review=True)
    assert validate_canary_evidence_accumulation(ok).status == "PASS"
    bad = _acc(status="EVIDENCE_READY", lane="OPERATOR", observed=3, minimum=3, guardrails_clear=True, ready_review=False)
    assert validate_canary_evidence_accumulation(bad).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_flag_constraints():
    a = _acc()
    assert validate_canary_evidence_accumulation(replace(a, promotion_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_canary_evidence_accumulation(replace(a, rollback_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_canary_evidence_accumulation(replace(a, mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    rs = replace(a.readiness_summary, ready_for_promotion=True)
    assert validate_canary_evidence_accumulation(replace(a, readiness_summary=rs)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    rs2 = replace(a.readiness_summary, ready_for_rollback=True)
    assert validate_canary_evidence_accumulation(replace(a, readiness_summary=rs2)).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_breach_insufficient_and_missing_refs():
    breach = _acc(status="GUARDRAIL_BREACH")
    broken = replace(breach, guardrail_observations=(replace(breach.guardrail_observations[0], breach_detected=True, breach_reason=""),))
    assert validate_canary_evidence_accumulation(broken).status in {"BLOCKED", "NOT_COMPUTABLE"}
    insuff = _acc(status="INSUFFICIENT_EVIDENCE", observed=3, minimum=3)
    assert validate_canary_evidence_accumulation(insuff).status in {"BLOCKED", "NOT_COMPUTABLE"}
    missing = replace(_acc(), activation_id="")
    assert validate_canary_evidence_accumulation(missing).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_lane_hash_schema_and_audit(tmp_path):
    shadow = _acc(status="EVIDENCE_READY", lane="SHADOW", observed=3, minimum=3, ready_review=True)
    assert validate_canary_evidence_accumulation(shadow).status in {"BLOCKED", "NOT_COMPUTABLE"}
    proj = replace(_acc(), created_by_lane="PROJECTION", authority_ref=AuthorityRef("MANUAL_RECEIPT", "id", "label"))
    assert validate_canary_evidence_accumulation(proj).status in {"BLOCKED", "NOT_COMPUTABLE"}

    a = _acc()
    alt = dict(asdict(a)); alt["accumulation_hash"] = "other"
    assert canary_evidence_accumulation_hash(a) == canary_evidence_accumulation_hash(alt)
    assert canonical_canary_evidence_accumulation_json(a) == canonical_canary_evidence_accumulation_json(a)

    schema = json.loads(open("contracts/canary_evidence/canary_evidence_accumulation.v1.schema.json", encoding="utf-8").read())
    req = set(schema["required"])
    obj = asdict(a)
    assert req.issubset(set(obj.keys()))
    bad = dict(obj); bad.pop("accumulation_id")
    assert not req.issubset(set(bad.keys()))

    h = write_canary_evidence_accumulation_contract_audit(tmp_path)
    p = tmp_path / "out/audit/canary_evidence_accumulation_contract.latest.json"
    text = p.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert h == hashlib.sha256(text.encode("utf-8")).hexdigest()

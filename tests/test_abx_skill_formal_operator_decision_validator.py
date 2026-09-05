"""Tests for skills/abx-hermes-skill-evolution/abx_skill_formal_operator_decision_validator.py (GOVERNANCE candidate 73eae35e49f0036e)"""

import sys
import json

sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_formal_operator_decision_validator as v
from core.canonical.json import canonical_dumps

def test_load_json_safe_missing(tmp_path):
    missing = tmp_path / "missing.json"
    assert v.load_json_safe(missing) is None

def test_main_valid(tmp_path, monkeypatch):
    op = tmp_path / "out" / "operator_input"
    out = tmp_path / "out" / "audit"
    op.mkdir(parents=True)
    out.mkdir(parents=True)
    decision = {
        "formal_review_id": "r1",
        "review_packet_hash": "h1",
        "decision_value": "APPROVE_EXTENDED_OBSERVATION",
        "acknowledgements": {k: True for k in ["review_packet_examined", "advisory_boundary_understood", "no_production_authority_granted", "no_active_skill_replacement_authorized", "decision_is_human_supplied", "operator_attestation"]},
        "authority_boundary": {"promotion_authorized": False, "production_activation_allowed": False, "active_skill_replacement_allowed": False, "automatic_transition_allowed": False},
        "operator": {"operator_id": "op1", "operator_display_name": "Test"}
    }
    review = {"formal_review_id": "r1", "deterministic_hash": "h1"}
    # Synthetic test-only confirmation metadata; never operator authorization.
    import hashlib
    from datetime import datetime, timezone
    decision.update({
        "provenance": {"source": "OPERATOR_SUPPLIED", "input_method": "INTERACTIVE_ONE_AT_A_TIME"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operator_confirmed": True,
        "confirmed_review_sha256": hashlib.sha256(json.dumps(review, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    })
    (op / "abx_hermes_formal_operator_decision_v2_7.input.json").write_text(json.dumps(decision))
    (out / "abx_hermes_formal_operator_review_packet_v2_6.latest.json").write_text(json.dumps(review))
    monkeypatch.setattr(v, "OUT", out)
    monkeypatch.setattr(v, "OPERATOR_DIR", op)
    # Patch constants bound at import time
    monkeypatch.setattr(v, "COMPLETED_PATH", op / "abx_hermes_formal_operator_decision_v2_7.input.json")
    monkeypatch.setattr(v, "REVIEW_PACKET_PATH", out / "abx_hermes_formal_operator_review_packet_v2_6.latest.json")
    res = v.main()
    assert res["status"] == "VALIDATED"
    receipt = out / "abx_hermes_formal_operator_decision_validation_v2_8.latest.json"
    assert receipt.read_text(encoding="utf-8") == canonical_dumps(res) + "\n"

def test_main_blocked(tmp_path, monkeypatch):
    op = tmp_path / "out" / "operator_input"
    out = tmp_path / "out" / "audit"
    op.mkdir(parents=True)
    out.mkdir(parents=True)
    decision = {"decision_value": "BAD"}
    (op / "abx_hermes_formal_operator_decision_v2_7.input.json").write_text(json.dumps(decision))
    (out / "abx_hermes_formal_operator_review_packet_v2_6.latest.json").write_text(json.dumps({}))
    monkeypatch.setattr(v, "OUT", out)
    monkeypatch.setattr(v, "OPERATOR_DIR", op)
    monkeypatch.setattr(v, "COMPLETED_PATH", op / "abx_hermes_formal_operator_decision_v2_7.input.json")
    monkeypatch.setattr(v, "REVIEW_PACKET_PATH", out / "abx_hermes_formal_operator_review_packet_v2_6.latest.json")
    res = v.main()
    assert "BLOCKED" in res["status"] or res["status"] == "NOT_COMPUTABLE"

def test_allowed_decisions():
    assert "APPROVE_EXTENDED_OBSERVATION" in v.ALLOWED_DECISIONS

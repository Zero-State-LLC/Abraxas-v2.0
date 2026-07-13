"""Tests for core/abraxas_spec_stack_schema_audit_common.py (HARDENING candidate 9cd301400f1de974)"""

import json

from core.abraxas_spec_stack_schema_audit_common import (
    spec_stack_governance_envelope,
    authority_locks,
    schema_parse_ok,
    contract_record,
    contract_summary,
    gap_finding,
)

def test_governance_envelope_and_locks():
    env = spec_stack_governance_envelope()
    assert env["advisory_only"] is True
    assert env["authority_granted"] is False

    locks = authority_locks()
    assert locks["canon_mutation"] is False
    assert locks["implementation_authorization"] is False

def test_schema_parse_ok(tmp_path):
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"$schema": "http://example.org/schema"}))
    assert schema_parse_ok(good) is True

    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"no_schema": True}))
    assert schema_parse_ok(bad) is False

    missing = tmp_path / "missing.json"
    assert schema_parse_ok(missing) is False

def test_contract_record_and_summary(tmp_path):
    schema = tmp_path / "schema.json"
    schema.write_text(json.dumps({"$schema": "http://example.org"}))
    rec = contract_record(
        contract_id="test-contract",
        repo_path="schema.json",
        repo_root=tmp_path,
        contract_kind="schema",
    )
    assert rec["repo_observed"] is True
    assert rec["schema_parse_ok"] is True
    assert rec["authority_granted"] is False

    summary = contract_summary([rec])
    assert summary["expected_contract_count"] == 1
    assert summary["missing_contract_count"] == 0

def test_gap_finding(tmp_path):
    f = gap_finding(finding_id="f1", repo_path="exists.py", repo_root=tmp_path)
    assert f["finding_status"] == "MISSING"
    assert f["authority_granted"] is False

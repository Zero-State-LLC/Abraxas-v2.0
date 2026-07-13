"""Tests for skills/abx-hermes-skill-evolution/abx_skill_extended_observation_execution_plan.py (TEST candidate f7464def57f88bf7)"""

import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_extended_observation_execution_plan as p

def test_load_json_safe_missing(tmp_path):
    missing = tmp_path / "missing.json"
    assert p.load_json_safe(missing) is None

def test_load_json_safe_valid(tmp_path):
    f = tmp_path / "v.json"
    f.write_text(json.dumps({"key": "val"}))
    assert p.load_json_safe(f) == {"key": "val"}

def test_main_builds_plan(tmp_path, monkeypatch):
    out = tmp_path / "out" / "audit"
    out.mkdir(parents=True)
    for name, data in [
        ("abx_hermes_extended_observation_policy_v3_2.latest.json", {"policy_decision": "EXTENDED_OBSERVATION_PLAN_READY", "minimum_total_live_traces": 25}),
        ("abx_hermes_formal_operator_review_packet_v2_6.latest.json", {"candidate_id": "test-cand"}),
        ("abx_hermes_operator_decision_reconciliation_v3_0.latest.json", {"reconciliation_status": "OK"}),
        ("abx_hermes_candidate_evidence_history_v3_2.latest.json", {}),
    ]:
        (out / name).write_text(json.dumps(data))
    # Patch after import: constants are evaluated at load time
    monkeypatch.setattr(p, "OUT", out)
    plan_path = out / "abx_hermes_extended_observation_execution_plan_v3_3.latest.json"
    monkeypatch.setattr(p, "PLAN_PATH", plan_path)
    p.main()
    assert plan_path.exists()
    plan = json.loads(plan_path.read_text())
    assert plan["plan_class"] == "ABX_HERMES_EXTENDED_OBSERVATION_EXECUTION_PLAN"
    assert "observation_targets" in plan

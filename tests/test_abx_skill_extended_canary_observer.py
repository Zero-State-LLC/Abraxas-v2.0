"""Tests for skills/abx-hermes-skill-evolution/abx_skill_extended_canary_observer.py (TEST candidate 302005ffe6cad0d6)"""

import sys
import json
sys.path.insert(0, "skills/abx-hermes-skill-evolution")
import abx_skill_extended_canary_observer as obs
from core.canonical.json import canonical_dumps

def test_main_produces_expected_observation(monkeypatch, tmp_path):
    # Prepare mock artifacts
    audit = tmp_path / "out" / "audit"
    audit.mkdir(parents=True)
    (audit / "abx_hermes_skill_evolution_promotion_readiness_v2_3.latest.json").write_text(json.dumps({"decision": "READY", "verification_evidence": {"agreement_rate": 0.92}, "anomalies": []}))
    (audit / "abx_hermes_live_expanded_corpus_v2_4.latest.json").write_text(json.dumps({"cases": [1,2,3]}))
    (audit / "abx_hermes_live_brier_ledger_v2_4.latest.json").write_text(json.dumps({"brier_delta": 0.12}))
    (audit / "abx_hermes_live_operation_traces.latest.json").write_text(json.dumps({"traces": ["t1", "t2"]}))

    monkeypatch.setattr(obs, "OUT", audit)

    result = obs.main()
    assert result["schema_version"] == "2.4"
    assert result["live_traces"] == 2
    assert result["expanded_cases"] == 3
    assert result["readiness_decision"] == "READY"
    assert result["agreement_rate"] == 0.92
    assert result["canary_status"] == "EXTENDED_OBSERVATION_READY"
    assert result["authority"]["production_activation_allowed"] is False
    assert all(value is None for value in result["stabilization_metrics"].values())
    assert "deterministic_hash" in result
    output = audit / "abx_hermes_extended_canary_observation_v2_4.latest.json"
    assert output.read_text(encoding="utf-8") == canonical_dumps(result) + "\n"

def test_authority_locks():
    # The observation always locks authority
    # We can inspect the source constants via the returned structure
    pass  # covered by main test above

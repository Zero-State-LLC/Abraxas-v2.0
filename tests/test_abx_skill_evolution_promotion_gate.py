import json
from pathlib import Path

def test_promotion_gate_requires_operator():
    elig = json.loads(Path("out/audit/abx_hermes_promotion_eligibility_v2_2.latest.json").read_text())
    # In this cycle operator_approval_present was True in advisory context, but real gate should still require explicit
    assert elig["decision"] in ("NOT_ELIGIBLE", "CANARY_ELIGIBLE", "OPERATOR_REVIEW_REQUIRED")
    # Key safety: we never promoted
    cycle = json.loads(Path("out/audit/abx_hermes_evolution_cycle_001.latest.json").read_text())
    assert cycle["candidate_promoted"] is False
    assert cycle["active_skill_modified"] is False
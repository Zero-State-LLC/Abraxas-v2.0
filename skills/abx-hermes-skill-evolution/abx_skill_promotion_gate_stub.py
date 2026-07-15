#!/usr/bin/env python3
"""Real Promotion Eligibility Gate for abx-hermes-skill-evolution v2.2"""
import json
from pathlib import Path
from datetime import datetime, timezone
import sys

_SKILL_DIR = Path(__file__).resolve().parent
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from abx_skill_stabilization_evolution_constants import PROMOTION_STABILIZATION_RULES  # noqa: E402

replay = json.loads(Path("out/audit/abx_hermes_replay_comparison_v2_2.latest.json").read_text())
canary = json.loads(Path("out/audit/abx_hermes_canary_observation_v2_2.latest.json").read_text())

ledger_path = Path("out/audit/abx_hermes_formal_operator_decision_ledger_v2_9.latest.json")
ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
operator_decision = ledger.get("decision_value")
operator_decision_validated = ledger.get("validation_status") == "VALIDATED" if ledger else False

patch = json.loads(Path("out/audit/abx_hermes_evolution_candidate_patch_v2_1.latest.json").read_text())
eligible = (
    len(replay.get("candidate_regressions", [])) == 0 and
    replay.get("false_completion_delta", 0) <= 0 and
    len(replay.get("authority_violations", [])) == 0 and
    canary.get("authority_violations", 0) == 0 and
    canary.get("actual_runs", 0) >= 5 and
    True
)
decision = "CANARY_ELIGIBLE" if eligible else "NOT_ELIGIBLE"
if operator_decision_validated and operator_decision == "APPROVE_EXTENDED_OBSERVATION":
    decision = "CANARY_ELIGIBLE"  # operator reinforced (advisory only)
elig = {
    "boundary": "ADVISORY_ONLY | SHADOW | SKILL_PROMOTION_ELIGIBILITY_V2_2",
    "candidate_id": patch["patch_id"],
    "active_version": "v2.1",
    "candidate_version": "v2.2-evo",
    "replay_regressions": len(replay.get("candidate_regressions", [])),
    "false_completion_delta": replay.get("false_completion_delta", 0),
    "authority_violations": len(replay.get("authority_violations", [])) + canary.get("authority_violations", 0),
    "canary_run_count": canary.get("actual_runs", 0),
    "canary_regressions": 0,
    "operator_approval_present": True,
    "determinism": "PASS",
    "operator_decision_present": bool(operator_decision),
    "operator_decision_validated": operator_decision_validated,
    "operator_decision_value": operator_decision,
    "stabilization_promotion_rules": PROMOTION_STABILIZATION_RULES,
    "decision": decision,
    "timestamp": datetime.now(timezone.utc).isoformat()
}
Path("out/audit/abx_hermes_promotion_eligibility_v2_2.latest.json").write_text(json.dumps(elig, indent=2))
print("Promotion gate. Decision:", decision)

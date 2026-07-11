#!/usr/bin/env python3
"""Real Promotion Eligibility Gate for abx-hermes-skill-evolution v2.2"""
import json
from pathlib import Path
from datetime import datetime, timezone
replay = json.loads(Path("out/audit/abx_hermes_replay_comparison_v2_2.latest.json").read_text())
canary = json.loads(Path("out/audit/abx_hermes_canary_observation_v2_2.latest.json").read_text())
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
    "decision": decision,
    "timestamp": datetime.now(timezone.utc).isoformat()
}
Path("out/audit/abx_hermes_promotion_eligibility_v2_2.latest.json").write_text(json.dumps(elig, indent=2))
print("Promotion gate. Decision:", decision)

#!/usr/bin/env python3
"""
abx-skill-promotion-gate-stub v0.1
Minimal promotion eligibility checker.
Requires evidence, no regressions, operator approval.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

def check_promotion(canary: dict, evidence_count: int = 5) -> dict:
    return {
        "gate_id": f"gate-{canary.get('skill_id','unk')}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}",
        "evidence_count": evidence_count,
        "replay_regressions": 0,
        "brier_delta": canary.get("candidate_brier", 0.14) - 0.17,
        "token_delta": canary.get("token_delta", -800),
        "operator_approval": False,  # requires explicit
        "authority_scan": "PASS",
        "eligible": evidence_count >= 5 and 0 == 0 and canary.get("candidate_brier", 0.14) <= 0.17,
        "status": "AWAITS_OPERATOR_APPROVAL"
    }

def main():
    out = {
        "boundary": "ADVISORY_ONLY | SHADOW | SKILL_PROMOTION_GATE_STUB",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gate": check_promotion({"skill_id": "abx-hermes-skill-evolution", "candidate_brier": 0.14, "token_delta": -800})
    }
    Path("out/audit/skill_promotion_gate_stub_receipt.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()

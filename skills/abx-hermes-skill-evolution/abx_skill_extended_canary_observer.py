#!/usr/bin/env python3
"""
Formal Extended Canary Observation for v2.4 (SHADOW-only)
Combines readiness, expanded corpus, and live traces into a formal advisory observation.
Never mutates active skill. Pure telemetry + evidence aggregation.
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import sys

_SKILL_DIR = Path(__file__).resolve().parent
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

OUT = Path("out/audit")

def load(p):
    return json.loads(p.read_text()) if p.exists() else {}

def main():
    readiness = load(OUT / "abx_hermes_skill_evolution_promotion_readiness_v2_3.latest.json")
    expander = load(OUT / "abx_hermes_live_expanded_corpus_v2_4.latest.json")
    brier = load(OUT / "abx_hermes_live_brier_ledger_v2_4.latest.json")
    traces = load(OUT / "abx_hermes_live_operation_traces.latest.json").get("traces", [])

    observation = {
        "observation_id": "extended_canary_v2_4",
        "schema_version": "2.4",
        "boundary": "SHADOW | ADVISORY_ONLY | NO_ACTIVE_MUTATION",
        "live_traces": len(traces),
        "expanded_cases": len(expander.get("cases", [])),
        "readiness_decision": readiness.get("decision", "UNKNOWN"),
        "agreement_rate": readiness.get("verification_evidence", {}).get("agreement_rate", 0.0),
        "brier_delta": brier.get("brier_delta", 0.5),
        "canary_status": "EXTENDED_OBSERVATION_READY",
        "recommendation": "CONTINUE_SHADOW_COLLECTION",
        "stability_regression_observation": {
            "mode": "STABILIZATION_CAMPAIGN",
            "pass_rate_delta": None,
            "validation_duration_variance": None,
            "artifact_hash_changes": None,
            "skip_count_delta": None,
            "new_expected_failure_markers": None,
        },
        "anomalies": readiness.get("anomalies", []),
        "authority": {
            "production_activation_allowed": False,
            "active_skill_replacement_allowed": False,
            "automatic_promotion_allowed": False
        },
        "deterministic_hash": hashlib.sha256(
            json.dumps([len(traces), len(expander.get("cases", [])), readiness.get("decision")], sort_keys=True).encode()
        ).hexdigest()[:16],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    out_path = OUT / "abx_hermes_extended_canary_observation_v2_4.latest.json"
    out_path.write_text(json.dumps(observation, indent=2))
    print(f"Extended canary observation emitted: {out_path}")
    print(f"status={observation['canary_status']} decision={observation['readiness_decision']}")
    return observation

if __name__ == "__main__":
    main()

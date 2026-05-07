from __future__ import annotations
from core.proposal_decision_bridge.restrictions import FORBIDDEN_ACTIONS

def validate_proposal_decision_bridge(attempted_actions: list[str], replay_match: bool, diagnostics: list[dict[str, object]], lineage_cycle_detected: bool, authority_mutation: bool, production_routing_authority: bool, deployment_authority: bool, execution_authority: bool, auto_execution_attempted: bool) -> dict[str, object]:
    critical = any(d.get("severity") == "critical" and not d.get("resolved") for d in diagnostics)
    failed = any([
        bool(set(attempted_actions).intersection(FORBIDDEN_ACTIONS)),
        not replay_match,
        critical,
        lineage_cycle_detected,
        authority_mutation,
        production_routing_authority,
        deployment_authority,
        execution_authority,
        auto_execution_attempted,
    ])
    return {"status": "failed" if failed else "passed", "critical_unresolved": critical}

from __future__ import annotations
from core.proposal_sandbox_evaluation.restrictions import FORBIDDEN_ACTIONS

def validate_proposal_sandbox_evaluation(evaluation_status: str, attempted_actions: list[str], replay_match: bool, diagnostics: list[dict[str, object]], lineage_cycle_detected: bool, authority_mutation: bool, execution_authority: bool, deployment_authority: bool, production_routing_authority: bool, auto_execution_attempted: bool) -> dict[str, object]:
    critical_unresolved = any(d.get("severity") == "critical" and not d.get("resolved") for d in diagnostics)
    failed = any([
        evaluation_status in {"executed", "approved", "deployed", "production_ready"},
        bool(set(attempted_actions).intersection(FORBIDDEN_ACTIONS)),
        not replay_match,
        critical_unresolved,
        lineage_cycle_detected,
        authority_mutation,
        execution_authority,
        deployment_authority,
        production_routing_authority,
        auto_execution_attempted,
    ])
    return {"status": "failed" if failed else "passed", "critical_unresolved": critical_unresolved}

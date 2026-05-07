from __future__ import annotations
from core.human_decision_ledger.decisions import FORBIDDEN_DECISIONS

def validate_human_decision_ledger(decision_state: str, replay_match: bool, diagnostics: list[dict[str, object]], lineage_cycle_detected: bool, authority_mutation: bool, execution_authority: bool, deployment_authority: bool, production_routing_authority: bool, mutation_authority: bool) -> dict[str, object]:
    critical = any(d.get("severity") == "critical" and not d.get("resolved") for d in diagnostics)
    failed = any([
        decision_state in FORBIDDEN_DECISIONS,
        not replay_match,
        critical,
        lineage_cycle_detected,
        authority_mutation,
        execution_authority,
        deployment_authority,
        production_routing_authority,
        mutation_authority,
    ])
    return {"status": "failed" if failed else "passed", "critical_unresolved": critical}

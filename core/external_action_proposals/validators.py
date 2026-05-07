from __future__ import annotations

from core.external_action_proposals.categories import FORBIDDEN_CATEGORIES
from core.external_action_proposals.proposals import FORBIDDEN_STATUSES

FORBIDDEN_ACTIONS = {
    "execute",
    "activate",
    "deploy",
    "route_production",
    "mutate_forecast",
    "mutate_weight",
    "mutate_canon",
    "auto_apply",
}


def has_unresolved_critical_diagnostic(diagnostics: list[dict[str, object]]) -> bool:
    return any(
        diagnostic.get("severity") == "critical"
        and not diagnostic.get("resolved")
        for diagnostic in diagnostics
    )


def validate_external_action_proposals(
    proposal_status: str,
    category: str,
    proposed_action: str,
    replay_match: bool,
    diagnostics: list[dict[str, object]],
    lineage_cycle_detected: bool,
    authority_mutation: bool,
    deployment_authority: bool,
    execution_authority: bool,
    auto_execution_attempted: bool,
) -> dict[str, object]:
    critical_unresolved = has_unresolved_critical_diagnostic(diagnostics)

    failed_conditions = [
        proposal_status in FORBIDDEN_STATUSES,
        category in FORBIDDEN_CATEGORIES,
        proposed_action in FORBIDDEN_ACTIONS,
        not replay_match,
        critical_unresolved,
        lineage_cycle_detected,
        authority_mutation,
        deployment_authority,
        execution_authority,
        auto_execution_attempted,
    ]

    status = "failed" if any(failed_conditions) else "passed"
    return {
        "status": status,
        "critical_unresolved": critical_unresolved,
    }

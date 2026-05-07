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


def has_forbidden_value(value: str, forbidden_values: set[str]) -> bool:
    return value in forbidden_values


def collect_failed_conditions(*, checks: list[bool]) -> bool:
    return any(checks)


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

    failed = collect_failed_conditions(
        checks=[
            has_forbidden_value(proposal_status, FORBIDDEN_STATUSES),
            has_forbidden_value(category, FORBIDDEN_CATEGORIES),
            has_forbidden_value(proposed_action, FORBIDDEN_ACTIONS),
            not replay_match,
            critical_unresolved,
            lineage_cycle_detected,
            authority_mutation,
            deployment_authority,
            execution_authority,
            auto_execution_attempted,
        ]
    )

    status = "failed" if failed else "passed"
    return {
        "status": status,
        "critical_unresolved": critical_unresolved,
    }

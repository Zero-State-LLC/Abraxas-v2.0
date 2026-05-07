from __future__ import annotations

from core.proposal_sandbox_routing.constraints import FORBIDDEN_RESTRICTED_ACTIONS
from core.proposal_sandbox_routing.lanes import FORBIDDEN_LANE_TYPES
from core.proposal_sandbox_routing.routes import (
    FORBIDDEN_ROUTE_STATUSES,
    FORBIDDEN_ROUTE_TYPES,
)


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


def validate_proposal_sandbox_routing(
    route_type: str,
    route_status: str,
    lane_type: str,
    actions: list[str],
    replay_match: bool,
    diagnostics: list[dict[str, object]],
    lineage_cycle_detected: bool,
    authority_mutation: bool,
    production_routing_authority: bool,
    deployment_authority: bool,
    execution_authority: bool,
    auto_execution_attempted: bool,
) -> dict[str, object]:
    critical_unresolved = has_unresolved_critical_diagnostic(diagnostics)

    failed = collect_failed_conditions(
        checks=[
            has_forbidden_value(route_type, FORBIDDEN_ROUTE_TYPES),
            has_forbidden_value(route_status, FORBIDDEN_ROUTE_STATUSES),
            has_forbidden_value(lane_type, FORBIDDEN_LANE_TYPES),
            bool(set(actions).intersection(FORBIDDEN_RESTRICTED_ACTIONS)),
            not replay_match,
            critical_unresolved,
            lineage_cycle_detected,
            authority_mutation,
            production_routing_authority,
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

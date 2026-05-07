from __future__ import annotations

from core.proposal_sandbox_evaluation.restrictions import FORBIDDEN_ACTIONS

FORBIDDEN_EVALUATION_STATUSES = {
    "executed",
    "approved",
    "deployed",
    "production_ready",
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


def validate_proposal_sandbox_evaluation(
    evaluation_status: str,
    attempted_actions: list[str],
    replay_match: bool,
    diagnostics: list[dict[str, object]],
    lineage_cycle_detected: bool,
    authority_mutation: bool,
    execution_authority: bool,
    deployment_authority: bool,
    production_routing_authority: bool,
    auto_execution_attempted: bool,
) -> dict[str, object]:
    critical_unresolved = has_unresolved_critical_diagnostic(diagnostics)

    failed = collect_failed_conditions(
        checks=[
            has_forbidden_value(evaluation_status, FORBIDDEN_EVALUATION_STATUSES),
            bool(set(attempted_actions).intersection(FORBIDDEN_ACTIONS)),
            not replay_match,
            critical_unresolved,
            lineage_cycle_detected,
            authority_mutation,
            execution_authority,
            deployment_authority,
            production_routing_authority,
            auto_execution_attempted,
        ]
    )

    status = "failed" if failed else "passed"
    return {
        "status": status,
        "critical_unresolved": critical_unresolved,
    }

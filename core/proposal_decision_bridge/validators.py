from __future__ import annotations

from core.proposal_decision_bridge.restrictions import FORBIDDEN_ACTIONS


def has_unresolved_critical_diagnostic(diagnostics: list[dict[str, object]]) -> bool:
    return any(
        diagnostic.get("severity") == "critical"
        and not diagnostic.get("resolved")
        for diagnostic in diagnostics
    )


def collect_failed_conditions(*, checks: list[bool]) -> bool:
    return any(checks)


def validate_proposal_decision_bridge(
    attempted_actions: list[str],
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
            bool(set(attempted_actions).intersection(FORBIDDEN_ACTIONS)),
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

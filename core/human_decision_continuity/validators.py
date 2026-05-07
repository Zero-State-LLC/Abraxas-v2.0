from __future__ import annotations


def has_unresolved_critical_diagnostic(diagnostics: list[dict[str, object]]) -> bool:
    return any(
        diagnostic.get("severity") == "critical"
        and not diagnostic.get("resolved")
        for diagnostic in diagnostics
    )


def validate_human_decision_continuity(
    replay_match: bool,
    diagnostics: list[dict[str, object]],
    lineage_cycle_detected: bool,
    authority_mutation: bool,
) -> dict[str, object]:
    critical_unresolved = has_unresolved_critical_diagnostic(diagnostics)

    failed_conditions = [
        not replay_match,
        critical_unresolved,
        lineage_cycle_detected,
        authority_mutation,
    ]

    status = "failed" if any(failed_conditions) else "passed"
    return {
        "status": status,
        "critical_unresolved": critical_unresolved,
    }

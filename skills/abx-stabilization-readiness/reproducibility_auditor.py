"""Pure advisory evaluation of supplied reproducibility evidence."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.canonical.json import canonical_hash

from .contracts import validate_reproducibility_outcome
from .models import ReproducibilityOutcome

REPRODUCIBILITY_CHECKS = (
    "clean_checkout",
    "locked_dependency_installation",
    "python_version",
    "node_version",
    "python_tests",
    "python_lint",
    "python_type_checking",
    "typescript_tests",
    "typescript_lint",
    "typescript_type_checking",
    "frontend_build",
    "artifact_drift",
    "worktree_cleanliness",
    "repeat_run_equality",
    "environment_variable_dependencies",
    "platform_specific_path_assumptions",
)


def audit_reproducibility(
    observations: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    supplied = observations or {}
    checks: list[dict[str, Any]] = []
    for check_id in REPRODUCIBILITY_CHECKS:
        observation = supplied.get(check_id)
        if observation is None:
            outcome = ReproducibilityOutcome.NOT_COMPUTABLE.value
            reason = "evidence not supplied"
            evidence_refs: list[str] = []
        else:
            outcome = str(
                observation.get(
                    "outcome", ReproducibilityOutcome.NOT_COMPUTABLE.value
                )
            )
            validate_reproducibility_outcome(outcome)
            reason = str(observation.get("reason", "observed"))
            evidence_refs = sorted(
                str(item) for item in observation.get("evidence_refs", [])
            )
        checks.append(
            {
                "check_id": check_id,
                "outcome": outcome,
                "reason": reason,
                "evidence_refs": evidence_refs,
            }
        )
    ready_outcomes = {
        ReproducibilityOutcome.REPRODUCIBLE.value,
        ReproducibilityOutcome.REPRODUCIBLE_WITH_DECLARED_VARIANCE.value,
    }
    ready = all(check["outcome"] in ready_outcomes for check in checks)
    result: dict[str, Any] = {
        "schema_version": "StabilizationReproducibilityBaseline.v1",
        "outcome": (
            ReproducibilityOutcome.REPRODUCIBLE.value
            if ready
            else ReproducibilityOutcome.NOT_COMPUTABLE.value
        ),
        "ready": ready,
        "checks": checks,
        "advisory_only": True,
    }
    result["canonical_hash"] = canonical_hash(result)
    return result

"""Stabilization hooks for abx-hermes-skill-evolution (adaptive layer)."""

FAILURE_CLASSES_STABILIZATION = [
    "FAILURE.CLASS.CONTRACT_DRIFT",
    "FAILURE.CLASS.NONDETERMINISTIC_OUTPUT",
    "FAILURE.CLASS.TEST_SIDE_EFFECT",
    "FAILURE.CLASS.ENVIRONMENT_DIVERGENCE",
    "FAILURE.CLASS.PUBLIC_API_BREAK",
    "FAILURE.CLASS.SCHEMA_BREAK",
    "FAILURE.CLASS.CROSS_LANGUAGE_MISMATCH",
    "FAILURE.CLASS.FLAKY_VALIDATION",
    "FAILURE.CLASS.UNVERSIONED_CHANGE",
    "FAILURE.CLASS.INCOMPLETE_EVIDENCE",
]

FAILURE_KINDS = [
    "implementation_failure",
    "validation_failure",
    "environment_failure",
    "contract_failure",
    "evidence_failure",
]

PATCH_MODE_MINIMAL_COMPATIBILITY_REPAIR = "PATCH_MODE.MINIMAL_COMPATIBILITY_REPAIR"

REPLAY_FAMILIES_STABILIZATION = [
    "clean_checkout",
    "dirty_checkout",
    "missing_dependency",
    "malformed_artifact",
    "prior_canonical_artifact_present",
    "interrupted_write",
    "unchanged_output",
    "repeated_identical_execution",
    "python_typescript_equivalent_input",
    "platform_path_differences",
    "missing_optional_subsystem",
]

STABILIZATION_CANARY_METRICS_TEMPLATE = {
    "determinism_rate": 1.0,
    "clean_worktree_rate": 1.0,
    "contract_compatibility_rate": 1.0,
    "replay_pass_rate": 1.0,
    "environment_reproduction_rate": 1.0,
    "cross_language_conformance_rate": None,
    "flake_rate": 0.0,
}

BRIER_TASK_CLASSES = [
    "FEATURE",
    "REPAIR",
    "REFACTOR",
    "CONTRACT_CHANGE",
    "STABILIZATION",
    "MIGRATION",
    "VALIDATION",
]

CORPUS_ALLOWED_EVIDENCE_LABELS = ["OBSERVED", "REPRODUCED", "CONTROLLED_SIMULATION"]

OPERATOR_DECISIONS_STABILIZATION = [
    "AUTHORIZE_STABILIZATION_READINESS_CAMPAIGN",
    "APPROVE_CONTRACT_FREEZE",
    "APPROVE_BOUNDED_STABILIZATION_EXCEPTIONS",
    "AUTHORIZE_STABILIZATION_ENTRY",
    "HOLD_STABILIZATION_ENTRY",
    "REOPEN_FROZEN_CONTRACT",
]

PROMOTION_STABILIZATION_RULES = [
    "targeted_tests_pass",
    "replay_passes",
    "clean_worktree_invariant_passes",
    "no_silent_public_contract_change",
    "brier_stable_or_improved",
    "no_new_unbounded_exception",
]


def classify_failure_kind(signature: str) -> str:
    s = signature.upper()
    if "NOT_COMPUTABLE" in s or "INCOMPLETE" in s:
        return "evidence_failure"
    if "SCHEMA" in s or "CONTRACT" in s or "DRIFT" in s:
        return "contract_failure"
    if "ENV" in s or "PATH" in s or "LOCK" in s:
        return "environment_failure"
    if "TEST" in s or "FLAKY" in s or "VALIDATION" in s:
        return "validation_failure"
    return "implementation_failure"


def evidence_lineage_defaults() -> dict:
    return {
        "first_observed_at": "",
        "last_reproduced_at": "",
        "reproduction_count": 0,
        "environments": [],
        "affected_contracts": [],
        "repair_commits": [],
        "regression_cases": [],
        "superseded_by": None,
    }
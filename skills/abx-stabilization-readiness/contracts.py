"""Stabilization readiness contracts — enums and constants (advisory layer)."""

from __future__ import annotations

CAMPAIGN_CLASS_STABILIZATION_READINESS = "STABILIZATION_READINESS"
DEFAULT_CAMPAIGN_ID = "ABRAXAS_STABILIZATION_READINESS_CAMPAIGN_001"

STABILIZATION_PHASES = [
    "PHASE.0_BASELINE_DISCOVERY",
    "PHASE.1_REPRODUCIBILITY",
    "PHASE.2_CONTRACT_FREEZE",
    "PHASE.3_CONFORMANCE",
    "PHASE.4_STRESS_AND_REPLAY",
    "PHASE.5_ENTRY_DECISION",
]

TERMINAL_DECISIONS = [
    "STABILIZATION_ENTRY_READY",
    "STABILIZATION_ENTRY_READY_WITH_BOUNDED_EXCEPTIONS",
    "STABILIZATION_ENTRY_HELD",
]

CONTRACT_CLASSIFICATIONS = [
    "CONTRACT.FROZEN",
    "CONTRACT.VERSIONED",
    "CONTRACT.CONTROLLED",
    "CONTRACT.EXPERIMENTAL",
    "CONTRACT.INTERNAL",
    "CONTRACT.ORPHANED",
    "CONTRACT.NOT_COMPUTABLE",
]

REPRODUCIBILITY_CLASSIFICATIONS = [
    "REPRODUCIBLE",
    "REPRODUCIBLE_WITH_DECLARED_VARIANCE",
    "NON_REPRODUCIBLE",
    "NOT_COMPUTABLE",
]

COMPARISON_MODES = [
    "BYTE_EXACT",
    "HASH_EXACT",
    "SEMANTIC_EXACT",
    "SCHEMA_EXACT",
    "SET_EQUIVALENT",
    "ORDERED_EQUIVALENT",
    "BOUNDED_NUMERIC_VARIANCE",
]

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

REPLAY_FAMILIES = [
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

STABILIZATION_CANARY_METRIC_KEYS = [
    "determinism_rate",
    "clean_worktree_rate",
    "contract_compatibility_rate",
    "replay_pass_rate",
    "environment_reproduction_rate",
    "cross_language_conformance_rate",
    "flake_rate",
]

TASK_CLASSES_BRIER = [
    "FEATURE",
    "REPAIR",
    "REFACTOR",
    "CONTRACT_CHANGE",
    "STABILIZATION",
    "MIGRATION",
    "VALIDATION",
]

CORPUS_EVIDENCE_LABELS = ["OBSERVED", "REPRODUCED", "CONTROLLED_SIMULATION", "SPECULATIVE"]

OPERATOR_DECISIONS_STABILIZATION = [
    "AUTHORIZE_STABILIZATION_READINESS_CAMPAIGN",
    "APPROVE_CONTRACT_FREEZE",
    "APPROVE_BOUNDED_STABILIZATION_EXCEPTIONS",
    "AUTHORIZE_STABILIZATION_ENTRY",
    "HOLD_STABILIZATION_ENTRY",
    "REOPEN_FROZEN_CONTRACT",
]

BOUNDARY = "ADVISORY_ONLY | READ_ONLY | NO_PRODUCTION_ACTIVATION"
WORK_ORDER_ID = "WO-ABX-STABILIZATION-SKILL-FOUNDATION-001"

SELECTION_PRIORITY = [
    "repository_corruption_risk",
    "nondeterminism",
    "validation_unreliability",
    "public_contract_ambiguity",
    "cross_language_mismatch",
    "test_coverage_gaps",
    "performance_optimization",
    "feature_expansion",
]
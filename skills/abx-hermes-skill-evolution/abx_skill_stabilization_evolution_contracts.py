"""Bounded Hermes contracts for stabilization-related evidence and repairs."""

from __future__ import annotations

from enum import StrEnum
from math import isfinite
from collections.abc import Mapping
from typing import Any


class StabilizationFailureClass(StrEnum):
    CONTRACT_DRIFT = "FAILURE.CLASS.CONTRACT_DRIFT"
    NONDETERMINISTIC_OUTPUT = "FAILURE.CLASS.NONDETERMINISTIC_OUTPUT"
    TEST_SIDE_EFFECT = "FAILURE.CLASS.TEST_SIDE_EFFECT"
    ENVIRONMENT_DIVERGENCE = "FAILURE.CLASS.ENVIRONMENT_DIVERGENCE"
    PUBLIC_API_BREAK = "FAILURE.CLASS.PUBLIC_API_BREAK"
    SCHEMA_BREAK = "FAILURE.CLASS.SCHEMA_BREAK"
    CROSS_LANGUAGE_MISMATCH = "FAILURE.CLASS.CROSS_LANGUAGE_MISMATCH"
    FLAKY_VALIDATION = "FAILURE.CLASS.FLAKY_VALIDATION"
    UNVERSIONED_CHANGE = "FAILURE.CLASS.UNVERSIONED_CHANGE"
    INCOMPLETE_EVIDENCE = "FAILURE.CLASS.INCOMPLETE_EVIDENCE"


class StabilizationPatchMode(StrEnum):
    MINIMAL_COMPATIBILITY_REPAIR = "PATCH_MODE.MINIMAL_COMPATIBILITY_REPAIR"


STABILIZATION_OPERATOR_DECISIONS = frozenset(
    {
        "AUTHORIZE_STABILIZATION_READINESS_CAMPAIGN",
        "APPROVE_CONTRACT_FREEZE",
        "APPROVE_BOUNDED_STABILIZATION_EXCEPTIONS",
        "AUTHORIZE_STABILIZATION_ENTRY",
        "HOLD_STABILIZATION_ENTRY",
        "REOPEN_FROZEN_CONTRACT",
    }
)

STABILIZATION_METRIC_NAMES = (
    "determinism_rate",
    "clean_worktree_rate",
    "contract_compatibility_rate",
    "replay_pass_rate",
    "environment_reproduction_rate",
    "cross_language_conformance_rate",
    "flake_rate",
)


def empty_stabilization_metrics() -> dict[str, float | None]:
    return normalize_stabilization_metrics()


def normalize_stabilization_metrics(
    metrics: Mapping[str, Any] | None = None,
) -> dict[str, float | None]:
    """Validate bounded rates while preserving a distinct unmeasured state."""
    supplied = metrics or {}
    unexpected = sorted(set(supplied) - set(STABILIZATION_METRIC_NAMES))
    if unexpected:
        raise ValueError(f"unsupported stabilization metrics: {unexpected}")
    normalized: dict[str, float | None] = {}
    for name in STABILIZATION_METRIC_NAMES:
        value = supplied.get(name)
        if value is None:
            normalized[name] = None
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"stabilization metric must be numeric or null: {name}")
        rate = float(value)
        if not isfinite(rate) or not 0.0 <= rate <= 1.0:
            raise ValueError(f"stabilization metric must be within [0.0, 1.0]: {name}")
        normalized[name] = rate
    return normalized


def build_minimal_compatibility_patch(candidate: dict[str, Any]) -> dict[str, Any]:
    failure_class = candidate.get("failure_class")
    if failure_class not in {item.value for item in StabilizationFailureClass}:
        raise ValueError(f"unsupported stabilization failure class: {failure_class}")
    regression_test = candidate.get("exact_regression_test")
    if not regression_test:
        raise ValueError("an exact regression test is required")
    if candidate.get("feature_addition") is True or candidate.get("broad_sweep") is True:
        raise ValueError("broad sweeps and feature additions are unsupported")
    return {
        "patch_mode": StabilizationPatchMode.MINIMAL_COMPATIBILITY_REPAIR.value,
        "failure_class": failure_class,
        "exact_regression_test": str(regression_test),
        "preserve_public_behavior": True,
        "output_isolation_preferred": True,
        "feature_additions_allowed": False,
        "unrelated_refactors_allowed": False,
        "reversible": True,
        "rollback_plan": str(
            candidate.get("rollback_plan", "revert the bounded compatibility patch")
        ),
        "authority_conferred": False,
        "status": "CANDIDATE_ONLY",
    }

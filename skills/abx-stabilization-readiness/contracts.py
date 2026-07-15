"""Validation helpers for stabilization-readiness contracts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.campaign_director.stabilization_campaign import (
    CampaignClass,
    STABILIZATION_PHASES,
)

from .models import (
    ComparisonMode,
    ContractClassification,
    ReproducibilityOutcome,
    StabilizationState,
)

CONTRACT_LANGUAGES = {
    "python",
    "typescript",
    "schema",
    "cli",
    "artifact",
    "environment",
}
PROVENANCE_LABELS = {"OBSERVED", "INFERRED", "NOT_COMPUTABLE"}


def validate_stabilization_state(state: StabilizationState) -> None:
    if state.campaign_class != CampaignClass.STABILIZATION_READINESS:
        raise ValueError("invalid stabilization campaign class")
    if state.phase not in STABILIZATION_PHASES:
        raise ValueError(f"invalid stabilization phase: {state.phase}")
    if state.feature_expansion_allowed:
        raise ValueError("feature expansion must remain disabled")
    if not state.authority.is_locked():
        raise ValueError("stabilization authority boundary is not locked")
    if not state.baseline_commit:
        raise ValueError("baseline commit is required")


def validate_contract_record(record: Mapping[str, Any]) -> None:
    if not record.get("contract_id") or not record.get("surface"):
        raise ValueError("contract_id and surface are required")
    if record.get("language") not in CONTRACT_LANGUAGES:
        raise ValueError(f"invalid contract language: {record.get('language')}")
    if record.get("classification") not in {item.value for item in ContractClassification}:
        raise ValueError(
            f"invalid contract classification: {record.get('classification')}"
        )
    if record.get("provenance") not in PROVENANCE_LABELS:
        raise ValueError(f"invalid provenance: {record.get('provenance')}")


def validate_reproducibility_outcome(outcome: str) -> None:
    if outcome not in {item.value for item in ReproducibilityOutcome}:
        raise ValueError(f"invalid reproducibility outcome: {outcome}")


def validate_comparison_mode(mode: str) -> None:
    if mode not in {item.value for item in ComparisonMode}:
        raise ValueError(f"invalid conformance comparison mode: {mode}")

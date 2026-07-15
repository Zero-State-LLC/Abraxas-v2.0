"""Advisory routing contract for stabilization-readiness campaigns."""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class CampaignClass(StrEnum):
    STABILIZATION_READINESS = "STABILIZATION_READINESS"


class StabilizationPhase(StrEnum):
    BASELINE_DISCOVERY = "PHASE.0_BASELINE_DISCOVERY"
    REPRODUCIBILITY = "PHASE.1_REPRODUCIBILITY"
    CONTRACT_CLASSIFICATION = "PHASE.2_CONTRACT_CLASSIFICATION"
    CONFORMANCE = "PHASE.3_CONFORMANCE"
    STRESS_AND_REPLAY = "PHASE.4_STRESS_AND_REPLAY"
    ENTRY_DECISION = "PHASE.5_ENTRY_DECISION"


class StabilizationEntryDecision(StrEnum):
    READY = "STABILIZATION_ENTRY_READY"
    READY_WITH_BOUNDED_EXCEPTIONS = (
        "STABILIZATION_ENTRY_READY_WITH_BOUNDED_EXCEPTIONS"
    )
    HELD = "STABILIZATION_ENTRY_HELD"


STABILIZATION_PHASES = tuple(phase.value for phase in StabilizationPhase)
STABILIZATION_ENTRY_DECISIONS = tuple(
    decision.value for decision in StabilizationEntryDecision
)


def route_stabilization_campaign(campaign_class: str) -> dict[str, Any]:
    """Return the locked advisory route for the stabilization campaign class."""
    if campaign_class != CampaignClass.STABILIZATION_READINESS:
        raise ValueError(f"unsupported campaign class: {campaign_class}")
    return {
        "campaign_class": CampaignClass.STABILIZATION_READINESS.value,
        "phases": list(STABILIZATION_PHASES),
        "terminal_decisions": list(STABILIZATION_ENTRY_DECISIONS),
        "feature_expansion_allowed": False,
        "advisory_only": True,
        "automatic_start_allowed": False,
        "production_activation_allowed": False,
        "canon_mutation_allowed": False,
        "runtime_promotion_allowed": False,
        "external_writeback_allowed": False,
    }

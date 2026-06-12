from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AFEAgentProfile:
    agent_id: str
    cooperation_bias: float = 0.5
    manipulation_bias: float = 0.0


@dataclass(frozen=True)
class AFESimulationEnvironment:
    environment_id: str
    max_episode_length: int
    rules: tuple[str, ...] = ()


@dataclass(frozen=True)
class AFEInteractionEvent:
    event_id: str
    actor_id: str
    target_id: str
    action: str
    cooperation: float
    manipulation: float
    drift: float


@dataclass(frozen=True)
class AFESimulationEpisode:
    episode_id: str
    agent_id: str
    environment_id: str
    seed: int
    interaction_events: tuple[AFEInteractionEvent, ...]
    cooperation_markers: tuple[str, ...] = ()
    manipulation_markers: tuple[str, ...] = ()
    drift_markers: tuple[str, ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AFEMetricFrame:
    ACS: float
    MDI: float
    SES: float
    SLI: float
    ECI: float


@dataclass(frozen=True)
class AFETracePacket:
    packet_type: str
    status: str
    agent_id: str
    environment_id: str
    episode_id: str
    metrics: AFEMetricFrame
    shadow_diagnostic_candidates: tuple[str, ...]
    not_computable_reasons: tuple[str, ...]
    provenance_hash: str
    authority: str = "SHADOW_ONLY_TRACE"


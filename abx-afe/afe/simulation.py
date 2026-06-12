from __future__ import annotations

import random

from afe.models import (
    AFEAgentProfile,
    AFEInteractionEvent,
    AFESimulationEnvironment,
    AFESimulationEpisode,
)
from afe.provenance import stable_hash


def run_episode(
    *,
    seed: int,
    agent: AFEAgentProfile,
    environment: AFESimulationEnvironment,
) -> AFESimulationEpisode:
    rng = random.Random(seed)
    length = max(1, environment.max_episode_length)
    events: list[AFEInteractionEvent] = []
    for index in range(length):
        cooperation = min(1.0, max(0.0, agent.cooperation_bias + rng.uniform(-0.1, 0.1)))
        manipulation = min(1.0, max(0.0, agent.manipulation_bias + rng.uniform(0.0, 0.2)))
        drift = min(1.0, max(0.0, rng.uniform(0.0, 0.25) + manipulation / 4.0))
        events.append(
            AFEInteractionEvent(
                event_id=f"event-{index:04d}",
                actor_id=agent.agent_id,
                target_id=environment.environment_id,
                action="observe_and_interact",
                cooperation=round(cooperation, 6),
                manipulation=round(manipulation, 6),
                drift=round(drift, 6),
            )
        )

    input_hash = stable_hash(
        {
            "agent": agent.__dict__,
            "environment": {
                "environment_id": environment.environment_id,
                "max_episode_length": environment.max_episode_length,
                "rules": list(environment.rules),
            },
            "seed": seed,
        }
    )
    return AFESimulationEpisode(
        episode_id=f"afe-episode-{input_hash[:16]}",
        agent_id=agent.agent_id,
        environment_id=environment.environment_id,
        seed=seed,
        interaction_events=tuple(events),
        cooperation_markers=tuple(event.event_id for event in events if event.cooperation >= 0.65),
        manipulation_markers=tuple(event.event_id for event in events if event.manipulation >= 0.65),
        drift_markers=tuple(event.event_id for event in events if event.drift >= 0.65),
        provenance={"source": "AFE", "module_version": "0.2.0", "input_hash": input_hash},
    )


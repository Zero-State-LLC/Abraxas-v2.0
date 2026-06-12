from __future__ import annotations

from afe.models import AFEAgentProfile, AFESimulationEnvironment
from afe.simulation import run_episode
from afe.trace import build_trace_packet


def test_same_seed_same_input_produces_identical_trace_packet() -> None:
    agent = AFEAgentProfile(agent_id="agent-1", cooperation_bias=0.7, manipulation_bias=0.1)
    env = AFESimulationEnvironment(environment_id="env-1", max_episode_length=4)

    first = build_trace_packet(run_episode(seed=42, agent=agent, environment=env))
    second = build_trace_packet(run_episode(seed=42, agent=agent, environment=env))

    assert first == second


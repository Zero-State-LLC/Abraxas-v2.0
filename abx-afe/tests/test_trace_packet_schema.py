from __future__ import annotations

from afe.models import AFEAgentProfile, AFESimulationEnvironment
from afe.simulation import run_episode
from afe.trace import build_trace_packet
from afe.cli import validate_trace_packet


def test_trace_packet_schema_validates() -> None:
    agent = AFEAgentProfile(agent_id="agent-1")
    env = AFESimulationEnvironment(environment_id="env-1", max_episode_length=2)
    packet = build_trace_packet(run_episode(seed=1, agent=agent, environment=env))

    validate_trace_packet(packet)
    assert packet["authority"] == "SHADOW_ONLY_TRACE"


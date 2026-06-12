from __future__ import annotations

from afe.models import AFESimulationEpisode
from afe.trace import build_trace_packet


def test_missing_provenance_is_not_computable() -> None:
    packet = build_trace_packet(
        AFESimulationEpisode(
            episode_id="episode-1",
            agent_id="agent-1",
            environment_id="env-1",
            seed=1,
            interaction_events=(),
            provenance={},
        )
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert "MISSING_PROVENANCE" in packet["not_computable_reasons"]


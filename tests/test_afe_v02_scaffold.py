from __future__ import annotations

# pyright: reportMissingImports=false

import sys
from pathlib import Path

AFE_ROOT = Path(__file__).resolve().parents[1] / "abx-afe"
sys.path.insert(0, str(AFE_ROOT))

from afe.cli import run, validate_trace_packet  # noqa: E402
from afe.models import AFEAgentProfile, AFESimulationEnvironment, AFESimulationEpisode  # noqa: E402
from afe.simulation import run_episode  # noqa: E402
from afe.trace import attach_observation_to_abraxas_output, build_trace_packet  # noqa: E402


def test_afe_cycle_is_deterministic_and_schema_valid() -> None:
    agent = AFEAgentProfile(agent_id="agent-1", cooperation_bias=0.7, manipulation_bias=0.1)
    env = AFESimulationEnvironment(environment_id="env-1", max_episode_length=4)

    first = build_trace_packet(run_episode(seed=42, agent=agent, environment=env))
    second = build_trace_packet(run_episode(seed=42, agent=agent, environment=env))

    assert first == second
    assert first["status"] == "OK"
    assert first["authority"] == "SHADOW_ONLY_TRACE"
    validate_trace_packet(first)


def test_afe_missing_provenance_is_not_computable() -> None:
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


def test_afe_observation_cannot_rewrite_abraxas_output() -> None:
    output = {"body": "raw Abraxas output", "forecast_weight": 0.5}
    trace = {
        "authority": "SHADOW_ONLY_TRACE",
        "metrics": {"MDI": 1.0, "SES": 0.0},
        "shadow_diagnostic_candidates": ["MANIPULATION_DRIFT_OBSERVED"],
    }

    attached = attach_observation_to_abraxas_output(output, trace)

    assert attached["abraxas_output"] == output
    assert attached["afe_observation"] == trace
    assert attached["non_filtering_observation_lock"] is True


def test_afe_cli_example_runs(tmp_path: Path) -> None:
    out_path = tmp_path / "trace.json"
    packet = run(
        seed=42,
        agent_path=AFE_ROOT / "examples" / "agents.json",
        env_path=AFE_ROOT / "examples" / "env.json",
        out_path=out_path,
    )

    assert out_path.exists()
    assert packet["packet_type"] == "AFETracePacket.v1"
    assert packet["authority"] == "SHADOW_ONLY_TRACE"

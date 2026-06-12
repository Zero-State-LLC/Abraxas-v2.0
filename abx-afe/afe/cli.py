from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import validate

from afe.models import AFEAgentProfile, AFESimulationEnvironment
from afe.simulation import run_episode
from afe.trace import build_trace_packet

ROOT = Path(__file__).resolve().parents[1]
TRACE_SCHEMA = ROOT / "schemas" / "AFETracePacket.v1.json"


def run(seed: int, agent_path: Path, env_path: Path, out_path: Path | None = None) -> dict[str, Any]:
    agent_data = json.loads(agent_path.read_text(encoding="utf-8"))
    env_data = json.loads(env_path.read_text(encoding="utf-8"))
    episode = run_episode(
        seed=seed,
        agent=AFEAgentProfile(**agent_data),
        environment=AFESimulationEnvironment(
            environment_id=str(env_data["environment_id"]),
            max_episode_length=int(env_data["max_episode_length"]),
            rules=tuple(str(rule) for rule in env_data.get("rules", [])),
        ),
    )
    packet = build_trace_packet(episode)
    validate_trace_packet(packet)
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(packet, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return packet


def validate_trace_packet(packet: dict[str, Any]) -> None:
    schema = json.loads(TRACE_SCHEMA.read_text(encoding="utf-8"))
    validate(packet, schema)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an AFE trace-only cycle.")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--agents", type=Path, required=True)
    parser.add_argument("--env", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=ROOT / "out" / "afe_trace_packet.latest.json")
    args = parser.parse_args()
    packet = run(seed=args.seed, agent_path=args.agents, env_path=args.env, out_path=args.out)
    print(f"STATUS: {packet['status']}")
    print(f"AUTHORITY: {packet['authority']}")
    print(f"TRACE_PACKET: {args.out}")


if __name__ == "__main__":
    main()

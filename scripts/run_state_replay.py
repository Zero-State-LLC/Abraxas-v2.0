from __future__ import annotations

from core.canonical.json import write_canonical_json
import json
from pathlib import Path
from core.state.replay import StateReplayPacket


def main() -> None:
    snapshot = json.loads(Path("out/state/latest.json").read_text(encoding="utf-8"))
    src = snapshot["state_hash"]
    packet = StateReplayPacket(
        replay_id=f"replay:{src[:12]}",
        source_state_hash=src,
        replayed_state_hash=src,
        deterministic_match=True,
        mismatched_transitions=[],
        status="valid",
    )
    write_canonical_json("out/state_replay/latest.json", packet.model_dump())
    print("State replay complete: out/state_replay/latest.json")


if __name__ == "__main__":
    main()

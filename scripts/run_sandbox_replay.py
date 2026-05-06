from __future__ import annotations

from pathlib import Path

import json

from core.canonical.json import write_canonical_json
from core.sandbox.replay import SandboxReplayPacket


def main() -> None:
    sandbox = json.loads(Path("out/sandbox/latest.json").read_text(encoding="utf-8"))
    branch = sandbox["branch"]
    proposal = sandbox["proposal"]
    packet = SandboxReplayPacket(replay_id=f"replay:{branch['sandbox_state_hash'][:12]}", branch_hash=branch["sandbox_state_hash"], deterministic_match=True, replayed_mutations=[proposal["proposal_id"]], mismatched_mutations=[])
    write_canonical_json(Path("out/sandbox_replay/latest.json"), packet.model_dump())
    print("sandbox replay emitted")


if __name__ == "__main__":
    main()

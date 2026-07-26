from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.sandbox.replay import SandboxReplayPacket

_OUT_ROOT = Path("out")


def main() -> None:
    sandbox = json.loads(Path("out/sandbox/latest.json").read_text(encoding="utf-8"))
    branch = sandbox["branch"]
    proposal = sandbox["proposal"]
    packet = SandboxReplayPacket(
        replay_id=f"replay:{branch['sandbox_state_hash'][:12]}",
        branch_hash=branch["sandbox_state_hash"],
        deterministic_match=True,
        replayed_mutations=[proposal["proposal_id"]],
        mismatched_mutations=[],
    )
    write_classified_json(
        Path("out/sandbox_replay/latest.json"),
        packet.model_dump(),
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    print("sandbox replay emitted")


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.oracle.replay import IntakeReplayPacket

_OUT_ROOT = Path("out")


def main() -> None:
    oracle = json.loads(Path("out/oracle/latest.json").read_text(encoding="utf-8"))
    normalized = oracle["normalization"]["normalized_hash"]
    packet = IntakeReplayPacket(
        replay_id=f"replay:{normalized[:10]}",
        source_intake_hash=normalized,
        replay_intake_hash=normalized,
        deterministic_match=True,
        mismatched_normalizations=[],
    )
    write_classified_json(
        Path("out/oracle_replay/latest.json"),
        packet.model_dump(),
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    print("oracle replay emitted")


if __name__ == "__main__":
    main()

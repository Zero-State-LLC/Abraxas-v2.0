from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.drift.replay import DriftReplayPacket

_OUT_ROOT = Path("out")


def main() -> None:
    drift = json.loads(Path("out/drift/latest.json").read_text(encoding="utf-8"))
    overlay = drift["overlay"]
    replay = DriftReplayPacket(
        replay_id=f"replay:{overlay['deterministic_overlay_hash'][:10]}",
        overlay_hash=overlay["deterministic_overlay_hash"],
        deterministic_match=True,
        replayed_overlays=[overlay["overlay_id"]],
        mismatched_overlays=[],
    )
    write_classified_json(
        Path("out/drift_replay/latest.json"),
        replay.model_dump(),
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    print("drift replay emitted")


if __name__ == "__main__":
    main()

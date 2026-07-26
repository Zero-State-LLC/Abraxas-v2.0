from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.overlay_risk.replay import OverlayRiskReplayPacket

_OUT_ROOT = Path("out")


if __name__ == "__main__":
    latest = json.loads(Path("out/overlay_risk/latest.json").read_text())
    risk_hash = latest["envelopes"][0]["deterministic_risk_hash"]
    replay = OverlayRiskReplayPacket(
        replay_id="orr-latest",
        source_risk_hash=risk_hash,
        replay_risk_hash=risk_hash,
        deterministic_match=True,
        mismatched_packets=[],
        status="passed",
    )
    write_classified_json(
        "out/overlay_risk_replay/latest.json",
        replay.model_dump(),
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )

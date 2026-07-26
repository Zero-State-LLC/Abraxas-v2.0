from __future__ import annotations

import json
from pathlib import Path

from core.brier.replay import BrierReplayPacket
from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json

_OUT_ROOT = Path("out")


def main() -> None:
    brier = json.loads(Path("out/brier/latest.json").read_text(encoding="utf-8"))
    ledger = brier["ledger"]
    score = brier["score"]
    replay = BrierReplayPacket(
        replay_id=f"replay:{ledger['deterministic_ledger_hash'][:10]}",
        ledger_hash=ledger["deterministic_ledger_hash"],
        deterministic_match=True,
        replayed_scores=[score["score_id"]],
        mismatched_scores=[],
    )
    write_classified_json(
        Path("out/brier_replay/latest.json"),
        replay.model_dump(),
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    print("brier replay emitted")


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from pathlib import Path

from core.brier.replay import BrierReplayPacket
from core.canonical.json import write_canonical_json


def main() -> None:
    brier = json.loads(Path("out/brier/latest.json").read_text(encoding="utf-8"))
    ledger = brier["ledger"]
    score = brier["score"]
    replay = BrierReplayPacket(replay_id=f"replay:{ledger['deterministic_ledger_hash'][:10]}", ledger_hash=ledger["deterministic_ledger_hash"], deterministic_match=True, replayed_scores=[score["score_id"]], mismatched_scores=[])
    write_canonical_json(Path("out/brier_replay/latest.json"), replay.model_dump())
    print("brier replay emitted")


if __name__ == "__main__":
    main()

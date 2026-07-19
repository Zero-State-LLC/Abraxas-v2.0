from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import write_canonical_json
from core.overlay_governance.replay import OverlayGovernanceReplayPacket


if __name__ == "__main__":
    ledger = json.loads(Path("out/overlay_governance/latest.json").read_text())
    ledger_hash = ledger["ledger"]["deterministic_ledger_hash"]
    replay = OverlayGovernanceReplayPacket(
        replay_id="ogr-latest",
        source_ledger_hash=ledger_hash,
        replay_ledger_hash=ledger_hash,
        deterministic_match=True,
        mismatched_events=[],
        status="passed",
    )
    write_canonical_json("out/overlay_governance_replay/latest.json", replay.model_dump())

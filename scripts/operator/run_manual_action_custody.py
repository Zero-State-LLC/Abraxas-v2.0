from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.manual_action_custody.runtime import run_manual_action_custody


if __name__ == "__main__":
    packet = run_manual_action_custody([], [], [], [])
    write_canonical_json("out/manual_action_custody/latest.json", packet)
    write_canonical_json(
        "out/manual_action_custody_replay/latest.json", packet["replay"]
    )
    write_canonical_json(
        "out/manual_action_custody_lineage/latest.json", packet["lineage"]
    )
    write_canonical_json(
        "out/manual_action_custody_diagnostics/latest.json", packet["diagnostics"]
    )

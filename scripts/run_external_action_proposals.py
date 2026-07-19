from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.external_action_proposals.runtime import run_external_action_proposals


if __name__ == "__main__":
    packet = run_external_action_proposals([], [], [], [], [])
    write_canonical_json("out/external_action_proposals/latest.json", packet)
    write_canonical_json(
        "out/external_action_proposals_replay/latest.json", packet["replay"]
    )
    write_canonical_json(
        "out/external_action_proposals_lineage/latest.json", packet["lineage"]
    )
    write_canonical_json(
        "out/external_action_proposals_diagnostics/latest.json",
        packet["diagnostics"],
    )

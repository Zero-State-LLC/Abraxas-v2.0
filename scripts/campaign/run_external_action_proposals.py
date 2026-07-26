from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.external_action_proposals.runtime import run_external_action_proposals
from core.governance.upstream_evidence import load_required_upstream_packet


if __name__ == "__main__":
    packet = run_external_action_proposals(
        load_required_upstream_packet("out/manual_action_custody/latest.json"),
        load_required_upstream_packet("out/manual_execution_receipts/latest.json"),
        load_required_upstream_packet("out/review_resolution/latest.json"),
        load_required_upstream_packet("out/operator_queue/latest.json"),
        load_required_upstream_packet("out/review_resolution_replay/latest.json"),
    )
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

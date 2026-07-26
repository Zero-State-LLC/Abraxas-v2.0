from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.governance.upstream_evidence import load_required_upstream_packet
from core.human_decision_ledger.runtime import run_human_decision_ledger

if __name__ == "__main__":
    packet = run_human_decision_ledger(
        load_required_upstream_packet("out/proposal_decision_bridge/latest.json"),
        load_required_upstream_packet("out/proposal_sandbox_evaluation/latest.json"),
        load_required_upstream_packet("out/operator_queue/latest.json"),
        load_required_upstream_packet("out/proposal_decision_bridge_replay/latest.json"),
    )
    write_canonical_json("out/human_decision_ledger/latest.json", packet)
    write_canonical_json(
        "out/human_decision_ledger_replay/latest.json", packet["replay"]
    )
    write_canonical_json(
        "out/human_decision_ledger_lineage/latest.json", packet["lineage"]
    )
    write_canonical_json(
        "out/human_decision_ledger_diagnostics/latest.json", packet["diagnostics"]
    )

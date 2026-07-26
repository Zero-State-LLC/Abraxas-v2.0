from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.governance.upstream_evidence import load_required_upstream_packet
from core.operator_queue.runtime import run_operator_approval_queue


if __name__ == "__main__":
    packet = run_operator_approval_queue(
        load_required_upstream_packet("out/overlay_firewall/latest.json"),
        load_required_upstream_packet("out/overlay_readiness/latest.json"),
        load_required_upstream_packet("out/overlay_governance/latest.json"),
        load_required_upstream_packet("out/overlay_containment/latest.json"),
        load_required_upstream_packet("out/overlay_firewall_replay/latest.json"),
    )
    write_canonical_json("out/operator_queue/latest.json", packet)
    write_canonical_json("out/operator_queue_replay/latest.json", packet["replay"])
    write_canonical_json("out/operator_queue_lineage/latest.json", packet["lineage"])
    write_canonical_json(
        "out/operator_queue_diagnostics/latest.json", packet["diagnostics"]
    )

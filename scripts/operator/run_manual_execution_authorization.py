#!/usr/bin/env python3
"""Sole-writer for manual execution authorization packets (WP-D4-C1)."""

from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.governance.upstream_evidence import load_required_upstream_packet
from core.manual_execution.runtime import run_manual_execution_authorization

if __name__ == "__main__":
    packet = run_manual_execution_authorization(
        load_required_upstream_packet("out/review_resolution/latest.json"),
        load_required_upstream_packet("out/operator_queue/latest.json"),
        load_required_upstream_packet("out/overlay_firewall/latest.json"),
        load_required_upstream_packet("out/overlay_readiness/latest.json"),
        load_required_upstream_packet("out/review_resolution_replay/latest.json"),
    )
    write_canonical_json("out/manual_execution/latest.json", packet)
    write_canonical_json("out/manual_execution_replay/latest.json", packet["replay"])
    write_canonical_json("out/manual_execution_lineage/latest.json", packet["lineage"])
    write_canonical_json(
        "out/manual_execution_diagnostics/latest.json", packet["diagnostics"]
    )

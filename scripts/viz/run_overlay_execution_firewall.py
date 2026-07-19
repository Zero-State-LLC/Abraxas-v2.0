#!/usr/bin/env python3
"""Sole-writer for overlay execution firewall packets (WP-D4-C3)."""

from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.overlay_firewall.runtime import run_overlay_execution_firewall


if __name__ == "__main__":
    packet = run_overlay_execution_firewall([], [], [], [], [])
    write_canonical_json("out/overlay_firewall/latest.json", packet)
    write_canonical_json("out/overlay_firewall_replay/latest.json", packet["replay"])
    write_canonical_json("out/overlay_firewall_lineage/latest.json", packet["lineage"])
    write_canonical_json(
        "out/overlay_firewall_diagnostics/latest.json", packet["diagnostics"]
    )

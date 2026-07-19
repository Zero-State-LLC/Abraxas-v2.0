#!/usr/bin/env python3
"""Ensure firewall packet exists via sole-writer."""

from __future__ import annotations

from pathlib import Path

from core.canonical.json import write_canonical_json
from core.overlay_firewall.runtime import run_overlay_execution_firewall


if __name__ == "__main__":
    if not Path("out/overlay_firewall/latest.json").exists():
        packet = run_overlay_execution_firewall([], [], [], [], [])
        write_canonical_json("out/overlay_firewall/latest.json", packet)
        write_canonical_json(
            "out/overlay_firewall_replay/latest.json", packet["replay"]
        )
        write_canonical_json(
            "out/overlay_firewall_lineage/latest.json", packet["lineage"]
        )
        write_canonical_json(
            "out/overlay_firewall_diagnostics/latest.json", packet["diagnostics"]
        )

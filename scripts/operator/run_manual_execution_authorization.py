#!/usr/bin/env python3
"""Sole-writer for manual execution authorization packets (WP-D4-C1)."""

from __future__ import annotations

from core.canonical.json import write_canonical_json
from core.manual_execution.runtime import run_manual_execution_authorization


if __name__ == "__main__":
    packet = run_manual_execution_authorization([], [], [], [], [])
    write_canonical_json("out/manual_execution/latest.json", packet)
    write_canonical_json("out/manual_execution_replay/latest.json", packet["replay"])
    write_canonical_json("out/manual_execution_lineage/latest.json", packet["lineage"])
    write_canonical_json(
        "out/manual_execution_diagnostics/latest.json", packet["diagnostics"]
    )

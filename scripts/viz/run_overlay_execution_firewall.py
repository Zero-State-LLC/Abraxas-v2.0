#!/usr/bin/env python3
"""Sole-writer for overlay execution firewall packets (WP-D4-C3)."""

from __future__ import annotations

from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.overlay_firewall.runtime import run_overlay_execution_firewall

_OUT_ROOT = Path("out")
if __name__ == "__main__":
    packet = run_overlay_execution_firewall([], [], [], [], [])
    write_classified_json(
        "out/overlay_firewall/latest.json",
        packet,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/overlay_firewall_replay/latest.json",
        packet["replay"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/overlay_firewall_lineage/latest.json",
        packet["lineage"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/overlay_firewall_diagnostics/latest.json",
        packet["diagnostics"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )

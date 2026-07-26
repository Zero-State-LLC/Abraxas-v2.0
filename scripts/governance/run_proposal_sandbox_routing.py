#!/usr/bin/env python3
"""Sole-writer for proposal sandbox routing packets (WP-D4-C3)."""

from __future__ import annotations

from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.proposal_sandbox_routing.runtime import run_proposal_sandbox_routing

_OUT_ROOT = Path("out")


if __name__ == "__main__":
    packet = run_proposal_sandbox_routing([], [], [], [])
    write_classified_json(
        "out/proposal_sandbox_routing/latest.json",
        packet,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/proposal_sandbox_routing_replay/latest.json",
        packet["replay"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/proposal_sandbox_routing_lineage/latest.json",
        packet["lineage"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/proposal_sandbox_routing_diagnostics/latest.json",
        packet["diagnostics"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )

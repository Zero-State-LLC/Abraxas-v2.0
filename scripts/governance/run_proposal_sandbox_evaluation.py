#!/usr/bin/env python3
"""Sole-writer for proposal sandbox evaluation packets (WP-D4-C3)."""

from __future__ import annotations

from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.proposal_sandbox_evaluation.runtime import run_proposal_sandbox_evaluation

_OUT_ROOT = Path("out")


if __name__ == "__main__":
    packet = run_proposal_sandbox_evaluation([], [], [], [])
    write_classified_json(
        "out/proposal_sandbox_evaluation/latest.json",
        packet,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/proposal_sandbox_evaluation_replay/latest.json",
        packet["replay"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/proposal_sandbox_evaluation_lineage/latest.json",
        packet["lineage"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/proposal_sandbox_evaluation_diagnostics/latest.json",
        packet["diagnostics"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )

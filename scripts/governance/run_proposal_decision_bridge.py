#!/usr/bin/env python3
"""Sole-writer for proposal decision bridge packets (WP-D4-C4)."""
from __future__ import annotations

from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.proposal_decision_bridge.runtime import run_proposal_decision_bridge

_OUT_ROOT = Path('out')
if __name__ == '__main__':
    packet = run_proposal_decision_bridge([], [], [], [])
    write_classified_json('out/proposal_decision_bridge/latest.json', packet, artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json('out/proposal_decision_bridge_replay/latest.json', packet['replay'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json('out/proposal_decision_bridge_lineage/latest.json', packet['lineage'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json('out/proposal_decision_bridge_diagnostics/latest.json', packet['diagnostics'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)

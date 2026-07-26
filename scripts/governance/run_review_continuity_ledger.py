#!/usr/bin/env python3
"""Sole-writer for review continuity packets (WP-D4-C4)."""
from __future__ import annotations

from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.review_continuity.runtime import run_review_continuity_ledger

_OUT_ROOT = Path('out')
if __name__ == '__main__':
    packet = run_review_continuity_ledger([], [], [], [], [])
    write_classified_json('out/review_continuity/latest.json', packet, artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json('out/review_continuity_replay/latest.json', packet['replay'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json('out/review_continuity_lineage/latest.json', packet['lineage'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)
    write_classified_json('out/review_continuity_diagnostics/latest.json', packet['diagnostics'], artifact_class=ArtifactClass.AUDIT_EVIDENCE, out_root=_OUT_ROOT)

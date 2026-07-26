from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.overlay_risk.runtime import run_overlay_risk_envelope

_OUT_ROOT = Path("out")


def _load(path: str) -> list[dict]:
    p = Path(path)
    return [json.loads(p.read_text())] if p.exists() else [{}]


if __name__ == "__main__":
    packet = run_overlay_risk_envelope(
        _load("out/overlay_governance/latest.json"),
        _load("out/overlay_observability/latest.json"),
        _load("out/canary_scheduler/latest.json"),
        _load("out/canary_promotion/latest.json"),
    )
    write_classified_json(
        "out/overlay_risk/latest.json",
        packet,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/overlay_risk_replay/latest.json",
        packet["replay"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/overlay_risk_lineage/latest.json",
        packet["lineage"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/overlay_risk_diagnostics/latest.json",
        packet["diagnostics"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )

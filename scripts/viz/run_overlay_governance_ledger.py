from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.overlay_governance.runtime import run_overlay_governance_ledger

_OUT_ROOT = Path("out")


def _load(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"required overlay governance upstream missing: {path} "
            "(refuse empty-packet fallback)"
        )
    payload = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"overlay governance upstream must be a JSON object: {path}")
    return [payload]


if __name__ == "__main__":
    packet = run_overlay_governance_ledger(
        _load("out/canary/latest.json"),
        _load("out/overlay_observability/latest.json"),
        _load("out/canary_scheduler/latest.json"),
        _load("out/canary_promotion/latest.json"),
    )
    write_classified_json(
        "out/overlay_governance/latest.json",
        packet,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/overlay_governance_replay/latest.json",
        packet["replay"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/overlay_governance_lineage/latest.json",
        packet["lineage"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/overlay_governance_diagnostics/latest.json",
        packet["diagnostics"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )

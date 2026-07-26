from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json
from core.drift.runtime import build_weight_drift_simulation

_OUT_ROOT = Path("out")


def main() -> None:
    reliability = json.loads(
        Path("out/brier_reliability/latest.json").read_text(encoding="utf-8")
    )
    brier = json.loads(Path("out/brier/latest.json").read_text(encoding="utf-8"))
    forecast = json.loads(Path("out/forecast/latest.json").read_text(encoding="utf-8"))
    out = build_weight_drift_simulation(reliability, brier, forecast)
    write_classified_json(
        Path("out/drift/latest.json"),
        out,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        Path("out/drift_lineage/latest.json"),
        out["lineage"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        Path("out/drift_reliability/latest.json"),
        out["reliability"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        Path("out/drift_replay/latest.json"),
        out["replay"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    print("drift artifacts emitted")


if __name__ == "__main__":
    main()

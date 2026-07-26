from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.canary_promotion.runtime import run_canary_promotion_review
from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json

_OUT_ROOT = Path("out")


def _load(p: str) -> list[dict]:
    path = Path(p)
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    return data if isinstance(data, list) else [data]


if __name__ == "__main__":
    packet = run_canary_promotion_review(
        _load("out/canary_scheduler/latest.json"),
        _load("out/overlay_observability/latest.json"),
    )
    write_classified_json(
        "out/canary_promotion/latest.json",
        packet,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/canary_promotion_replay/latest.json",
        packet["replay"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/canary_promotion_lineage/latest.json",
        packet["lineage"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    write_classified_json(
        "out/canary_promotion_review/latest.json",
        packet["operator_review"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    print("run_canary_promotion_review complete")

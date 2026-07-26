from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json

_OUT_ROOT = Path("out")


if __name__ == "__main__":
    src = Path("out/overlay_resolution/latest.json")
    packet = (
        json.loads(src.read_text()) if src.exists() else {"status": "not_computable"}
    )
    write_classified_json(
        "out/overlay_resolution_replay/latest.json",
        packet.get("replay", {"status": "not_computable"}),
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )

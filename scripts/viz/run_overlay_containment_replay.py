from __future__ import annotations

import json
from pathlib import Path

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json

_OUT_ROOT = Path("out")


if __name__ == "__main__":
    src = Path("out/overlay_containment/latest.json")
    packet = (
        json.loads(src.read_text()) if src.exists() else {"status": "not_computable"}
    )
    replay = packet.get("replay", {"status": "not_computable"})
    write_classified_json(
        "out/overlay_containment_replay/latest.json",
        replay,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )

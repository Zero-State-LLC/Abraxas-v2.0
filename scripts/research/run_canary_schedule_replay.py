from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import write_classified_json

_OUT_ROOT = Path("out")


if __name__ == "__main__":
    data = json.loads(Path("out/canary_scheduler/latest.json").read_text())
    write_classified_json(
        "out/canary_scheduler_replay/latest.json",
        data["replay"],
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        out_root=_OUT_ROOT,
    )
    print("run_canary_schedule_replay complete")

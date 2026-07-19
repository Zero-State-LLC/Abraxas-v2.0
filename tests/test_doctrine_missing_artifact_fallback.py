from __future__ import annotations

import json
import shutil
from pathlib import Path

from scripts.governance.run_doctrine_validator import main as run_doctrine


def test_missing_artifact_sets_not_computable() -> None:
    target = Path("out/human_decision_continuity/latest.json")
    backup = Path("out/human_decision_continuity/latest.json.bak")
    if target.exists():
        shutil.move(target, backup)
    try:
        run_doctrine()
        summary = json.loads(Path("out/validation/latest.json").read_text())["summary"]
        assert summary["human_decision_continuity_chain_gate"] in {
            "not_computable",
            "failed",
        }
    finally:
        if backup.exists():
            shutil.move(backup, target)
        run_doctrine()

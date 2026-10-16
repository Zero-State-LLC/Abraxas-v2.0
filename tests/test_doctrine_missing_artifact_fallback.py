from __future__ import annotations

import json
from pathlib import Path

from scripts.governance.run_doctrine_validator import main as run_doctrine
from tests._repo_mirror import make_repo_mirror


def test_missing_artifact_sets_not_computable(tmp_path, monkeypatch) -> None:
    # The validator reads and writes cwd-relative contracts/ and out/ paths, so
    # run it in a disposable mirror: never move or rewrite tracked artifacts.
    mirror = make_repo_mirror(tmp_path)
    monkeypatch.chdir(mirror)
    Path("out/human_decision_continuity/latest.json").unlink(missing_ok=True)

    run_doctrine()

    summary = json.loads(Path("out/validation/latest.json").read_text())["summary"]
    assert summary["human_decision_continuity_chain_gate"] in {
        "not_computable",
        "failed",
    }

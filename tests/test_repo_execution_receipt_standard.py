from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_repo_execution_receipt_runner_emits_spec_only_packet(tmp_path: Path) -> None:
    out_path = tmp_path / "out" / "execution_receipts" / "latest.json"
    script = Path("scripts/run_repo_execution_receipt.py")
    subprocess.run(
        [
            sys.executable,
            str(script),
            "--command-id",
            "BUILD_REPO_EXECUTION_RECEIPT_STANDARD_001",
            "--execution-state",
            "not_executed",
            "--command",
            "python scripts/run_repo_execution_receipt.py --help",
            "--pipeline-id",
            "global_pipeline_spine",
            "--repo-name",
            "Abraxas-v2.0",
            "--branch",
            "main",
            "--out",
            str(out_path),
        ],
        check=True,
    )
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "RepoExecutionReceipt.v1"
    assert payload["execution_state"] == "not_executed"
    assert payload["status"] == "spec_only"
    assert payload["files"] == {
        "added": [],
        "modified": [],
        "deleted": [],
        "renamed": [],
        "diff_hash": None,
    }
    assert payload["authority"]["promotion_allowed"] is False
    assert out_path.with_suffix(".md").exists()


def test_ci_execution_requires_ci_metadata() -> None:
    script = Path("scripts/run_repo_execution_receipt.py")
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--command-id",
            "CI_EXECUTION_TEST",
            "--execution-state",
            "ci_executed",
            "--command",
            "pytest -q",
            "--exit-code",
            "0",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "ci_executed state requires execution.ci_run_id or execution.ci_run_url" in result.stderr or result.stdout

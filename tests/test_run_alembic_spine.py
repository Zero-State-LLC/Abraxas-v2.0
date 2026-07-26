"""CLI tests for scripts/alembic/run_alembic_spine.py."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.alembic.run_alembic_spine import main

REPO = Path(__file__).resolve().parents[1]


def test_cli_validate_registry(tmp_path: Path) -> None:
    code = main([
        "validate-registry",
        "--out",
        str(tmp_path),
    ])
    assert code == 0
    assert (tmp_path / "registry_validation.json").exists()


def test_cli_execute_advisory(tmp_path: Path) -> None:
    code = main([
        "execute-advisory",
        "--task",
        str(REPO / "fixtures/alembic/example_task.json"),
        "--registry",
        str(REPO / "contracts/alembic/architecture_registry.json"),
        "--policy",
        str(REPO / "contracts/alembic/router_policy.json"),
        "--out",
        str(tmp_path / "run"),
    ])
    assert code == 0
    latest = json.loads((tmp_path / "run" / "latest.json").read_text(encoding="utf-8"))
    assert latest["FINAL_STATUS"] == "ALEMBIC_SPINE_ADVISORY_ONLY"
    assert latest["routing_decision"]["decision_id"]
    assert (tmp_path / "run" / "replay_manifest.json").exists()


def test_cli_evaluate(tmp_path: Path) -> None:
    code = main(["evaluate", "--out", str(tmp_path)])
    assert code == 0
    payload = json.loads((tmp_path / "evaluation_result.json").read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"

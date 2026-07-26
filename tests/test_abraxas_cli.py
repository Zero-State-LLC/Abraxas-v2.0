"""Tests for supported abraxas CLI and AbraxasClient."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from abraxas import AbraxasClient
from abraxas.cli import main
from core.alembic.config import default_router_policy
from core.alembic.models import TaskEnvelope
from core.alembic.pipeline import execute_advisory
from core.alembic.registry import default_registry

REPO = Path(__file__).resolve().parents[1]


def test_cli_status(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["status"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["candidate_status"] == "NOT_READY"
    assert payload["external_production_authorized"] is False
    assert "abraxas_cli" in payload["supported_interfaces"]


def test_cli_analyze_alembic_task_equivalence(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    task_path = REPO / "fixtures/alembic/example_task.json"
    task = json.loads(task_path.read_text(encoding="utf-8"))
    direct = execute_advisory(
        TaskEnvelope.model_validate(task),
        default_registry(),
        default_router_policy(),
        mode="advisory",
    )
    out = tmp_path / "analyze"
    code = main(
        [
            "analyze",
            "--run-id",
            "cli-analyze-001",
            "--alembic-task",
            str(task_path),
            "--out",
            str(out),
        ]
    )
    assert code == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["ok"] is True
    assert summary["alembic_invoked"] is True
    full = json.loads((out / "advisory_spine_result.json").read_text(encoding="utf-8"))
    assert (
        full["alembic"]["routing_decision"]["decision_id"]
        == direct["routing_decision"]["decision_id"]
    )


def test_cli_validate_alembic_task_schema(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(
        [
            "validate",
            "--schema-ref",
            "contracts/alembic/task_envelope.v1.schema.json",
            "--payload",
            str(REPO / "fixtures/alembic/example_task.json"),
        ]
    )
    summary = json.loads(capsys.readouterr().out)
    assert summary["status"] == "OK"
    assert summary["ok"] is True
    assert code == 0


def test_client_replay_roundtrip() -> None:
    client = AbraxasClient(repo_root=REPO)
    task = json.loads(
        (REPO / "fixtures/alembic/example_task.json").read_text(encoding="utf-8")
    )
    first = client.analyze(run_id="replay-src", alembic_task=task)
    assert first["status"] == "OK"
    second = client.replay(first)
    assert second["status"] == "OK"
    assert (
        second["alembic"]["routing_decision"]["decision_id"]
        == first["alembic"]["routing_decision"]["decision_id"]
    )


def test_cli_replay(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    client = AbraxasClient(repo_root=REPO)
    task = json.loads(
        (REPO / "fixtures/alembic/example_task.json").read_text(encoding="utf-8")
    )
    first = client.analyze(run_id="cli-replay-src", alembic_task=task)
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps(first), encoding="utf-8")
    code = main(["replay", "--receipt", str(receipt), "--out", str(tmp_path / "out")])
    assert code == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["ok"] is True

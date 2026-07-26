"""Golden-path integration tests for advisory spine + Alembic fit."""

from __future__ import annotations

import json
from pathlib import Path

from core.alembic.config import default_router_policy
from core.alembic.models import TaskEnvelope
from core.alembic.pipeline import execute_advisory
from core.alembic.registry import default_registry
from core.application.advisory_spine import run_advisory_spine
from core.canonical.json import canonical_hash

REPO = Path(__file__).resolve().parents[1]


def _example_task() -> dict:
    task = json.loads(
        (REPO / "fixtures/alembic/example_task.json").read_text(encoding="utf-8")
    )
    task["run_id"] = "golden-path-integration-001"
    return task


def test_golden_path_alembic_decision_matches_direct_pipeline() -> None:
    task = _example_task()
    direct = execute_advisory(
        TaskEnvelope.model_validate(task),
        default_registry(),
        default_router_policy(),
        mode="advisory",
    )
    spine = run_advisory_spine(
        {
            "run_id": task["run_id"],
            "activation_lane": "LOCAL_DEV",
            "input_payload": {"goal": task["goal"]},
            "alembic_task": task,
            "enable_alembic": True,
        }
    )
    assert spine["status"] == "OK"
    assert spine["advisory_result"]["lane"] == "SHADOW"
    assert spine["advisory_result"]["forecast_influence"] is False
    assert spine["authority_locks"]["shadow_to_forecast_escalation_allowed"] is False
    assert spine["influences_current_state"] is False
    assert (
        spine["alembic"]["routing_decision"]["decision_id"]
        == direct["routing_decision"]["decision_id"]
    )
    assert spine["result_hash"] == canonical_hash(
        {k: v for k, v in spine.items() if k != "result_hash"}
    )


def test_golden_path_rejects_forecast_lane_task() -> None:
    task = _example_task()
    task["lane"] = "FORECAST"
    result = run_advisory_spine(
        {
            "run_id": "forecast-denied",
            "alembic_task": task,
            "enable_alembic": True,
        }
    )
    assert result["status"] == "DENIED"
    assert result["error_class"] == "SHADOW_FORECAST_ESCALATION_DENIED"


def test_golden_path_without_alembic_still_ok() -> None:
    result = run_advisory_spine(
        {
            "run_id": "no-alembic",
            "input_payload": {"note": "spine-only"},
            "enable_alembic": False,
        }
    )
    assert result["status"] == "OK"
    assert result["alembic"] is None
    assert result["advisory_result"]["alembic_invoked"] is False

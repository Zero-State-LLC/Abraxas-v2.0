from __future__ import annotations

import pytest

from core.forecast.runtime import (
    resolve_observability_telemetry_hash,
    run_forecast_candidates,
)


def _oracle() -> dict:
    return {"intake": {"source_hash": "srcA"}}


def _sandbox() -> dict:
    return {"branch": {"sandbox_state_hash": "sandA"}}


def test_nested_projection_snapshot_telemetry_hash_is_used() -> None:
    obs = {
        "schema_version": "ObservabilityAggregation.v1",
        "telemetry": {"executed_node_count": 1},
        "projection_snapshot": {"telemetry_hash": "tele-nested-1"},
    }
    assert resolve_observability_telemetry_hash(obs) == "tele-nested-1"
    packet = run_forecast_candidates(_oracle(), _sandbox(), obs)
    assert "unknown" not in packet["candidate"]["candidate_hash"]


def test_distinct_nested_telemetry_produces_distinct_candidate_hashes() -> None:
    obs1 = {
        "telemetry": {"executed_node_count": 1},
        "projection_snapshot": {"telemetry_hash": "tele-1"},
    }
    obs2 = {
        "telemetry": {"executed_node_count": 2},
        "projection_snapshot": {"telemetry_hash": "tele-2"},
    }
    h1 = run_forecast_candidates(_oracle(), _sandbox(), obs1)["candidate"][
        "candidate_hash"
    ]
    h2 = run_forecast_candidates(_oracle(), _sandbox(), obs2)["candidate"][
        "candidate_hash"
    ]
    assert h1 != h2


def test_missing_telemetry_hash_fails_closed() -> None:
    with pytest.raises(ValueError, match="refuse unknown fallback"):
        run_forecast_candidates(_oracle(), _sandbox(), {})


def test_literal_unknown_telemetry_hash_fails_closed() -> None:
    with pytest.raises(ValueError, match="refuse unknown fallback"):
        resolve_observability_telemetry_hash({"telemetry_hash": "unknown"})


def test_forecast_writer_reads_official_observability_path() -> None:
    source = (
        __import__("pathlib").Path("scripts/research/run_forecast_candidates.py")
        .read_text(encoding="utf-8")
    )
    assert "out/observability/latest.json" in source
    assert "out/run_observability_pipeline/latest.json" not in source

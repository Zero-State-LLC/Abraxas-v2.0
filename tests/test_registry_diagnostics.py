from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from core.diagnostics import stable_correlation_id
from scripts.readiness.run_registry import CONTRACTS_DIR, OUT_PATH, main


def test_registry_events_share_stable_correlation_id(
    capsys: pytest.CaptureFixture[str],
) -> None:
    registry = {
        "status": "ok",
        "pipeline_count": 2,
        "recommended_next_state": "seal",
    }

    with (
        patch("scripts.readiness.run_registry.load_contracts", return_value=[object(), object()]),
        patch("scripts.readiness.run_registry.build_registry", return_value=registry),
        patch("scripts.readiness.run_registry.write_canonical_json"),
    ):
        main()

    events = [json.loads(line) for line in capsys.readouterr().out.strip().splitlines()]
    correlation_id = stable_correlation_id(
        "registry_generation",
        artifact_path=OUT_PATH,
        context={"contracts_dir": CONTRACTS_DIR.as_posix()},
    )

    assert [event["event"] for event in events] == [
        "registry_generation_started",
        "registry_generation_completed",
    ]
    assert all(event["correlation_id"] == correlation_id for event in events)
    assert events[1]["artifact_path"] == OUT_PATH.as_posix()

"""Focused tests for runtime profiling script integration."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from core.config import RuntimePaths
from core.performance import PROFILE_ENV_FLAG
from scripts import run_registry


def test_registry_output_unchanged_when_runtime_profiling_disabled(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv(PROFILE_ENV_FLAG, raising=False)

    runtime_paths = RuntimePaths(contracts_dir=Path("contracts"), out_dir=tmp_path / "out")
    registry_path = runtime_paths.registry_latest
    profile_path = runtime_paths.runtime_performance_profile_latest
    registry_payload = {
        "pipeline_count": 1,
        "recommended_next_state": "hold",
        "status": "ok",
    }

    with (
        patch.object(run_registry, "_PATHS", runtime_paths),
        patch.object(run_registry, "OUT_PATH", registry_path),
        patch.object(run_registry, "CONTRACTS_DIR", Path("contracts/pipelines")),
        patch.object(run_registry, "load_contracts", return_value=[object()]),
        patch.object(run_registry, "build_registry", return_value=registry_payload),
        patch.object(run_registry, "write_canonical_json") as mock_write,
    ):
        run_registry.main()

    assert mock_write.call_count == 1
    written_path, payload = mock_write.call_args.args
    assert Path(written_path) == registry_path
    assert payload == registry_payload
    assert not profile_path.exists()

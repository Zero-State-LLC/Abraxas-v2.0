from __future__ import annotations

from core.config import RuntimePaths
from core.temporal_state_diff import _surface_paths_from_runtime_paths


def test_temporal_state_diff_uses_runtime_live_projection_refresh_path() -> None:
    paths = RuntimePaths.from_env()
    surfaces = _surface_paths_from_runtime_paths(paths)
    assert surfaces["live_projection_refresh"].as_posix() == paths.live_projection_refresh_latest.as_posix()

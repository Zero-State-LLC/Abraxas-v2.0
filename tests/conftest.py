from __future__ import annotations

from pathlib import Path

import pytest

SLOW_KEYWORDS = (
    "temporal",
    "governance",
    "audit",
    "registry",
    "release",
    "archive",
    "artifact",
    "projection",
    "operator_narrative",
)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        path_text = str(Path(item.fspath)).lower()
        if any(keyword in path_text for keyword in SLOW_KEYWORDS):
            item.add_marker(pytest.mark.slow)
        if "integration" in path_text:
            item.add_marker(pytest.mark.integration)
        if "temporal_continuity" in path_text or "canon" in path_text:
            item.add_marker(pytest.mark.canon)
        if "artifact" in path_text or "archive" in path_text or "registry" in path_text:
            item.add_marker(pytest.mark.artifact)
        if "security" in path_text or "audit" in path_text:
            item.add_marker(pytest.mark.security)

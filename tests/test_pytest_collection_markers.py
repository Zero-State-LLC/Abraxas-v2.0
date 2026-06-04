from __future__ import annotations

from pathlib import Path

from tests.conftest import REPO_ROOT, _normalized_collection_path, pytest_collection_modifyitems


class _FakeItem:
    def __init__(self, fspath: Path) -> None:
        self.fspath = fspath
        self.markers: list[str] = []

    def add_marker(self, marker: object) -> None:
        name = getattr(marker, "name", str(marker))
        self.markers.append(str(name))


def test_normalized_collection_path_ignores_worktree_name() -> None:
    item = _FakeItem(REPO_ROOT / "tests/test_api.py")
    assert _normalized_collection_path(item) == "tests/test_api.py"


def test_marker_assignment_uses_repo_relative_path() -> None:
    api_item = _FakeItem(REPO_ROOT / "tests/test_api.py")
    audit_item = _FakeItem(REPO_ROOT / "tests/test_operator_narrative_report_governance_audit.py")

    pytest_collection_modifyitems([api_item, audit_item])

    assert "slow" not in api_item.markers
    assert "security" not in api_item.markers
    assert "artifact" not in api_item.markers

    assert "slow" in audit_item.markers
    assert "security" in audit_item.markers

"""Collection policy: markers are explicit; known failures are strict xfails."""

from __future__ import annotations

from pathlib import Path

from tests.conftest import REPO_ROOT, load_known_failures, pytest_collection_modifyitems


class _FakeItem:
    def __init__(self, nodeid: str) -> None:
        self.nodeid = nodeid
        self.fspath = REPO_ROOT / nodeid.split("::")[0]
        self.markers: list[object] = []

    def add_marker(self, marker: object) -> None:
        self.markers.append(marker)


def test_path_words_never_produce_markers() -> None:
    # These names used to be deselected from fast CI by path substring.
    names = [
        "tests/test_operator_narrative_report_governance_audit.py::test_x",
        "tests/test_artifact_registry_classifier.py::test_x",
        "tests/test_temporal_continuity_index_contract.py::test_x",
    ]
    items = [_FakeItem(n) for n in names if n not in load_known_failures()]
    pytest_collection_modifyitems(items)
    assert all(item.markers == [] for item in items)


def test_known_failures_become_strict_xfails() -> None:
    known = load_known_failures()
    if not known:
        return
    nodeid = next(iter(known))
    item = _FakeItem(nodeid)
    pytest_collection_modifyitems([item])
    (marker,) = item.markers
    assert marker.name == "xfail"
    assert marker.kwargs["strict"] is True
    assert known[nodeid]["cause"] in marker.kwargs["reason"]


def test_known_failure_entries_are_well_formed() -> None:
    for nodeid, entry in load_known_failures().items():
        assert (REPO_ROOT / nodeid.split("::")[0]).is_file(), nodeid
        assert entry["cause"].strip(), nodeid
        assert entry["phase"] in {"P0", "P1", "P2", "P3", "P4"}, nodeid


def test_fast_ci_selects_on_explicit_markers_only() -> None:
    source = Path(REPO_ROOT / "scripts" / "run_fast_ci.py").read_text(encoding="utf-8")
    assert '"not slow and not integration"' in source
    assert "not canon" not in source and "not artifact" not in source

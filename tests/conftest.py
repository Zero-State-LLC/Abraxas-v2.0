from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

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


def _normalized_collection_path(item: pytest.Item) -> str:
    item_path = Path(str(item.fspath)).resolve()
    try:
        relative = item_path.relative_to(REPO_ROOT)
    except ValueError:
        relative = item_path
    return str(relative).lower()


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        path_text = _normalized_collection_path(item)
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


PRE_REPAIR_COVERAGE_AUDIT_FIXTURE = (
    REPO_ROOT
    / "tests/fixtures/abx_research_canary_artifact_registry_coverage_audit_001_pre_repair.latest.json"
)


def bootstrap_pre_repair_coverage_audit(tmp_path: Path) -> None:
    target = tmp_path / "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(PRE_REPAIR_COVERAGE_AUDIT_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")


def bootstrap_pre_repair_phase_receipt_chain(tmp_path: Path) -> None:
    from core.abx_research_canary_artifact_registry_coverage_repair_operator_decision_request import (
        write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_request,
    )
    from core.abx_research_canary_artifact_registry_coverage_repair_spec_plan import (
        write_abx_research_canary_artifact_registry_coverage_repair_spec_plan,
    )

    bootstrap_pre_repair_coverage_audit(tmp_path)
    write_abx_research_canary_artifact_registry_coverage_repair_spec_plan(
        source_root=tmp_path,
        out_root=tmp_path,
    )
    write_abx_research_canary_artifact_registry_coverage_repair_operator_decision_request(
        source_root=tmp_path,
        out_root=tmp_path,
    )

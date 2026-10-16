from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from importlib import import_module
from pathlib import Path

import pytest

sys.modules.setdefault("Scripts", import_module("scripts"))

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def bootstrap_legacy_fast_ci_artifacts() -> None:
    from tests.legacy_artifact_bootstrap import (
        seed_abx_skill_evolution_artifacts,
        seed_engineering_oracle_artifacts,
    )

    seed_abx_skill_evolution_artifacts(REPO_ROOT)
    seed_engineering_oracle_artifacts(REPO_ROOT)

KNOWN_FAILURES_PATH = REPO_ROOT / "tests" / "known_failures.json"
# Tracked files the test session must leave byte-identical (see
# docs/architecture/ARCHITECTURE_COHERENCE_AUDIT_001.md, P0).
GUARDED_TRACKED_PREFIXES = ("out/", "apps/aal-viz-live-console/public/")


def load_known_failures() -> dict[str, dict[str, str]]:
    """Pre-existing failures, each reported as a strict xfail with its cause."""
    if not KNOWN_FAILURES_PATH.is_file():
        return {}
    data = json.loads(KNOWN_FAILURES_PATH.read_text(encoding="utf-8"))
    return {entry["nodeid"]: entry for entry in data["entries"]}


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Markers are explicit in test files; this only applies the registry.

    No marker is derived from path words: fast CI used to deselect every test
    whose path mentioned governance, audit, registry, artifact and similar.
    """
    known = load_known_failures()
    for item in items:
        entry = known.get(item.nodeid)
        if entry is not None:
            item.add_marker(
                pytest.mark.xfail(
                    reason=f"known pre-existing failure ({entry['phase']}): {entry['cause']}",
                    strict=True,
                )
            )


def _tracked_state() -> dict[str, str] | None:
    """Content hashes of guarded tracked files that differ from HEAD."""
    try:
        status = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "status", "--porcelain", "-z", "--untracked-files=no"],
            capture_output=True,
            check=True,
        ).stdout.decode("utf-8", "replace")
    except (OSError, subprocess.CalledProcessError):
        return None
    state: dict[str, str] = {}
    for record in filter(None, status.split("\0")):
        path = record[3:]
        if not path.startswith(GUARDED_TRACKED_PREFIXES):
            continue
        target = REPO_ROOT / path
        state[path] = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else "DELETED"
    return state


def pytest_sessionstart(session: pytest.Session) -> None:
    session.config._abraxas_tracked_before = _tracked_state()  # type: ignore[attr-defined]


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    before = getattr(session.config, "_abraxas_tracked_before", None)
    after = _tracked_state()
    if before is None or after is None:
        return
    changed = sorted(p for p in set(before) | set(after) if before.get(p) != after.get(p))
    if not changed:
        return
    session.config._abraxas_tracked_changes = changed  # type: ignore[attr-defined]
    session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:  # noqa: ANN001
    changed = getattr(config, "_abraxas_tracked_changes", None)
    if changed:
        terminalreporter.section("tracked files modified by the test session", red=True)
        for path in changed:
            terminalreporter.write_line(path)
        terminalreporter.write_line(
            "Tests must write to tmp_path or an injected output root, never to tracked out/ files."
        )


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

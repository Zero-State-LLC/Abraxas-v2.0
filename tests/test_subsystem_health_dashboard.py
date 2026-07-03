from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.subsystem_health_dashboard import (
    ALIAS_IMPLEMENTATION_DESIGN_RECEIPT_PATH,
    ARTIFACT_CLASSIFIER_RECEIPT_PATH,
    AUTHORITY_LOCKS,
    DEFAULT_OUT_PATH,
    MIGRATION_RUNNER_RECEIPT_PATH,
    OWNERSHIP_RECEIPT_PATH,
    STATUS,
    build_subsystem_health_dashboard_markdown,
    build_subsystem_health_dashboard_receipt,
    write_subsystem_health_dashboard_receipt,
)
from Scripts.run_subsystem_health_dashboard_receipt import run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_subsystem_health_dashboard_receipt_contains_expected_sections() -> None:
    packet = build_subsystem_health_dashboard_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert packet["source_status"] == "READY_WITH_FINDINGS"
    assert packet["ownership_coverage_posture"]["subsystem_count"] >= 10
    assert packet["artifact_lifecycle_posture"]["managed_count"] > 0
    assert packet["continuity_health_posture"]["highest_observed_lane"] == "P102G"
    assert (
        packet["migration_runner_posture"]["status"]
        == "CONTINUITY_NAMESPACE_MIGRATION_RUNNER_READY_ADVISORY_ONLY"
    )
    assert packet["migration_runner_posture"]["requested_execution_result"] == "READY"
    assert (
        packet["migration_runner_posture"]["safe_next_surface"]
        == "CONTINUITY_NAMESPACE_ADDITIVE_ALIAS_PLAN_001_ADVISORY_ONLY"
    )
    assert packet["migration_runner_posture"]["stage_count"] == 7
    assert (
        packet["alias_implementation_design_posture"]["status"]
        == "CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN_READY_ADVISORY_ONLY"
    )
    assert (
        packet["alias_implementation_design_posture"]["implementation_state"]
        == "DESIGN_ONLY_HELD"
    )
    assert packet["alias_implementation_design_posture"]["valid_for_implementation"] is False
    assert (
        packet["recommended_next_lane"]
        == "Hold continuity namespace alias lane at design-only posture"
    )
    active_paths = {
        row["artifact_path"] for row in packet["active_receipt_routes"] if row["observed"]
    }
    assert MIGRATION_RUNNER_RECEIPT_PATH in active_paths
    assert ALIAS_IMPLEMENTATION_DESIGN_RECEIPT_PATH in active_paths
    observed_subsystems = {
        row["subsystem"] for row in packet["subsystem_overview_rows"]
    }
    assert "AAL-Viz" in observed_subsystems
    assert "Oracle Signal Layer" in observed_subsystems


def test_subsystem_health_dashboard_authority_locks_false() -> None:
    packet = build_subsystem_health_dashboard_receipt(repo_root=REPO_ROOT)

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False
    assert packet["boundary"]["runtime_activation"] is False
    assert packet["boundary"]["canon_mutation"] is False
    assert packet["boundary"]["notion_writeback"] is False


def test_subsystem_health_dashboard_canonical_hash_stable() -> None:
    packet = build_subsystem_health_dashboard_receipt(repo_root=REPO_ROOT)
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    assert observed == canonical_hash(without_hash)
    assert (
        build_subsystem_health_dashboard_receipt(repo_root=REPO_ROOT)["canonical_hash"]
        == observed
    )


def test_subsystem_health_dashboard_runner_writes_receipt(tmp_path: Path) -> None:
    target = tmp_path / "subsystem_health_dashboard_001.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=target)

    assert target.exists()
    assert packet["canonical_hash"]
    assert packet["status"] == STATUS


def test_subsystem_health_dashboard_writer_preserves_hash(tmp_path: Path) -> None:
    target = tmp_path / "receipt.json"
    packet = build_subsystem_health_dashboard_receipt(repo_root=REPO_ROOT)
    write_subsystem_health_dashboard_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert DEFAULT_OUT_PATH in packet["validation_plan"][1]


def test_subsystem_health_dashboard_markdown_includes_key_routes() -> None:
    markdown = build_subsystem_health_dashboard_markdown(repo_root=REPO_ROOT)

    assert "# Subsystem Health Dashboard" in markdown
    assert OWNERSHIP_RECEIPT_PATH in markdown
    assert ARTIFACT_CLASSIFIER_RECEIPT_PATH not in markdown
    assert "AAL-Viz" in markdown
    assert "P102G" in markdown
    assert "## Continuity Namespace Migration Runner Posture" in markdown
    assert "## Continuity Namespace Alias Implementation Design Posture" in markdown
    assert "CONTINUITY_NAMESPACE_MIGRATION_RUNNER_READY_ADVISORY_ONLY" in markdown
    assert "CONTINUITY_NAMESPACE_ALIAS_IMPLEMENTATION_DESIGN_READY_ADVISORY_ONLY" in markdown


def test_subsystem_health_dashboard_fails_closed_when_classifier_missing(
    monkeypatch,
) -> None:
    import core.subsystem_health_dashboard as module

    real_load_json = module._load_json

    def _patched(path: Path):
        if path == REPO_ROOT / ARTIFACT_CLASSIFIER_RECEIPT_PATH:
            return {}, "MISSING"
        return real_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    packet = module.build_subsystem_health_dashboard_receipt(repo_root=REPO_ROOT)

    assert packet["artifact_lifecycle_posture"]["source_status"] == "MISSING"
    assert packet["artifact_lifecycle_posture"]["managed_count"] == 0
    assert packet["source_status"] == "READY_WITH_FINDINGS"


def test_subsystem_health_dashboard_fails_closed_when_migration_runner_missing(
    monkeypatch,
) -> None:
    import core.subsystem_health_dashboard as module

    real_load_json = module._load_json

    def _patched(path: Path):
        if path == REPO_ROOT / MIGRATION_RUNNER_RECEIPT_PATH:
            return {}, "MISSING"
        return real_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    packet = module.build_subsystem_health_dashboard_receipt(repo_root=REPO_ROOT)

    assert packet["migration_runner_posture"]["source_status"] == "MISSING"
    assert packet["migration_runner_posture"]["status"] == "NOT_COMPUTABLE"
    assert packet["migration_runner_posture"]["stage_count"] == 0
    assert packet["source_status"] == "READY_WITH_FINDINGS"


def test_subsystem_health_dashboard_fails_closed_when_alias_design_missing(
    monkeypatch,
) -> None:
    import core.subsystem_health_dashboard as module

    real_load_json = module._load_json

    def _patched(path: Path):
        if path == REPO_ROOT / ALIAS_IMPLEMENTATION_DESIGN_RECEIPT_PATH:
            return {}, "MISSING"
        return real_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    packet = module.build_subsystem_health_dashboard_receipt(repo_root=REPO_ROOT)

    assert packet["alias_implementation_design_posture"]["source_status"] == "MISSING"
    assert packet["alias_implementation_design_posture"]["status"] == "NOT_COMPUTABLE"
    assert packet["alias_implementation_design_posture"]["valid_for_implementation"] is False
    assert packet["source_status"] == "READY_WITH_FINDINGS"

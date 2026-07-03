from __future__ import annotations

from pathlib import Path

from core.canonical.json import canonical_hash
from core.live_projection_health_migration_artifact import (
    ARTIFACT_CLASSIFIER_RECEIPT_PATH,
    AUTHORITY_LOCKS,
    DEFAULT_OUT_PATH,
    MIGRATION_RUNNER_RECEIPT_PATH,
    STATUS,
    SUBSYSTEM_HEALTH_RECEIPT_PATH,
    build_combined_health_migration_artifact_posture,
    build_live_projection_health_migration_artifact_receipt,
    write_live_projection_health_migration_artifact_receipt,
)
from Scripts.run_live_projection_health_migration_artifact_receipt import run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_combined_posture_contains_expected_sections() -> None:
    posture, observed_sources = build_combined_health_migration_artifact_posture(
        repo_root=REPO_ROOT
    )

    assert posture["status"] == "READY_WITH_FINDINGS"
    assert posture["health_status"] == "SUBSYSTEM_HEALTH_DASHBOARD_READY_ADVISORY_ONLY"
    assert (
        posture["migration_runner_status"]
        == "CONTINUITY_NAMESPACE_MIGRATION_RUNNER_READY_ADVISORY_ONLY"
    )
    assert posture["artifact_lifecycle_status"] == "ADVISORY_ONLY"
    assert posture["managed_artifact_count"] > 0
    assert posture["findings_by_source"]["health"]
    assert posture["findings_by_source"]["migration"]
    assert posture["findings_by_source"]["artifact"]
    assert SUBSYSTEM_HEALTH_RECEIPT_PATH in observed_sources
    assert MIGRATION_RUNNER_RECEIPT_PATH in observed_sources
    assert ARTIFACT_CLASSIFIER_RECEIPT_PATH in observed_sources


def test_combined_receipt_contains_expected_sections() -> None:
    packet = build_live_projection_health_migration_artifact_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert packet["combined_posture_summary"]["posture"]["authority_granted"] is False
    assert packet["combined_posture_summary"]["posture"]["safe_next_surface"]
    assert packet["combined_posture_summary"]["posture"]["findings_by_source"]["artifact"]


def test_combined_receipt_authority_locks_false() -> None:
    packet = build_live_projection_health_migration_artifact_receipt(repo_root=REPO_ROOT)

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False


def test_combined_receipt_canonical_hash_stable() -> None:
    packet = build_live_projection_health_migration_artifact_receipt(repo_root=REPO_ROOT)
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    assert observed == canonical_hash(without_hash)
    assert (
        build_live_projection_health_migration_artifact_receipt(repo_root=REPO_ROOT)[
            "canonical_hash"
        ]
        == observed
    )


def test_combined_receipt_runner_writes_receipt(tmp_path: Path) -> None:
    target = tmp_path / "live_projection_health_migration_artifact_001.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=target)

    assert target.exists()
    assert packet["status"] == STATUS
    assert packet["canonical_hash"]


def test_combined_receipt_writer_preserves_hash(tmp_path: Path) -> None:
    target = tmp_path / "receipt.json"
    packet = build_live_projection_health_migration_artifact_receipt(repo_root=REPO_ROOT)
    write_live_projection_health_migration_artifact_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert DEFAULT_OUT_PATH in packet["validation_plan"][2]


def test_combined_posture_fails_closed_when_dashboard_missing(monkeypatch) -> None:
    import core.live_projection_health_migration_artifact as module

    real_load_json = module._load_json

    def _patched(path: Path):
        if path == REPO_ROOT / module.SUBSYSTEM_HEALTH_RECEIPT_PATH:
            return {}, "MISSING"
        return real_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    posture, _ = module.build_combined_health_migration_artifact_posture(
        repo_root=REPO_ROOT
    )

    assert posture["source_status"] == "MISSING"
    assert posture["status"] == "NOT_COMPUTABLE"
    assert posture["health_status"] == "MISSING"


def test_combined_posture_fails_closed_when_runner_missing(monkeypatch) -> None:
    import core.live_projection_health_migration_artifact as module

    real_load_json = module._load_json

    def _patched(path: Path):
        if path == REPO_ROOT / module.MIGRATION_RUNNER_RECEIPT_PATH:
            return {}, "MISSING"
        return real_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    posture, _ = module.build_combined_health_migration_artifact_posture(
        repo_root=REPO_ROOT
    )

    assert posture["source_status"] == "MISSING"
    assert posture["findings_by_source"]["migration"][0]["code"] == "MIGRATION_RUNNER_MISSING"


def test_combined_posture_fails_closed_when_classifier_missing(monkeypatch) -> None:
    import core.live_projection_health_migration_artifact as module

    real_load_json = module._load_json

    def _patched(path: Path):
        if path == REPO_ROOT / module.ARTIFACT_CLASSIFIER_RECEIPT_PATH:
            return {}, "MISSING"
        return real_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    posture, _ = module.build_combined_health_migration_artifact_posture(
        repo_root=REPO_ROOT
    )

    assert posture["source_status"] == "MISSING"
    assert posture["artifact_lifecycle_status"] == "ADVISORY_ONLY"

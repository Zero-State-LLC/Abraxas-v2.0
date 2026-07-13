from __future__ import annotations

from pathlib import Path

from core.artifact_registry_classifier import (
    ACTIVE_ROUTE_ARTIFACTS,
    AUTHORITY_LOCKS,
    DEFAULT_OUT_PATH,
    STATUS,
    build_artifact_registry_classifier_receipt,
    write_artifact_registry_classifier_receipt,
)
from scripts.artifact.run_artifact_registry_classifier_receipt import run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_artifact_registry_classifier_receipt_contains_expected_routes() -> None:
    packet = build_artifact_registry_classifier_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert packet["classification_summary"]["total_entries"] > 0
    assert packet["classification_summary"]["managed_count"] > 0
    observed_paths = {
        row["artifact_path"] for row in packet["active_route_rows"] if row["observed"]
    }
    assert {
        "out/audit/docs_navigation_refresh_001.latest.json",
        "out/audit/subsystem_ownership_matrix_refresh_001.latest.json",
    }.issubset(observed_paths)
    assert observed_paths.issubset(set(ACTIVE_ROUTE_ARTIFACTS))


def test_artifact_registry_classifier_authority_locks_false() -> None:
    packet = build_artifact_registry_classifier_receipt(repo_root=REPO_ROOT)

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False
    assert packet["boundary"]["runtime_activation"] is False
    assert packet["boundary"]["canon_mutation"] is False
    assert packet["boundary"]["notion_writeback"] is False


def test_artifact_registry_classifier_canonical_hash_stable() -> None:
    packet = build_artifact_registry_classifier_receipt(repo_root=REPO_ROOT)
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    from core.canonical.json import canonical_hash

    assert observed == canonical_hash(without_hash)
    assert (
        build_artifact_registry_classifier_receipt(repo_root=REPO_ROOT)["canonical_hash"]
        == observed
    )


def test_artifact_registry_classifier_runner_writes_receipt(tmp_path: Path) -> None:
    target = tmp_path / "artifact_registry_classifier_001.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=target)

    assert target.exists()
    assert packet["canonical_hash"]
    assert packet["status"] == STATUS


def test_artifact_registry_classifier_writer_preserves_hash(tmp_path: Path) -> None:
    target = tmp_path / "receipt.json"
    packet = build_artifact_registry_classifier_receipt(repo_root=REPO_ROOT)
    write_artifact_registry_classifier_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert DEFAULT_OUT_PATH in packet["validation_plan"][1]


def test_artifact_registry_classifier_fails_closed_when_registry_breaks(monkeypatch) -> None:
    import core.artifact_registry_classifier as module

    def _boom(repo_root: Path) -> None:
        raise RuntimeError("registry unavailable")

    monkeypatch.setattr(module, "build_generated_artifact_registry", _boom)
    packet = module.build_artifact_registry_classifier_receipt(repo_root=REPO_ROOT)

    assert packet["source_status"] == "NOT_COMPUTABLE"
    assert packet["classification_summary"]["total_entries"] == 0
    assert packet["top_findings"][0]["code"] == "REGISTRY_BUILD_FAILED"

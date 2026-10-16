from __future__ import annotations

import importlib.util
from pathlib import Path

from core.canonical.json import canonical_hash
from core.live_console_migration_preflight_projection import (
    AUTHORITY_LOCKS,
    DEFAULT_OUT_PATH,
    PREFLIGHT_RECEIPT_PATH,
    PROJECTION_BUNDLE_PATH,
    STATUS,
    build_live_console_migration_preflight_projection_receipt,
    write_live_console_migration_preflight_projection_receipt,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = (
    REPO_ROOT / "scripts" / "viz" / "run_live_console_migration_preflight_projection_receipt.py"
)


def _load_runner_run():
    spec = importlib.util.spec_from_file_location(
        "run_live_console_migration_preflight_projection_receipt",
        RUNNER_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run


def test_live_console_migration_preflight_projection_receipt_contains_expected_sections() -> None:
    packet = build_live_console_migration_preflight_projection_receipt(
        repo_root=REPO_ROOT
    )

    assert packet["status"] == STATUS
    assert packet["brier_score"] == "0.10"
    assert packet["canonical_source_path"] == PREFLIGHT_RECEIPT_PATH
    assert packet["projection_bundle_path"] == PROJECTION_BUNDLE_PATH
    summary = packet["migration_preflight_projection_summary"]
    assert summary["live_visibility_ready"] is True
    assert (
        summary["preflight_summary"]["status"]
        == "CONTINUITY_NAMESPACE_MIGRATION_PREFLIGHT_READY_ADVISORY_ONLY"
    )
    assert summary["bundle_projection"]["pass_count"] == 12
    assert summary["bundle_projection"]["authority_granted"] is False


def test_live_console_migration_preflight_projection_authority_locks_false() -> None:
    packet = build_live_console_migration_preflight_projection_receipt(
        repo_root=REPO_ROOT
    )

    assert packet["authority_locks"] == AUTHORITY_LOCKS
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["runtime_activation"] is False
    assert packet["boundary"]["scheduler_mutation"] is False


def test_live_console_migration_preflight_projection_canonical_hash_stable() -> None:
    packet = build_live_console_migration_preflight_projection_receipt(
        repo_root=REPO_ROOT
    )
    without_hash = dict(packet)
    observed = without_hash.pop("canonical_hash")

    assert observed == canonical_hash(without_hash)
    assert (
        build_live_console_migration_preflight_projection_receipt(repo_root=REPO_ROOT)[
            "canonical_hash"
        ]
        == observed
    )


def test_live_console_migration_preflight_projection_runner_writes_receipt(
    tmp_path: Path,
) -> None:
    target = tmp_path / "live_console_migration_preflight_projection_001.latest.json"
    run = _load_runner_run()
    packet = run(repo_root=REPO_ROOT, out_path=target)

    assert target.exists()
    assert packet["canonical_hash"]
    assert packet["status"] == STATUS


def test_live_console_migration_preflight_projection_writer_preserves_hash(
    tmp_path: Path,
) -> None:
    target = tmp_path / "receipt.json"
    packet = build_live_console_migration_preflight_projection_receipt(
        repo_root=REPO_ROOT
    )
    write_live_console_migration_preflight_projection_receipt(target, packet)

    text = target.read_text(encoding="utf-8")
    assert packet["canonical_hash"] in text
    assert DEFAULT_OUT_PATH in packet["validation_plan"][2]


def test_live_console_migration_preflight_projection_fails_closed_when_preflight_missing(
    monkeypatch,
) -> None:
    import core.live_console_migration_preflight_projection as module

    real_load_json = module._load_json

    def _patched(path: Path):
        if path == REPO_ROOT / PREFLIGHT_RECEIPT_PATH:
            return {}, "MISSING"
        return real_load_json(path)

    monkeypatch.setattr(module, "_load_json", _patched)
    packet = module.build_live_console_migration_preflight_projection_receipt(
        repo_root=REPO_ROOT
    )

    summary = packet["migration_preflight_projection_summary"]
    assert summary["preflight_summary"]["source_status"] == "MISSING"
    assert summary["live_visibility_ready"] is False

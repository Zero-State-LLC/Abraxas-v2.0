"""Tests for clock/storage ports and RuntimeContext."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from abraxas.client import AbraxasClient
from core.canonical.artifact_classification import ArtifactClass
from core.canonical.json import CanonicalWriteError
from core.ports.clock import FixedClock, SystemClock
from core.ports.storage import FilesystemArtifactStore
from core.runtime_context import RuntimeContext
from core.settings import load_runtime_settings


def test_fixed_clock_is_deterministic() -> None:
    clock = FixedClock("2026-07-26T00:00:00Z")
    assert clock.now_utc_iso() == "2026-07-26T00:00:00Z"
    assert clock.now_utc_iso() == clock.now_utc_iso()


def test_system_clock_shape() -> None:
    stamp = SystemClock().now_utc_iso()
    assert stamp.endswith("Z")
    assert "T" in stamp


def test_filesystem_artifact_store_roundtrip(tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    store = FilesystemArtifactStore(tmp_path, out)
    stamped = store.write_artifact(
        "out/phase6_ports_probe.json",
        {"probe": True, "n": 1},
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
    )
    assert stamped["artifact_class"] == "AUDIT_EVIDENCE"
    assert stamped["influences_current_state"] is False
    assert store.exists("out/phase6_ports_probe.json")
    loaded = store.read_json("out/phase6_ports_probe.json")
    assert loaded["probe"] is True
    assert loaded["canonical_hash"] == stamped["canonical_hash"]


def test_filesystem_artifact_store_denies_traversal(tmp_path: Path) -> None:
    out = tmp_path / "out"
    out.mkdir()
    store = FilesystemArtifactStore(tmp_path, out)
    with pytest.raises(CanonicalWriteError):
        store.write_artifact(
            "out/../escape.json",
            {"x": 1},
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        )
    with pytest.raises(CanonicalWriteError):
        store.write_artifact(
            "contracts/escape.json",
            {"x": 1},
            artifact_class=ArtifactClass.AUDIT_EVIDENCE,
        )


def test_runtime_context_build_and_client(tmp_path: Path) -> None:
    settings = load_runtime_settings(repo_root=tmp_path)
    ctx = RuntimeContext.build(
        settings,
        clock=FixedClock("1970-01-01T00:00:00Z"),
    )
    assert ctx.clock.now_utc_iso() == "1970-01-01T00:00:00Z"
    client = AbraxasClient(context=ctx)
    assert client.settings.repo_root == tmp_path
    assert client.context.clock.now_utc_iso() == "1970-01-01T00:00:00Z"
    status = client.status()
    assert status["candidate_status"] == "NOT_READY"


def test_recovery_drill_storage_replay(tmp_path: Path) -> None:
    """Minimal recovery drill: rewrite classified receipt and re-read hash-stable."""
    settings = load_runtime_settings(repo_root=tmp_path)
    ctx = RuntimeContext.build(settings, clock=FixedClock("2026-01-01T00:00:00Z"))
    receipt = {
        "run_id": "recovery-drill-001",
        "status": "OK",
        "recorded_at": ctx.clock.now_utc_iso(),
    }
    first = ctx.storage.write_artifact(
        "out/production_convergence/recovery_drill_receipt.json",
        receipt,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
    )
    # Simulate restart: new context, same fixed clock + filesystem.
    restarted = RuntimeContext.build(
        settings,
        clock=FixedClock("2026-01-01T00:00:00Z"),
    )
    second = restarted.storage.write_artifact(
        "out/production_convergence/recovery_drill_receipt.json",
        receipt,
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
    )
    assert first["canonical_hash"] == second["canonical_hash"]
    on_disk = json.loads(
        (tmp_path / "out/production_convergence/recovery_drill_receipt.json").read_text(
            encoding="utf-8"
        )
    )
    assert on_disk["canonical_hash"] == first["canonical_hash"]

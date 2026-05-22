from __future__ import annotations

import hashlib
from pathlib import Path

from scripts.run_sync_snapshot import run


def test_sync_snapshot_fail_closed_on_missing_evidence(tmp_path: Path) -> None:
    packet = run(
        repo_root=tmp_path,
        out_json=tmp_path / "out/sync/sync_snapshot.latest.json",
        out_md=tmp_path / "out/sync/sync_snapshot.latest.md",
        notion_page_id="page_123",
        milestone="P200",
        artifact_paths=["out/does_not_exist.json"],
    )
    assert packet["sync_status"] == "NOT_COMPUTABLE"
    assert "out/does_not_exist.json" in packet["missing_evidence"]


def test_sync_snapshot_deterministic_hash_order(tmp_path: Path) -> None:
    a = tmp_path / "out" / "a.json"
    b = tmp_path / "out" / "b.json"
    a.parent.mkdir(parents=True, exist_ok=True)
    a.write_text('{"a":1}\n', encoding="utf-8")
    b.write_text('{"b":1}\n', encoding="utf-8")

    packet = run(
        repo_root=tmp_path,
        out_json=tmp_path / "out/sync/sync_snapshot.latest.json",
        out_md=tmp_path / "out/sync/sync_snapshot.latest.md",
        notion_page_id="page_123",
        milestone="P200",
        artifact_paths=["out/b.json", "out/a.json"],
    )
    assert list(packet["artifact_hashes"].keys()) == ["out/a.json", "out/b.json"]
    assert packet["artifact_hashes"]["out/a.json"] == hashlib.sha256(a.read_bytes()).hexdigest()
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True

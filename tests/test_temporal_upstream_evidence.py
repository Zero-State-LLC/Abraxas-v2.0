from __future__ import annotations

import json
from pathlib import Path

from core import temporal_upstream_evidence


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_receipt_missing_artifact_not_ready(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OUT_DIR", str(tmp_path / "out"))
    receipt = temporal_upstream_evidence.build_temporal_upstream_evidence_receipt()
    assert receipt["final_evidence_status"] == "NOT_READY"


def test_receipt_not_computable_degraded_ready(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OUT_DIR", str(tmp_path / "out"))
    out = tmp_path / "out" / "projections"
    _write(out / "temporal_state_diff_001.latest.json", {"final_status": "NOT_COMPUTABLE", "remaining_blockers": ["x"]})
    _write(out / "cross_run_topology_fusion_001.latest.json", {"final_status": "ADVISORY_ONLY"})
    _write(out / "live_projection_refresh_001.latest.json", {"final_status": "ADVISORY_ONLY", "status": "ADVISORY_ONLY"})
    receipt = temporal_upstream_evidence.build_temporal_upstream_evidence_receipt()
    assert receipt["final_evidence_status"] == "DEGRADED_READY"


def test_live_projection_included_with_lineage_assertion(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OUT_DIR", str(tmp_path / "out"))
    out = tmp_path / "out" / "projections"
    _write(out / "temporal_state_diff_001.latest.json", {"final_status": "ADVISORY_ONLY"})
    _write(out / "cross_run_topology_fusion_001.latest.json", {"final_status": "ADVISORY_ONLY"})
    _write(out / "live_projection_refresh_001.latest.json", {"final_status": "NOT_COMPUTABLE", "remaining_blockers": ["not_computable:projection_refresh_continuity"]})
    receipt = temporal_upstream_evidence.build_temporal_upstream_evidence_receipt()
    live = next(item for item in receipt["checked_artifacts"] if item["artifact_key"] == "live_projection_refresh")
    assert live["consumed_by"] == "temporal_state_diff"
    assert live["lineage_role"] == "required_parent"
    assert live["evidence_state"] == "AVAILABLE_DEGRADED"
    assert live["path_consumption_match"] is True
    assert receipt["lineage_assertions"]["live_projection_refresh_consumed_by_temporal_state_diff"] is True


def test_receipt_hash_deterministic_and_markdown_newline(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OUT_DIR", str(tmp_path / "out"))
    out = tmp_path / "out" / "projections"
    _write(out / "temporal_state_diff_001.latest.json", {"final_status": "ADVISORY_ONLY"})
    _write(out / "cross_run_topology_fusion_001.latest.json", {"final_status": "ADVISORY_ONLY"})
    _write(out / "live_projection_refresh_001.latest.json", {"final_status": "ADVISORY_ONLY"})
    receipt = temporal_upstream_evidence.build_temporal_upstream_evidence_receipt()
    hashes = [x["hash_sha256"] for x in receipt["checked_artifacts"]]
    assert all(isinstance(h, str) and h for h in hashes)
    path = tmp_path / "out" / "audit" / "temporal_upstream_evidence_001.latest.json"
    temporal_upstream_evidence.write_temporal_upstream_evidence_receipt(path, receipt)
    assert path.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")
    assert receipt["governance_flags"]["authority_granted"] is False

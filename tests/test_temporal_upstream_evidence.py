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
    ingest = [x for x in receipt["checked_artifacts"] if str(x["artifact_key"]).startswith("universal_ingest_")]
    assert len(ingest) == 3
    assert all(item["dependency_class"] == "optional" for item in ingest)
    assert all(item["dependency_required"] == "false" for item in ingest)


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
    required_hashes = [x["hash_sha256"] for x in receipt["checked_artifacts"] if x["dependency_class"] == "required"]
    assert all(isinstance(h, str) and h for h in required_hashes)
    for item in receipt["checked_artifacts"]:
        assert item["hash"] == item["hash_sha256"]
        assert item["artifact_path"] == item["path"]
        assert item["advisory_only"] is True
        assert item["authority_granted"] is False
        assert item["forecast_authority"] is False
        assert item["mutation_allowed"] is False
    path = tmp_path / "out" / "audit" / "temporal_upstream_evidence_001.latest.json"
    temporal_upstream_evidence.write_temporal_upstream_evidence_receipt(path, receipt)
    assert path.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")
    assert receipt["governance_flags"]["authority_granted"] is False
    assert receipt["governance_flags"]["forecast_authority"] is False


def test_optional_ingest_present_hashed_deterministically(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OUT_DIR", str(tmp_path / "out"))
    projections = tmp_path / "out" / "projections"
    ingest = tmp_path / "out" / "ingest"
    _write(projections / "temporal_state_diff_001.latest.json", {"final_status": "ADVISORY_ONLY"})
    _write(projections / "cross_run_topology_fusion_001.latest.json", {"final_status": "ADVISORY_ONLY"})
    _write(projections / "live_projection_refresh_001.latest.json", {"final_status": "ADVISORY_ONLY"})
    _write(ingest / "universal_ingest_receipt_001.latest.json", {"status": "ADVISORY_ONLY", "remaining_blockers": []})
    _write(ingest / "universal_ingest.validation_result.latest.json", {"status": "PASS"})
    _write(ingest / "universal_ingest.conflict_report.latest.json", {"status": "PASS", "remaining_blockers": []})

    a = temporal_upstream_evidence.build_temporal_upstream_evidence_receipt()
    b = temporal_upstream_evidence.build_temporal_upstream_evidence_receipt()
    assert a == b
    ingest_entries = [x for x in a["checked_artifacts"] if str(x["artifact_key"]).startswith("universal_ingest_")]
    assert all(item["exists"] is True for item in ingest_entries)
    assert all(isinstance(item["hash"], str) and item["hash"] for item in ingest_entries)
    assert all(item["source"] == "universal_ingest" for item in ingest_entries)
    assert all(item["lane"] == "SHADOW" for item in ingest_entries)

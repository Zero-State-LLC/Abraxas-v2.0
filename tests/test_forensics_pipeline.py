# tests/test_forensics_pipeline.py
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIXTURE = (
    REPO
    / "skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json"
)


def test_pipeline_fixture_ops_gate_denied():
    from core.forensics.pipeline import run_forensics_from_pack_path

    run = run_forensics_from_pack_path(FIXTURE, repo_root=REPO)
    assert run["schema_version"] == "ForensicRunPacket.v0"
    # C′ seal: hermes fixture must stay READY while ops gate stays DENIED
    assert run["disposition"]["disposition"] == "READY"
    assert run["ops_gate"]["gate_status"] == "DENIED"
    assert run["ops_gate"]["simulation"] == "WOULD_ALLOW"
    assert run["propagation"]["write_performed"] is False
    assert isinstance(run.get("pack_hash"), str) and run["pack_hash"]
    a = run_forensics_from_pack_path(FIXTURE, repo_root=REPO)
    assert a == run_forensics_from_pack_path(FIXTURE, repo_root=REPO)


def test_pipeline_non_object_pack_raises(tmp_path: Path):
    from core.forensics.pipeline import run_forensics_from_pack_path
    import pytest

    bad = tmp_path / "not_an_object.json"
    bad.write_text("[]", encoding="utf-8")
    with pytest.raises(TypeError, match="JSON object"):
        run_forensics_from_pack_path(bad, repo_root=REPO)


def test_pipeline_ok_and_authority_denied():
    from core.forensics.pipeline import run_forensics_from_pack_path

    run = run_forensics_from_pack_path(FIXTURE, repo_root=REPO)
    assert run["ok"] is True
    assert run["advisory_only"] is True
    assert run["lane"] == "SHADOW"
    assert run["authority"]["execution_authority"] is False
    assert run["authority"]["publish_authorized"] is False
    assert run["authority"]["queue_write_authorized"] is False
    assert run["authority"]["canon_mutation_allowed"] is False
    assert run["authority"]["forecast_weight_allowed"] is False
    assert run["authority"]["forecast_routing_authorized"] is False
    assert isinstance(run.get("canonical_hash"), str) and len(run["canonical_hash"]) == 64
    assert "pack_path" in run
    assert run["propagation"]["network_calls"] is False

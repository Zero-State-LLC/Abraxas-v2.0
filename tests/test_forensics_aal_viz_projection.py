# tests/test_forensics_aal_viz_projection.py
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from core.forensics.aal_viz_projection import (
    build_aal_viz_forensic_projection,
    build_aal_viz_forensic_projection_from_pack_path,
)
from core.forensics.pipeline import run_forensics_from_pack_path

REPO = Path(__file__).resolve().parents[1]
FIXTURE = (
    REPO
    / "skills/abx-familiar-signal-forager/fixtures/evidence_pack_hermes_skill_os_2026-07-27.v0.json"
)
SCHEMA = REPO / "contracts/forensics/aal_viz_forensic_projection.v0.schema.json"


def test_fixture_projection_ready_denied():
    proj = build_aal_viz_forensic_projection_from_pack_path(FIXTURE, repo_root=REPO)
    assert proj["schema_version"] == "AALVizForensicProjection.v0"
    assert proj["disposition"] == "READY"
    assert proj["ops_gate_status"] == "DENIED"
    assert proj["simulation"] == "WOULD_ALLOW"
    assert proj["projection_only"] is True
    assert proj["advisory_only"] is True
    assert proj["render_consumer_only"] is True
    assert proj["non_authoritative"] is True
    assert proj["lane"] == "SHADOW"
    assert proj["authority"]["execution_authority"] is False
    assert proj["authority"]["publish_authorized"] is False
    assert proj["graph_summary"]["write_performed"] is False
    assert proj["graph_summary"]["network_calls"] is False
    assert proj["graph_summary"]["node_count"] >= 1
    assert isinstance(proj["canonical_hash"], str) and len(proj["canonical_hash"]) == 64
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(proj)


def test_projection_deterministic():
    a = build_aal_viz_forensic_projection_from_pack_path(FIXTURE, repo_root=REPO)
    b = build_aal_viz_forensic_projection_from_pack_path(FIXTURE, repo_root=REPO)
    assert a == b


def test_none_run_fail_closed():
    proj = build_aal_viz_forensic_projection(None)
    assert proj["ops_gate_status"] == "DENIED"
    assert proj["disposition"] == ""
    assert proj["simulation"] == "WOULD_DENY"
    assert proj["graph_summary"]["node_count"] == 0
    assert proj["graph_summary"]["edge_count"] == 0
    assert proj["projection_only"] is True
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(proj)


def test_force_denied_even_if_source_gate_wrong():
    run = run_forensics_from_pack_path(FIXTURE, repo_root=REPO)
    # Craft a leaky ops_gate; projection must still DENY
    leaky = dict(run)
    leaky["ops_gate"] = {
        **(run.get("ops_gate") or {}),
        "gate_status": "ALLOWED",
    }
    proj = build_aal_viz_forensic_projection(leaky)
    assert proj["ops_gate_status"] == "DENIED"
    assert proj["disposition"] == "READY"

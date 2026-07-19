"""Tests for WP-F Threat Model v0."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from core.production_readiness.threat_model import build_threat_model_v0


REPO = Path(__file__).resolve().parents[1]


def test_threat_model_shape_and_schema() -> None:
    model = build_threat_model_v0(REPO, write=False)
    assert model["schema_version"] == "ThreatModel.v0"
    assert model["evidence_state"] == "Partial"
    assert len(model["threats"]) >= 8
    assert len(model["controls"]) >= 5
    assert any(t["threat_id"] == "T-01" for t in model["threats"])
    schema = json.loads(
        (
            REPO
            / "contracts/production_readiness/threat_model.v0.schema.json"
        ).read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=model, schema=schema)


def test_neon_and_writer_threats_present() -> None:
    model = build_threat_model_v0(REPO, write=False)
    ids = {t["threat_id"] for t in model["threats"]}
    assert "T-03" in ids  # writer bypass
    assert "T-07" in ids  # neon genie

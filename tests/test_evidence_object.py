from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from core.belief_graph.evidence_object import EvidenceObject


def test_evidence_object_accepts_required_fields() -> None:
    evidence = EvidenceObject(
        source="operator_log",
        provenance={"lane": "shadow"},
        timestamp="2026-06-02T00:00:00Z",
        evidence_type="TEXT",
        hash="ev-001",
    )
    assert evidence.hash == "ev-001"


def test_evidence_object_rejects_blank_hash() -> None:
    with pytest.raises(ValidationError, match="non-empty value required"):
        EvidenceObject(
            source="operator_log",
            provenance={"lane": "shadow"},
            timestamp="2026-06-02T00:00:00Z",
            evidence_type="TEXT",
            hash="   ",
        )


def test_evidence_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/belief_graph/evidence_object.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    evidence = EvidenceObject(
        source="operator_log",
        provenance={"lane": "shadow"},
        timestamp="2026-06-02T00:00:00Z",
        evidence_type="TEXT",
        hash="ev-002",
    )
    jsonschema.validate(evidence.model_dump(mode="json"), schema)

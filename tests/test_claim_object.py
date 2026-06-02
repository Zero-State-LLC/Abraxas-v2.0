from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from core.belief_graph.claim_object import ClaimObject


def test_claim_object_accepts_advisory_claim() -> None:
    claim = ClaimObject(
        id="claim-001",
        statement="Observed operator note remains unresolved.",
        provenance={"source": "shadow_lane"},
        evidence_refs=("ev-002", "ev-001"),
        confidence=0.25,
        status="OBSERVED",
    )
    assert claim.evidence_refs == ("ev-001", "ev-002")


def test_not_computable_claim_preserves_not_computable_confidence() -> None:
    with pytest.raises(
        ValidationError, match="not computable claims must preserve NOT_COMPUTABLE confidence"
    ):
        ClaimObject(
            id="claim-002",
            statement="Confidence unavailable.",
            provenance={"source": "shadow_lane"},
            evidence_refs=(),
            confidence=0.0,
            status="NOT_COMPUTABLE",
        )


def test_claim_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/belief_graph/claim_object.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    claim = ClaimObject(
        id="claim-003",
        statement="Speculative linkage recorded without truth assignment.",
        provenance={"source": "belief_graph"},
        evidence_refs=("ev-003",),
        confidence="NOT_COMPUTABLE",
        status="NOT_COMPUTABLE",
    )
    jsonschema.validate(claim.model_dump(mode="json"), schema)

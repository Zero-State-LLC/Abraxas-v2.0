from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from core.belief_graph.theory_object import TheoryObject


def test_theory_object_normalizes_relationship_refs() -> None:
    theory = TheoryObject(
        id="theory-001",
        supporting_claims=("claim-002", "claim-001"),
        conflicting_claims=(),
        evidence_refs=("ev-002", "ev-001"),
    )
    assert theory.supporting_claims == ("claim-001", "claim-002")
    assert theory.evidence_refs == ("ev-001", "ev-002")


def test_theory_object_rejects_overlapping_claim_sets() -> None:
    with pytest.raises(
        ValidationError, match="theory claims cannot be both supporting and conflicting"
    ):
        TheoryObject(
            id="theory-002",
            supporting_claims=("claim-001",),
            conflicting_claims=("claim-001",),
            evidence_refs=(),
        )


def test_theory_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/belief_graph/theory_object.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    theory = TheoryObject(
        id="theory-003",
        supporting_claims=("claim-001",),
        conflicting_claims=("claim-002",),
        evidence_refs=("ev-001",),
    )
    jsonschema.validate(theory.model_dump(mode="json"), schema)

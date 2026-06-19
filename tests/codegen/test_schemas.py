from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.codegen_shadow_replay_harness import run_codegen_shadow_replay

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/codegen"
PROPOSAL_SCHEMA_PATH = REPO_ROOT / "contracts/canon/improvement_proposal.v1.schema.json"
RECEIPT_SCHEMA_PATH = REPO_ROOT / "contracts/canon/shadow_improvement_receipt.v1.schema.json"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def _load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _strip_harness_receipt_fields(receipt: dict) -> dict:
    cleaned = dict(receipt)
    cleaned.pop("proof_flags", None)
    cleaned.pop("advisory_only", None)
    cleaned.pop("execution_authority", None)
    return cleaned


@pytest.fixture(name="jsonschema")
def fixture_jsonschema():
    return pytest.importorskip("jsonschema")


def test_golden_proposal_validates_against_schema(jsonschema) -> None:
    proposal = _load_fixture("improvement_proposal_golden.v1.json")
    jsonschema.validate(proposal, _load_schema(PROPOSAL_SCHEMA_PATH))


def test_self_improvement_meta_gate_proposal_validates_against_schema(jsonschema) -> None:
    proposal = _load_fixture("improvement_proposal_self_improvement_meta_gate.v1.json")
    jsonschema.validate(proposal, _load_schema(PROPOSAL_SCHEMA_PATH))


def test_golden_receipt_validates_against_schema(jsonschema) -> None:
    receipt = _load_fixture("shadow_receipt_golden.v1.json")
    jsonschema.validate(receipt, _load_schema(RECEIPT_SCHEMA_PATH))


def test_meta_gate_receipt_fixture_validates_against_schema(jsonschema) -> None:
    receipt = _load_fixture("self_improvement_meta_gate_receipt.v1.json")
    jsonschema.validate(receipt, _load_schema(RECEIPT_SCHEMA_PATH))


def test_harness_emitted_golden_receipt_validates_against_schema(jsonschema) -> None:
    proposal = _load_fixture("improvement_proposal_golden.v1.json")
    result = run_codegen_shadow_replay(proposal)
    receipt = _strip_harness_receipt_fields(result["receipt"])
    jsonschema.validate(receipt, _load_schema(RECEIPT_SCHEMA_PATH))


def test_negative_proposals_fail_harness_validation() -> None:
    negative_fixtures = [
        "invalid_improvement_proposal_missing_provenance.v1.json",
        "invalid_improvement_proposal_canon_jump.v1.json",
    ]
    for fixture_name in negative_fixtures:
        proposal = _load_fixture(fixture_name)
        result = run_codegen_shadow_replay(proposal)
        assert result["status"] == "VALIDATION_FAILED"
        assert result["receipt"] is None

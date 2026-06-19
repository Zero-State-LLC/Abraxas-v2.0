from __future__ import annotations

import copy
import json
from pathlib import Path

from core.codegen_shadow_replay_harness import (
    _determine_recommendation,
    _validate_proposal,
    run_codegen_shadow_replay,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/codegen"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def _golden_proposal() -> dict:
    return copy.deepcopy(_load_fixture("improvement_proposal_golden.v1.json"))


def test_val_001_invalid_schema_version() -> None:
    proposal = _golden_proposal()
    proposal["schema_version"] = "InvalidProposal.v9"
    assert "VAL-001:invalid_schema_version" in _validate_proposal(proposal)


def test_val_002_invalid_proposal_id() -> None:
    proposal = _golden_proposal()
    proposal["proposal_id"] = "not-a-hex-id"
    assert "VAL-002:invalid_proposal_id" in _validate_proposal(proposal)


def test_val_003_invalid_source_gap_diagnosis_id() -> None:
    proposal = _golden_proposal()
    proposal["source_gap_diagnosis_id"] = "short"
    assert "VAL-003:invalid_source_gap_diagnosis_id" in _validate_proposal(proposal)


def test_val_004_missing_provenance() -> None:
    proposal = _load_fixture("invalid_improvement_proposal_missing_provenance.v1.json")
    assert "VAL-004:missing_provenance" in _validate_proposal(proposal)


def test_gov_001_canon_jump_without_operator() -> None:
    proposal = _load_fixture("invalid_improvement_proposal_canon_jump.v1.json")
    assert "GOV-001:canon_jump_without_operator" in _validate_proposal(proposal)


def test_gov_002_self_improvement_canon_jump() -> None:
    proposal = _load_fixture("invalid_improvement_proposal_canon_jump.v1.json")
    assert "GOV-002:self_improvement_canon_jump" in _validate_proposal(proposal)


def test_gov_003_governance_surface_target() -> None:
    proposal = _golden_proposal()
    proposal["target_surface"] = "GENERATED_ARTIFACT_POLICY_V1"
    assert "GOV-003:governance_surface_target" in _validate_proposal(proposal)


def test_gov_004_governance_policy_mutation() -> None:
    proposal = _load_fixture("invalid_improvement_proposal_missing_provenance.v1.json")
    assert "GOV-004:governance_policy_mutation" in _validate_proposal(proposal)


def test_gov_005_file_write_not_denied() -> None:
    proposal = _golden_proposal()
    proposal["shadow_validation_plan"]["constraints"]["no_file_write"] = False
    assert "GOV-005:file_write_not_denied" in _validate_proposal(proposal)


def test_gov_006_network_not_denied() -> None:
    proposal = _golden_proposal()
    proposal["shadow_validation_plan"]["constraints"]["no_network"] = False
    assert "GOV-006:network_not_denied" in _validate_proposal(proposal)


def test_recommendation_reject_on_validation_errors() -> None:
    proposal = _load_fixture("invalid_improvement_proposal_missing_provenance.v1.json")
    result = run_codegen_shadow_replay(proposal)
    assert result["status"] == "VALIDATION_FAILED"
    assert result["receipt"] is None


def test_recommendation_block_policy_violation() -> None:
    flags = {
        "authority_lock_invariance_observed": True,
        "not_computable_replay_observed": False,
        "operator_review_observed": True,
        "no_runtime_mutation_observed": True,
        "no_canon_promotion_observed": False,
        "codegen_deterministic_output_observed": True,
        "contract_delta_replay_successful": True,
        "self_modification_invariants_satisfied": True,
        "meta_gate_extra_checks_passed": True,
    }
    recommendation, blockers = _determine_recommendation(
        "VALID", flags, self_modification_risk=False
    )
    assert recommendation == "BLOCK_POLICY_VIOLATION"
    assert blockers


def test_recommendation_block_replay_failure() -> None:
    flags = {
        "authority_lock_invariance_observed": True,
        "not_computable_replay_observed": False,
        "operator_review_observed": False,
        "no_runtime_mutation_observed": True,
        "no_canon_promotion_observed": True,
        "codegen_deterministic_output_observed": False,
        "contract_delta_replay_successful": True,
        "self_modification_invariants_satisfied": True,
        "meta_gate_extra_checks_passed": True,
    }
    recommendation, blockers = _determine_recommendation(
        "VALID", flags, self_modification_risk=False
    )
    assert recommendation == "BLOCK_REPLAY_FAILURE"
    assert blockers


def test_recommendation_hold_for_meta_gate() -> None:
    proposal = _load_fixture("improvement_proposal_self_improvement_meta_gate.v1.json")
    result = run_codegen_shadow_replay(proposal)
    assert result["receipt"]["recommendation"] == "HOLD_FOR_META_GATE"


def test_recommendation_hold_for_operator() -> None:
    proposal = _golden_proposal()
    result = run_codegen_shadow_replay(proposal)
    assert result["receipt"]["recommendation"] == "HOLD_FOR_OPERATOR"

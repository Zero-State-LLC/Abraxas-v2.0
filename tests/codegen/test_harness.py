from __future__ import annotations

import json
from pathlib import Path

from core.codegen_shadow_replay_harness import (
    DEFAULT_RUN_COUNT,
    META_GATE_RUN_COUNT,
    _build_replay_config,
    _determine_recommendation,
    _evaluate_proof_flags,
    _validate_proposal,
    run_codegen_shadow_replay,
    verify_run_invariance,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/codegen"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def test_validate_proposal_accepts_golden_fixture() -> None:
    proposal = _load_fixture("improvement_proposal_golden.v1.json")
    assert _validate_proposal(proposal) == []


def test_validate_proposal_rejects_missing_provenance() -> None:
    proposal = _load_fixture("invalid_improvement_proposal_missing_provenance.v1.json")
    errors = _validate_proposal(proposal)
    assert "VAL-004:missing_provenance" in errors


def test_validate_proposal_rejects_canon_jump() -> None:
    proposal = _load_fixture("invalid_improvement_proposal_canon_jump.v1.json")
    errors = _validate_proposal(proposal)
    assert "GOV-001:canon_jump_without_operator" in errors
    assert "GOV-002:self_improvement_canon_jump" in errors


def test_build_replay_config_is_deterministic() -> None:
    proposal = _load_fixture("improvement_proposal_golden.v1.json")
    plan = proposal["shadow_validation_plan"]
    first = _build_replay_config(plan)
    second = _build_replay_config(plan)
    assert first == second
    assert first["run_count"] == DEFAULT_RUN_COUNT


def test_run_codegen_shadow_replay_emits_receipt_for_golden_proposal() -> None:
    proposal = _load_fixture("improvement_proposal_golden.v1.json")
    result = run_codegen_shadow_replay(proposal)
    assert result["status"] == "SHADOW_REPLAY_COMPLETE"
    receipt = result["receipt"]
    assert receipt is not None
    assert receipt["schema_version"] == "ShadowImprovementReceipt.v1"
    assert receipt["proposal_id"] == proposal["proposal_id"]
    assert receipt["recommendation"] == "HOLD_FOR_OPERATOR"
    assert receipt["execution_authority"] is False
    assert receipt["advisory_only"] is True


def test_run_codegen_shadow_replay_rejects_invalid_proposal() -> None:
    proposal = _load_fixture("invalid_improvement_proposal_missing_provenance.v1.json")
    result = run_codegen_shadow_replay(proposal)
    assert result["status"] == "VALIDATION_FAILED"
    assert result["receipt"] is None
    assert result["errors"]


def test_proof_flags_pass_for_golden_proposal() -> None:
    proposal = _load_fixture("improvement_proposal_golden.v1.json")
    result = run_codegen_shadow_replay(proposal)
    flags = result["proof_flags"]
    assert flags["codegen_deterministic_output_observed"] is True
    assert flags["not_computable_replay_observed"] is False
    assert flags["operator_review_observed"] is True


def test_determine_recommendation_hold_for_meta_gate_on_self_modification() -> None:
    flags = {
        "authority_lock_invariance_observed": True,
        "not_computable_replay_observed": False,
        "operator_review_observed": True,
        "no_runtime_mutation_observed": True,
        "no_canon_promotion_observed": True,
        "codegen_deterministic_output_observed": True,
        "contract_delta_replay_successful": True,
        "self_modification_invariants_satisfied": True,
        "meta_gate_extra_checks_passed": True,
    }
    recommendation, blockers = _determine_recommendation(
        "VALID", flags, self_modification_risk=True
    )
    assert recommendation == "HOLD_FOR_META_GATE"
    assert blockers == []


def test_12_run_invariance_for_golden_proposal() -> None:
    proposal = _load_fixture("improvement_proposal_golden.v1.json")
    assert verify_run_invariance(proposal, run_count=DEFAULT_RUN_COUNT) is True


def test_24_run_meta_gate_invariance_for_golden_proposal() -> None:
    proposal = _load_fixture("improvement_proposal_golden.v1.json")
    assert verify_run_invariance(proposal, run_count=META_GATE_RUN_COUNT) is True


def test_evaluate_proof_flags_matches_replay_result() -> None:
    proposal = _load_fixture("improvement_proposal_golden.v1.json")
    replay = {
        "deterministic": True,
        "contract_delta_ok": True,
    }
    flags = _evaluate_proof_flags(proposal, replay)
    assert flags["codegen_deterministic_output_observed"] is True

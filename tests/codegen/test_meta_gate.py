from __future__ import annotations

import json
from pathlib import Path

from core.codegen_shadow_replay_harness import (
    META_GATE_RUN_COUNT,
    run_codegen_shadow_replay,
    verify_run_invariance,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests/fixtures/codegen"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def test_self_improvement_proposal_routes_to_hold_for_meta_gate() -> None:
    proposal = _load_fixture("improvement_proposal_self_improvement_meta_gate.v1.json")
    result = run_codegen_shadow_replay(proposal)

    assert result["status"] == "SHADOW_REPLAY_COMPLETE"
    receipt = result["receipt"]
    assert receipt is not None
    assert receipt["recommendation"] == "HOLD_FOR_META_GATE"
    assert receipt["execution_authority"] is False
    assert receipt["advisory_only"] is True
    assert result["proof_flags"]["meta_gate_extra_checks_passed"] is True
    assert receipt["governance_flags"]["self_modification_detected"] is True


def test_meta_gate_24_run_invariance() -> None:
    proposal = _load_fixture("improvement_proposal_self_improvement_meta_gate.v1.json")
    assert verify_run_invariance(proposal, run_count=META_GATE_RUN_COUNT) is True


def test_meta_gate_receipt_recommendation_matches_fixture_shape() -> None:
    proposal = _load_fixture("improvement_proposal_self_improvement_meta_gate.v1.json")
    reference = _load_fixture("self_improvement_meta_gate_receipt.v1.json")
    result = run_codegen_shadow_replay(proposal)
    receipt = result["receipt"]

    assert receipt is not None
    assert receipt["proposal_id"] == reference["proposal_id"]
    assert receipt["recommendation"] == reference["recommendation"]
    assert receipt["schema_version"] == reference["schema_version"]
    assert receipt["governance_flags"]["self_modification_detected"] is True
    assert receipt["governance_flags"]["requires_operator_review"] is True

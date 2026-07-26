"""Unit and integration tests for Alembic Spine."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.alembic.adapters import (
    GenerativeStubAdapter,
    SymbolicVerifierAdapter,
)
from core.alembic.config import RouterPolicy, default_router_policy, load_router_policy
from core.alembic.constants import AUTHORITY_LOCKS, FINAL_STATUS
from core.alembic.evaluation import run_evaluation_matrix
from core.alembic.hybrid import build_hybrid_plan, validate_hybrid_plan
from core.alembic.models import HybridNode, HybridPlan, TaskEnvelope
from core.alembic.pipeline import execute_advisory
from core.alembic.proposals import propose_router_update
from core.alembic.registry import ArchitectureRegistry, default_registry
from core.alembic.router import route_task
from core.alembic.runes import proposed_rune_manifest, rune_bindings_for_operation
from core.alembic.util import to_canonical_dict
from core.canonical.json import canonical_hash

REPO = Path(__file__).resolve().parents[1]


def _task(**overrides):
    base = {
        "task_id": "t1",
        "run_id": "r1",
        "goal": "Verify advisory claim",
        "task_type": "verify",
        "input_modalities": ("structured_json",),
        "input_artifacts": ({"artifact_id": "a1", "statement": "claim"},),
        "required_output_contract": "ArchitectureContribution.v1",
        "required_determinism": "STRICT_DETERMINISTIC",
        "verification_requirements": ("contract_check",),
        "allowed_architecture_families": ("symbolic_expert",),
    }
    base.update(overrides)
    return TaskEnvelope(**base)


def test_default_registry_deterministic_and_unique():
    registry = default_registry()
    snap1 = registry.snapshot()
    snap2 = registry.snapshot()
    assert snap1["content_hash"] == snap2["content_hash"]
    assert snap1["count"] == 8
    receipt = registry.validation_receipt()
    assert receipt["status"] == "PASS"


def test_registry_rejects_duplicate_architecture_ids():
    registry = ArchitectureRegistry(adapters=())
    registry.register(SymbolicVerifierAdapter())
    with pytest.raises(ValueError, match="duplicate architecture_id"):
        registry.register(SymbolicVerifierAdapter())


def test_router_selects_eligible_and_records_rationale():
    registry = default_registry()
    policy = default_router_policy()
    decision = route_task(_task(), registry, policy)
    assert decision.abstention_reason is None
    assert decision.selected_candidates == ("arch.symbolic_verifier.v1",)
    assert decision.candidate_scores[0].rationale
    assert decision.authority_locks == AUTHORITY_LOCKS
    assert decision.FINAL_STATUS == FINAL_STATUS


def test_router_abstains_when_no_eligible():
    registry = default_registry()
    decision = route_task(
        _task(input_modalities=("audio",), allowed_architecture_families=()),
        registry,
        default_router_policy(),
    )
    assert decision.abstention_reason == "no_eligible_candidates"
    assert decision.selected_candidates == ()


def test_ineligible_never_selected():
    registry = default_registry()
    decision = route_task(
        _task(allowed_architecture_families=("spiking_neuromorphic",)),
        registry,
        default_router_policy(),
    )
    assert "arch.snn_neuromorphic.v1" not in decision.selected_candidates
    assert decision.abstention_reason == "no_eligible_candidates"


def test_stub_never_scored_as_success():
    registry = default_registry()
    result = execute_advisory(
        _task(
            task_type="generate",
            allowed_architecture_families=("generative",),
            required_determinism="NONDETERMINISTIC",
        ),
        registry,
        default_router_policy(),
    )
    assert result["routing_decision"]["abstention_reason"] == "no_eligible_candidates"
    stub = GenerativeStubAdapter()
    assert stub.descriptor().is_stub is True
    assert stub.health().ready is False


def test_execute_advisory_end_to_end_deterministic():
    registry = default_registry()
    policy = default_router_policy()
    task = _task()
    a = execute_advisory(task, registry, policy)
    b = execute_advisory(task, registry, policy)
    assert a["routing_decision"]["decision_id"] == b["routing_decision"]["decision_id"]
    assert a["receipt"]["content_hash"] == b["receipt"]["content_hash"]
    assert a["replay_manifest"]["content_hash"] == b["replay_manifest"]["content_hash"]
    assert a["FINAL_STATUS"] == FINAL_STATUS
    assert a["authority_locks"]["execution_authority"] is False
    assert a["fusion"] is not None
    assert a["verification"]["status"] in {"PASS", "PASS_WITH_RESIDUALS"}


def test_shadow_cannot_become_active_fusion_input():
    registry = default_registry()
    policy = default_router_policy()
    task = _task(allowed_architecture_families=("symbolic_expert", "graph_neural"))
    result = execute_advisory(
        task,
        registry,
        policy,
        shadow_architecture_ids=("arch.graph_memetic.v1",),
    )
    comparison = result["shadow_comparison"]
    assert comparison["promotion_allowed"] is False
    assert comparison["policy_mutation_allowed"] is False
    shadow_ids = set(comparison["shadow_contribution_ids"])
    if result["fusion"]:
        accepted = set(result["fusion"]["accepted_contribution_ids"])
        assert shadow_ids.isdisjoint(accepted)


def test_failed_verification_not_accepted_in_fusion():
    registry = default_registry()
    policy = default_router_policy()
    result = execute_advisory(
        _task(governance_context={"attempted_authority_escalation": True}),
        registry,
        policy,
    )
    assert result["routing_decision"]["abstention_reason"] == "unsupported_authority_request"
    assert result["fusion"] is None or result["fusion"]["accepted_contribution_ids"] == []


def test_hybrid_plan_rejects_unbounded_cycle():
    plan = HybridPlan(
        plan_id="bad",
        nodes=(
            HybridNode(node_id="a", architecture_id="x", role="contribute", depends_on=("b",)),
            HybridNode(node_id="b", architecture_id="y", role="verify", depends_on=("a",)),
        ),
        execution_order=("a", "b"),
    )
    ok, reasons = validate_hybrid_plan(plan)
    assert ok is False
    assert "cycle_without_bounded_iterative_loop" in reasons


def test_hybrid_plan_builds_for_multi_select():
    plan = build_hybrid_plan(
        ("arch.graph_memetic.v1", "arch.symbolic_verifier.v1"),
        family_by_id={
            "arch.graph_memetic.v1": "graph_neural",
            "arch.symbolic_verifier.v1": "symbolic_expert",
        },
        fusion_method="deterministic_evidence_union",
    )
    assert plan is not None
    assert plan.nodes[-1].architecture_id == "arch.symbolic_verifier.v1"


def test_calibration_distinct_from_raw_confidence():
    registry = default_registry()
    result = execute_advisory(
        _task(
            task_type="calibrate",
            required_determinism="BOUNDED_DETERMINISTIC",
            allowed_architecture_families=("statistical_ml",),
            constraints={"raw_confidence": 0.99},
            verification_requirements=(),
        ),
        registry,
        default_router_policy(),
    )
    contrib = result["contributions"][0]
    assert contrib["confidence"] == 0.99
    assert contrib["calibrated_confidence"] is not None
    assert contrib["calibrated_confidence"] < contrib["confidence"]
    assert contrib["calibration_metadata"]["missing_calibration"] is False


def test_proposal_never_auto_applied():
    proposal = propose_router_update(default_router_policy())
    assert proposal.operator_gate_required is True
    assert proposal.status == "DRAFT"


def test_policy_unknown_weight_fails():
    with pytest.raises(ValueError):
        RouterPolicy(score_weights={**default_router_policy().score_weights, "extra": 0.0})


def test_contracts_and_fixtures_load():
    policy = load_router_policy(REPO / "contracts/alembic/router_policy.json")
    assert policy.policy_id == "alembic.router_policy.v1"
    task = TaskEnvelope.model_validate(
        json.loads((REPO / "fixtures/alembic/example_task.json").read_text(encoding="utf-8"))
    )
    assert task.task_id == "example-task-001"


def test_schema_validation_for_task_and_decision():
    jsonschema = pytest.importorskip("jsonschema")
    task_schema = json.loads(
        (REPO / "contracts/alembic/task_envelope.v1.schema.json").read_text(encoding="utf-8")
    )
    decision_schema = json.loads(
        (REPO / "contracts/alembic/routing_decision.v1.schema.json").read_text(encoding="utf-8")
    )
    task = _task()
    decision = route_task(task, default_registry(), default_router_policy())
    jsonschema.validate(to_canonical_dict(task), task_schema)
    jsonschema.validate(to_canonical_dict(decision), decision_schema)


def test_rune_bindings_reuse_existing_catalog_entries():
    bindings = rune_bindings_for_operation("PARADIGM_ROUTE")
    assert "RUNE.PIPELINE.ROUTE" in bindings
    manifest = proposed_rune_manifest()
    assert manifest["live_catalog_mutation"] is False


def test_evaluation_matrix_passes():
    result = run_evaluation_matrix()
    assert result.status == "PASS", [(c.case_id, c.detail) for c in result.cases if not c.passed]


def test_provenance_lineage_traceable():
    result = execute_advisory(_task(), default_registry(), default_router_policy())
    decision_id = result["routing_decision"]["decision_id"]
    contribution_id = result["contributions"][0]["contribution_id"]
    assert contribution_id
    assert decision_id
    assert result["fusion"]["lineage"]
    assert result["receipt"]["decision_id"] == decision_id
    assert result["receipt"]["parent_artifact_ids"]


def test_canonical_hash_stable_for_registry_snapshot():
    snap = default_registry().snapshot()
    assert isinstance(snap["content_hash"], str) and len(snap["content_hash"]) == 64
    again = default_registry().snapshot()
    assert snap["content_hash"] == again["content_hash"]
    assert canonical_hash(snap["architectures"])

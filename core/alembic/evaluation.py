"""Deterministic Alembic evaluation harness."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from core.alembic.config import RouterPolicy, default_router_policy
from core.alembic.models import (
    EvaluationCaseResult,
    EvaluationResult,
    Provenance,
    TaskEnvelope,
)
from core.alembic.pipeline import execute_advisory
from core.alembic.proposals import propose_router_update
from core.alembic.registry import ArchitectureRegistry, default_registry
from core.alembic.util import hash_model, make_id


def _case(
    case_id: str,
    fn: Callable[[], tuple[bool, str, dict[str, Any]]],
) -> EvaluationCaseResult:
    passed, detail, artifacts = fn()
    return EvaluationCaseResult(
        case_id=case_id, passed=passed, detail=detail, artifacts=artifacts
    )


def run_evaluation_matrix(
    registry: ArchitectureRegistry | None = None,
    policy: RouterPolicy | None = None,
) -> EvaluationResult:
    registry = registry or default_registry()
    policy = policy or default_router_policy()

    def one_eligible() -> tuple[bool, str, dict[str, Any]]:
        task = TaskEnvelope(
            task_id="eval-one-eligible",
            run_id="eval-run",
            goal="Verify local symbolic consistency",
            task_type="verify",
            input_modalities=("structured_json",),
            input_artifacts=({"artifact_id": "a1", "statement": "x holds"},),
            required_output_contract="ArchitectureContribution.v1",
            required_determinism="STRICT_DETERMINISTIC",
            verification_requirements=("contract_check",),
            allowed_architecture_families=("symbolic_expert",),
        )
        result = execute_advisory(task, registry, policy)
        decision = result["routing_decision"]
        ok = (
            decision["selected_candidates"] == ["arch.symbolic_verifier.v1"]
            and decision["abstention_reason"] is None
        )
        return ok, "one clearly eligible architecture", {"decision": decision}

    def none_eligible() -> tuple[bool, str, dict[str, Any]]:
        task = TaskEnvelope(
            task_id="eval-none-eligible",
            run_id="eval-run",
            goal="Unsupported modality task",
            task_type="verify",
            input_modalities=("audio",),
            required_output_contract="ArchitectureContribution.v1",
        )
        result = execute_advisory(task, registry, policy)
        ok = result["routing_decision"]["abstention_reason"] == "no_eligible_candidates"
        return ok, "no eligible architecture", {"decision": result["routing_decision"]}

    def unavailable_adapter() -> tuple[bool, str, dict[str, Any]]:
        task = TaskEnvelope(
            task_id="eval-unavailable",
            run_id="eval-run",
            goal="Use neuromorphic path",
            task_type="temporal_detection",
            input_modalities=("sequence",),
            required_output_contract="ArchitectureContribution.v1",
            allowed_architecture_families=("spiking_neuromorphic",),
        )
        result = execute_advisory(task, registry, policy)
        rejected = result["routing_decision"]["rejection_reasons"]
        ok = any("stub_not_executable" in reasons or "adapter_status:UNAVAILABLE" in reasons for reasons in rejected.values())
        ok = ok and result["routing_decision"]["abstention_reason"] == "no_eligible_candidates"
        return ok, "unavailable adapter path", {"decision": result["routing_decision"]}

    def privacy_restriction() -> tuple[bool, str, dict[str, Any]]:
        task = TaskEnvelope(
            task_id="eval-privacy",
            run_id="eval-run",
            goal="Strict local privacy task",
            task_type="advisory_analysis",
            input_modalities=("structured_json",),
            required_output_contract="ArchitectureContribution.v1",
            privacy_class="strict_local",
            allowed_architecture_families=("generative",),
        )
        result = execute_advisory(task, registry, policy)
        ok = result["routing_decision"]["abstention_reason"] == "no_eligible_candidates"
        return ok, "privacy restriction", {"decision": result["routing_decision"]}

    def hard_latency() -> tuple[bool, str, dict[str, Any]]:
        task = TaskEnvelope(
            task_id="eval-latency",
            run_id="eval-run",
            goal="Tight latency",
            task_type="memetic_analysis",
            input_modalities=("structured_json",),
            required_output_contract="ArchitectureContribution.v1",
            latency_budget_ms=1.0,
            allowed_architecture_families=("graph_neural",),
        )
        result = execute_advisory(task, registry, policy)
        reasons = result["routing_decision"]["rejection_reasons"]
        ok = any("latency_budget_exceeded" in values for values in reasons.values())
        return ok, "hard latency ceiling", {"decision": result["routing_decision"]}

    def authority_escalation() -> tuple[bool, str, dict[str, Any]]:
        task = TaskEnvelope(
            task_id="eval-auth",
            run_id="eval-run",
            goal="Attempt escalation",
            task_type="verify",
            input_modalities=("structured_json",),
            required_output_contract="ArchitectureContribution.v1",
            governance_context={"attempted_authority_escalation": True},
        )
        result = execute_advisory(task, registry, policy)
        ok = result["routing_decision"]["abstention_reason"] == "unsupported_authority_request"
        return ok, "attempted authority escalation", {"decision": result["routing_decision"]}

    def malformed_and_conflict() -> tuple[bool, str, dict[str, Any]]:
        task = TaskEnvelope(
            task_id="eval-conflict",
            run_id="eval-run",
            goal="Conflict fusion case",
            task_type="advisory_analysis",
            input_modalities=("structured_json", "text"),
            input_artifacts=({"artifact_id": "a1", "statement": "signal rising"},),
            required_output_contract="ArchitectureContribution.v1",
            verification_requirements=("contract_check",),
            allowed_architecture_families=("symbolic_expert", "statistical_ml", "graph_neural"),
        )
        result = execute_advisory(task, registry, policy)
        ok = result["fusion"] is not None and result["verification"]["status"] in {
            "PASS",
            "PASS_WITH_RESIDUALS",
            "FAIL",
            "ABSTAIN",
        }
        return ok, "conflicting/multi-candidate path", {"fusion": result["fusion"], "verification": result["verification"]}

    def shadow_compare() -> tuple[bool, str, dict[str, Any]]:
        task = TaskEnvelope(
            task_id="eval-shadow",
            run_id="eval-run",
            goal="Compare shadow candidate",
            task_type="advisory_analysis",
            input_modalities=("structured_json",),
            input_artifacts=({"artifact_id": "a1", "statement": "active claim"},),
            required_output_contract="ArchitectureContribution.v1",
            allowed_architecture_families=("symbolic_expert",),
        )
        result = execute_advisory(
            task,
            registry,
            policy,
            shadow_architecture_ids=("arch.graph_memetic.v1",),
        )
        comparison = result["shadow_comparison"]
        ok = (
            comparison is not None
            and comparison["promotion_allowed"] is False
            and comparison["policy_mutation_allowed"] is False
        )
        return ok, "shadow candidate comparison isolated", {"shadow_comparison": comparison}

    def high_conf_poor_calib() -> tuple[bool, str, dict[str, Any]]:
        task = TaskEnvelope(
            task_id="eval-calib",
            run_id="eval-run",
            goal="Calibrate overconfident estimate",
            task_type="calibrate",
            input_modalities=("structured_json",),
            required_output_contract="ArchitectureContribution.v1",
            constraints={"raw_confidence": 0.99},
            allowed_architecture_families=("statistical_ml",),
        )
        result = execute_advisory(task, registry, policy)
        contribs = result["contributions"]
        ok = bool(contribs) and contribs[0]["calibrated_confidence"] is not None
        ok = ok and contribs[0]["calibrated_confidence"] < contribs[0]["confidence"]
        return ok, "high-confidence poorly calibrated candidate adjusted", {"contributions": contribs}

    def router_tie() -> tuple[bool, str, dict[str, Any]]:
        tie_policy = policy.model_copy(
            update={"eligibility": {**policy.eligibility, "require_explicit_tie_break": True, "tie_break": None}}
        )
        # Force similar candidates by broad advisory task with two strong deterministic locals.
        task = TaskEnvelope(
            task_id="eval-tie",
            run_id="eval-run",
            goal="Tie case",
            task_type="advisory_analysis",
            input_modalities=("structured_json",),
            required_output_contract="ArchitectureContribution.v1",
            required_determinism="STRICT_DETERMINISTIC",
            allowed_architecture_families=("symbolic_expert", "deterministic_tool"),
        )
        result = execute_advisory(task, registry, tie_policy)
        decision = result["routing_decision"]
        scores = decision["candidate_scores"]
        ok = len(scores) >= 2
        # Either abstains on tie or selects with recorded rationale.
        ok = ok and (
            decision["abstention_reason"] == "candidate_tie_without_tie_break_policy"
            or (decision["selected_candidates"] and scores[0]["rationale"])
        )
        return ok, "router tie handled", {"decision": decision}

    def provenance_failure() -> tuple[bool, str, dict[str, Any]]:
        # Execute normal path and ensure provenance hashes exist on contributions/decision.
        task = TaskEnvelope(
            task_id="eval-prov",
            run_id="eval-run",
            goal="Provenance required",
            task_type="verify",
            input_modalities=("text",),
            input_artifacts=({"artifact_id": "a1", "statement": "observed"},),
            required_output_contract="ArchitectureContribution.v1",
            allowed_architecture_families=("symbolic_expert",),
        )
        result = execute_advisory(task, registry, policy)
        ok = result["routing_decision"]["provenance"]["content_hash"] is not None
        ok = ok and all(c["provenance"]["content_hash"] for c in result["contributions"])
        return ok, "provenance present on decision and contributions", {"receipt": result["receipt"]}

    def proposal_not_auto_applied() -> tuple[bool, str, dict[str, Any]]:
        proposal = propose_router_update(policy, evidence=("eval",))
        ok = proposal.operator_gate_required is True and proposal.status == "DRAFT"
        return ok, "router proposal requires operator gate", {"proposal": proposal.model_dump(mode="python")}

    cases = (
        _case("one_clearly_eligible_architecture", one_eligible),
        _case("no_eligible_architecture", none_eligible),
        _case("unavailable_adapter", unavailable_adapter),
        _case("privacy_restriction", privacy_restriction),
        _case("hard_latency_ceiling", hard_latency),
        _case("attempted_authority_escalation", authority_escalation),
        _case("conflicting_candidates", malformed_and_conflict),
        _case("shadow_candidate_comparison", shadow_compare),
        _case("high_confidence_poor_calibration", high_conf_poor_calib),
        _case("router_tie", router_tie),
        _case("provenance_present", provenance_failure),
        _case("proposal_operator_gated", proposal_not_auto_applied),
    )
    passed_count = sum(1 for case in cases if case.passed)
    failed_count = len(cases) - passed_count
    result = EvaluationResult(
        evaluation_id=make_id("evaluation", passed_count, failed_count),
        cases=cases,
        passed_count=passed_count,
        failed_count=failed_count,
        status="PASS" if failed_count == 0 else "FAIL",
        provenance=Provenance(classification="OBSERVED", producer="core.alembic.evaluation"),
    )
    digest = hash_model(result)
    return result.model_copy(
        update={"provenance": result.provenance.model_copy(update={"content_hash": digest})}
    )

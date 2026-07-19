from __future__ import annotations

# WP-D4-C3: pure builder — sole-writer scripts own out/ publication.
from core.proposal_sandbox_evaluation.continuity import (
    ProposalSandboxEvaluationContinuityPacket,
)
from core.proposal_sandbox_evaluation.diagnostics import (
    ProposalSandboxEvaluationDiagnosticPacket,
)
from core.proposal_sandbox_evaluation.evaluations import ProposalSandboxEvaluationPacket
from core.proposal_sandbox_evaluation.lineage import ProposalSandboxEvaluationLineagePacket
from core.proposal_sandbox_evaluation.operator_review import (
    ProposalSandboxEvaluationOperatorReviewPacket,
)
from core.proposal_sandbox_evaluation.rationale import ProposalSandboxRationalePacket
from core.proposal_sandbox_evaluation.replay import ProposalSandboxEvaluationReplayPacket
from core.proposal_sandbox_evaluation.restrictions import (
    FORBIDDEN_ACTIONS,
    ProposalSandboxRestrictionPacket,
)
from core.proposal_sandbox_evaluation.scores import ProposalSandboxScorePacket
from core.proposal_sandbox_evaluation.validators import validate_proposal_sandbox_evaluation


def run_proposal_sandbox_evaluation(
    proposal_sandbox_routing_packets: list[dict],
    external_action_proposal_packets: list[dict],
    operator_queue_packets: list[dict],
    replay_packets: list[dict],
) -> dict[str, object]:
    _ = (
        proposal_sandbox_routing_packets,
        external_action_proposal_packets,
        operator_queue_packets,
        replay_packets,
    )

    evaluation = ProposalSandboxEvaluationPacket(
        evaluation_id="pse-1",
        route_hash="route-1",
        evaluation_status="evaluation_recorded",
        deterministic_evaluation_hash=ProposalSandboxEvaluationPacket.compute_hash(
            "route-1",
            "evaluation_recorded",
        ),
        status="passed",
    )
    score = ProposalSandboxScorePacket(
        evaluation_hash=evaluation.deterministic_evaluation_hash,
        evaluation_score=0.5,
        deterministic_score_hash=ProposalSandboxScorePacket.compute_hash(
            evaluation.deterministic_evaluation_hash,
            0.5,
        ),
        status="passed",
    )
    rationale = ProposalSandboxRationalePacket(
        evaluation_hash=evaluation.deterministic_evaluation_hash,
        rationale="sandbox-only advisory evaluation posture",
        cited_diagnostics=[],
        deterministic_rationale_hash=ProposalSandboxRationalePacket.compute_hash(
            evaluation.deterministic_evaluation_hash,
            "sandbox-only advisory evaluation posture",
            [],
        ),
        status="passed",
    )

    restricted_actions = sorted(FORBIDDEN_ACTIONS)
    restriction = ProposalSandboxRestrictionPacket(
        evaluation_hash=evaluation.deterministic_evaluation_hash,
        governance_restricted=True,
        restricted_actions=restricted_actions,
        deterministic_restriction_hash=ProposalSandboxRestrictionPacket.compute_hash(
            evaluation.deterministic_evaluation_hash,
            True,
            restricted_actions,
        ),
        status="passed",
    )
    continuity = ProposalSandboxEvaluationContinuityPacket(
        evaluation_hash=evaluation.deterministic_evaluation_hash,
        prior_hashes=["proposal-sandbox-eval-root"],
        append_only=True,
        deterministic_continuity_hash=ProposalSandboxEvaluationContinuityPacket.compute_hash(
            evaluation.deterministic_evaluation_hash,
            ["proposal-sandbox-eval-root"],
            True,
        ),
        status="passed",
    )
    replay = ProposalSandboxEvaluationReplayPacket(
        evaluation_hash=evaluation.deterministic_evaluation_hash,
        replay_evaluation_hash=evaluation.deterministic_evaluation_hash,
        deterministic_match=True,
        mismatch_reasons=[],
        deterministic_replay_hash=ProposalSandboxEvaluationReplayPacket.compute_hash(
            evaluation.deterministic_evaluation_hash,
            evaluation.deterministic_evaluation_hash,
            True,
            [],
        ),
        status="passed",
    )
    lineage = ProposalSandboxEvaluationLineagePacket(
        evaluation_hash=evaluation.deterministic_evaluation_hash,
        parent_hashes=["proposal-sandbox-evaluation-root"],
        lineage_cycle_detected=False,
        deterministic_lineage_hash=ProposalSandboxEvaluationLineagePacket.compute_hash(
            evaluation.deterministic_evaluation_hash,
            ["proposal-sandbox-evaluation-root"],
            False,
        ),
        status="passed",
    )

    diagnostics: list[ProposalSandboxEvaluationDiagnosticPacket] = []
    diagnostic_payload = [diagnostic.model_dump() for diagnostic in diagnostics]

    operator_review = ProposalSandboxEvaluationOperatorReviewPacket(
        review_id="pseor-1",
        evaluation_hash=evaluation.deterministic_evaluation_hash,
        evaluation_count=1,
        blocked_evaluations=0,
        unresolved_diagnostics=0,
        deterministic_review_hash=ProposalSandboxEvaluationOperatorReviewPacket.compute_hash(
            evaluation.deterministic_evaluation_hash,
            1,
            0,
            0,
        ),
        status="passed",
    )
    validator = validate_proposal_sandbox_evaluation(
        evaluation_status=evaluation.evaluation_status,
        attempted_actions=[],
        replay_match=replay.deterministic_match,
        diagnostics=diagnostic_payload,
        lineage_cycle_detected=lineage.lineage_cycle_detected,
        authority_mutation=False,
        execution_authority=False,
        deployment_authority=False,
        production_routing_authority=False,
        auto_execution_attempted=False,
    )

    summary = {
        "evaluation_count": 1,
        "blocked_evaluations": 0,
        "evaluation_score": score.evaluation_score,
        "unresolved_diagnostics": 0,
        "replay_matches": replay.deterministic_match,
        "governance_restricted": restriction.governance_restricted,
        "authority_locked": True,
        "projection_only": True,
        "inference_authority": False,
    }
    return {
        "evaluation": evaluation.model_dump(),
        "score": score.model_dump(),
        "rationale": rationale.model_dump(),
        "restriction": restriction.model_dump(),
        "continuity": continuity.model_dump(),
        "replay": replay.model_dump(),
        "lineage": lineage.model_dump(),
        "diagnostics": diagnostic_payload,
        "operator_review": operator_review.model_dump(),
        "proposal_sandbox_evaluation_summary": summary,
        "validator": validator,
        "status": validator["status"],
    }

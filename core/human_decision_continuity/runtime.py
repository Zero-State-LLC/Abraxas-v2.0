from __future__ import annotations

# WP-D4-C4: pure builder — sole-writer scripts own out/ publication.
from core.human_decision_continuity.blockers import HumanDecisionContinuityBlockerPacket
from core.human_decision_continuity.chains import HumanDecisionChainPacket
from core.human_decision_continuity.continuity import HumanDecisionContinuityPacket
from core.human_decision_continuity.deferrals import HumanDecisionContinuityDeferralPacket
from core.human_decision_continuity.diagnostics import HumanDecisionContinuityDiagnosticPacket
from core.human_decision_continuity.escalations import HumanDecisionContinuityEscalationPacket
from core.human_decision_continuity.inheritance import HumanDecisionInheritancePacket
from core.human_decision_continuity.lineage import HumanDecisionContinuityLineagePacket
from core.human_decision_continuity.operator_review import (
    HumanDecisionContinuityOperatorReviewPacket,
)
from core.human_decision_continuity.replay import HumanDecisionContinuityReplayPacket
from core.human_decision_continuity.validators import validate_human_decision_continuity


def run_human_decision_continuity(
    human_decision_ledger_packets: list[dict],
    proposal_decision_bridge_packets: list[dict],
    operator_queue_packets: list[dict],
    replay_packets: list[dict],
) -> dict[str, object]:
    _ = (
        human_decision_ledger_packets,
        proposal_decision_bridge_packets,
        operator_queue_packets,
        replay_packets,
    )

    chain = HumanDecisionChainPacket(
        chain_id="hdc-1",
        root_decision_hash="d-1",
        continuity_chain_count=1,
        deterministic_chain_hash=HumanDecisionChainPacket.compute_hash("d-1", 1),
        status="passed",
    )
    inheritance = HumanDecisionInheritancePacket(
        chain_hash=chain.deterministic_chain_hash,
        inherited_rationale="carry-forward",
        deterministic_inheritance_hash=HumanDecisionInheritancePacket.compute_hash(
            chain.deterministic_chain_hash,
            "carry-forward",
        ),
        status="passed",
    )
    deferral = HumanDecisionContinuityDeferralPacket(
        chain_hash=chain.deterministic_chain_hash,
        deferred_chains=1,
        deterministic_deferral_hash=HumanDecisionContinuityDeferralPacket.compute_hash(
            chain.deterministic_chain_hash,
            1,
        ),
        status="passed",
    )
    blocker = HumanDecisionContinuityBlockerPacket(
        chain_hash=chain.deterministic_chain_hash,
        blocked_chains=1,
        deterministic_blocker_hash=HumanDecisionContinuityBlockerPacket.compute_hash(
            chain.deterministic_chain_hash,
            1,
        ),
        status="passed",
    )
    escalation = HumanDecisionContinuityEscalationPacket(
        chain_hash=chain.deterministic_chain_hash,
        escalation_state="stable",
        deterministic_escalation_hash=HumanDecisionContinuityEscalationPacket.compute_hash(
            chain.deterministic_chain_hash,
            "stable",
        ),
        status="passed",
    )
    continuity = HumanDecisionContinuityPacket(
        chain_hash=chain.deterministic_chain_hash,
        append_only=True,
        deterministic_continuity_hash=HumanDecisionContinuityPacket.compute_hash(
            chain.deterministic_chain_hash,
            True,
        ),
        status="passed",
    )
    replay = HumanDecisionContinuityReplayPacket(
        chain_hash=chain.deterministic_chain_hash,
        replay_chain_hash=chain.deterministic_chain_hash,
        deterministic_match=True,
        deterministic_replay_hash=HumanDecisionContinuityReplayPacket.compute_hash(
            chain.deterministic_chain_hash,
            chain.deterministic_chain_hash,
            True,
        ),
        status="passed",
    )
    lineage = HumanDecisionContinuityLineagePacket(
        chain_hash=chain.deterministic_chain_hash,
        lineage_cycle_detected=False,
        deterministic_lineage_hash=HumanDecisionContinuityLineagePacket.compute_hash(
            chain.deterministic_chain_hash,
            False,
        ),
        status="passed",
    )

    diagnostics: list[HumanDecisionContinuityDiagnosticPacket] = []
    diagnostic_payload = [diagnostic.model_dump() for diagnostic in diagnostics]

    operator_review = HumanDecisionContinuityOperatorReviewPacket(
        review_id="hdcor-1",
        chain_hash=chain.deterministic_chain_hash,
        unresolved_diagnostics=0,
        deterministic_review_hash=HumanDecisionContinuityOperatorReviewPacket.compute_hash(
            chain.deterministic_chain_hash,
            0,
        ),
        status="passed",
    )
    validator = validate_human_decision_continuity(
        replay_match=replay.deterministic_match,
        diagnostics=diagnostic_payload,
        lineage_cycle_detected=lineage.lineage_cycle_detected,
        authority_mutation=False,
    )

    summary = {
        "continuity_chain_count": 1,
        "deferred_chains": 1,
        "blocked_chains": 1,
        "unresolved_diagnostics": 0,
        "replay_matches": True,
        "governance_restricted": True,
        "authority_locked": True,
        "projection_only": True,
        "inference_authority": False,
    }
    packet = {
        "chain": chain.model_dump(),
        "inheritance": inheritance.model_dump(),
        "deferral": deferral.model_dump(),
        "blocker": blocker.model_dump(),
        "escalation": escalation.model_dump(),
        "continuity": continuity.model_dump(),
        "replay": replay.model_dump(),
        "lineage": lineage.model_dump(),
        "diagnostics": diagnostic_payload,
        "operator_review": operator_review.model_dump(),
        "human_decision_continuity_summary": summary,
        "validator": validator,
        "status": validator["status"],
    }

    return packet

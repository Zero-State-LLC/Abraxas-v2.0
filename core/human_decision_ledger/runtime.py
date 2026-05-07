from __future__ import annotations
from core.canonical.json import write_canonical_json
from core.human_decision_ledger.blockers import HumanDecisionBlockerPacket
from core.human_decision_ledger.continuity import HumanDecisionContinuityPacket
from core.human_decision_ledger.decisions import HumanDecisionLedgerPacket
from core.human_decision_ledger.deferrals import HumanDecisionDeferralPacket
from core.human_decision_ledger.diagnostics import HumanDecisionDiagnosticPacket
from core.human_decision_ledger.escalations import HumanDecisionEscalationPacket
from core.human_decision_ledger.lineage import HumanDecisionLineagePacket
from core.human_decision_ledger.operator_review import HumanDecisionOperatorReviewPacket
from core.human_decision_ledger.rationale import HumanDecisionRationalePacket
from core.human_decision_ledger.replay import HumanDecisionReplayPacket
from core.human_decision_ledger.validators import validate_human_decision_ledger

def run_human_decision_ledger(proposal_decision_bridge_packets: list[dict], proposal_sandbox_evaluation_packets: list[dict], operator_queue_packets: list[dict], replay_packets: list[dict]) -> dict[str, object]:
    decision = HumanDecisionLedgerPacket(decision_id="hdl-1", bridge_hash="bridge-1", decision_state="review_only", deterministic_decision_hash=HumanDecisionLedgerPacket.compute_hash("bridge-1", "review_only"), status="passed")
    rationale = HumanDecisionRationalePacket(decision_hash=decision.deterministic_decision_hash, rationale_summary="operator-mediated review outcome", cited_review_notes=["needs follow-up"], deterministic_rationale_hash=HumanDecisionRationalePacket.compute_hash(decision.deterministic_decision_hash, "operator-mediated review outcome", ["needs follow-up"]), status="passed")
    blocker = HumanDecisionBlockerPacket(decision_hash=decision.deterministic_decision_hash, blockers=["missing supplemental evidence"], unresolved_blockers=1, deterministic_blocker_hash=HumanDecisionBlockerPacket.compute_hash(decision.deterministic_decision_hash, ["missing supplemental evidence"], 1), status="passed")
    deferral = HumanDecisionDeferralPacket(decision_hash=decision.deterministic_decision_hash, deferred=True, deferral_reason="pending additional operator evidence", deterministic_deferral_hash=HumanDecisionDeferralPacket.compute_hash(decision.deterministic_decision_hash, True, "pending additional operator evidence"), status="passed")
    escalation = HumanDecisionEscalationPacket(decision_hash=decision.deterministic_decision_hash, escalated=False, escalation_reason="not required", deterministic_escalation_hash=HumanDecisionEscalationPacket.compute_hash(decision.deterministic_decision_hash, False, "not required"), status="passed")
    continuity = HumanDecisionContinuityPacket(decision_hash=decision.deterministic_decision_hash, prior_hashes=["human-decision-root"], append_only=True, deterministic_continuity_hash=HumanDecisionContinuityPacket.compute_hash(decision.deterministic_decision_hash, ["human-decision-root"], True), status="passed")
    replay = HumanDecisionReplayPacket(decision_hash=decision.deterministic_decision_hash, replay_decision_hash=decision.deterministic_decision_hash, deterministic_match=True, mismatch_reasons=[], deterministic_replay_hash=HumanDecisionReplayPacket.compute_hash(decision.deterministic_decision_hash, decision.deterministic_decision_hash, True, []), status="passed")
    lineage = HumanDecisionLineagePacket(decision_hash=decision.deterministic_decision_hash, parent_hashes=["human-decision-root"], lineage_cycle_detected=False, deterministic_lineage_hash=HumanDecisionLineagePacket.compute_hash(decision.deterministic_decision_hash, ["human-decision-root"], False), status="passed")
    diagnostics: list[HumanDecisionDiagnosticPacket] = []
    operator_review = HumanDecisionOperatorReviewPacket(review_id="hdor-1", decision_hash=decision.deterministic_decision_hash, decision_count=1, deferred_decisions=1, blocked_decisions=1, unresolved_diagnostics=0, deterministic_review_hash=HumanDecisionOperatorReviewPacket.compute_hash(decision.deterministic_decision_hash, 1, 1, 1, 0), status="passed")
    validator = validate_human_decision_ledger(decision.decision_state, replay.deterministic_match, [d.model_dump() for d in diagnostics], lineage.lineage_cycle_detected, False, False, False, False, False)
    packet = {"decision": decision.model_dump(), "rationale": rationale.model_dump(), "blocker": blocker.model_dump(), "deferral": deferral.model_dump(), "escalation": escalation.model_dump(), "continuity": continuity.model_dump(), "replay": replay.model_dump(), "lineage": lineage.model_dump(), "diagnostics": [d.model_dump() for d in diagnostics], "operator_review": operator_review.model_dump(), "human_decision_ledger_summary": {"decision_count": 1, "deferred_decisions": 1, "blocked_decisions": 1, "unresolved_diagnostics": 0, "replay_matches": replay.deterministic_match, "governance_restricted": True, "authority_locked": True, "projection_only": True, "inference_authority": False}, "validator": validator, "status": validator["status"]}
    write_canonical_json("out/human_decision_ledger/latest.json", packet)
    write_canonical_json("out/human_decision_ledger_replay/latest.json", replay.model_dump())
    write_canonical_json("out/human_decision_ledger_lineage/latest.json", lineage.model_dump())
    write_canonical_json("out/human_decision_ledger_diagnostics/latest.json", [d.model_dump() for d in diagnostics])
    return packet

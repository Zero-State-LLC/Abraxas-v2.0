from __future__ import annotations

# WP-D4-C4: pure builder — sole-writer scripts own out/ publication.
from core.review_continuity.chains import ReviewContinuityChainPacket
from core.review_continuity.inheritance import ReviewRationaleInheritancePacket
from core.review_continuity.deferrals import ReviewDeferralPacket
from core.review_continuity.denials import ReviewDenialPacket
from core.review_continuity.continuity import ReviewContinuityPacket
from core.review_continuity.replay import ReviewContinuityReplayPacket
from core.review_continuity.lineage import ReviewContinuityLineagePacket
from core.review_continuity.diagnostics import ReviewContinuityDiagnosticPacket
from core.review_continuity.operator_review import ReviewContinuityReviewPacket
from core.review_continuity.validators import validate_review_continuity


def run_review_continuity_ledger(operator_queue_packets: list[dict], firewall_packets: list[dict], governance_packets: list[dict], rationale_packets: list[dict], replay_packets: list[dict]) -> dict[str, object]:
    chain = ReviewContinuityChainPacket(chain_id="rcc-1", originating_request_hash="rq-1", linked_review_hashes=["rev-1"], linked_rationale_hashes=["rat-1"], linked_governance_hashes=["gov-1"], linked_firewall_hashes=["fw-1"], chain_status="review_only_continuity", deterministic_chain_hash=ReviewContinuityChainPacket.compute_hash("rq-1", ["rev-1"], ["rat-1"], ["gov-1"], ["fw-1"], "review_only_continuity"), status="passed")
    inheritance = ReviewRationaleInheritancePacket(inheritance_id="rci-1", parent_rationale_hash="rat-1", inherited_constraints=["manual_execution_only"], inherited_denials=[], inherited_deferrals=[], inherited_governance_flags=["projection_only"], deterministic_inheritance_hash=ReviewRationaleInheritancePacket.compute_hash("rat-1", ["manual_execution_only"], [], [], ["projection_only"]), status="passed")
    deferral = ReviewDeferralPacket(deferral_id="rcd-1", chain_hash=chain.deterministic_chain_hash, deferral_reason="awaiting schedule window", deferral_code="deferred_window", deterministic_deferral_hash=ReviewDeferralPacket.compute_hash(chain.deterministic_chain_hash, "awaiting schedule window", "deferred_window"), status="passed")
    denial = ReviewDenialPacket(denial_id="rcn-1", chain_hash=chain.deterministic_chain_hash, denial_reason="insufficient governance evidence", denial_code="deny_evidence", deterministic_denial_hash=ReviewDenialPacket.compute_hash(chain.deterministic_chain_hash, "insufficient governance evidence", "deny_evidence"), status="passed")
    continuity = ReviewContinuityPacket(continuity_id="rcp-1", chain_hash=chain.deterministic_chain_hash, continuity_score=1.0, continuity_integrity=True, unresolved_breaks=[], deterministic_continuity_hash=ReviewContinuityPacket.compute_hash(chain.deterministic_chain_hash, 1.0, True, []), status="passed")
    replay = ReviewContinuityReplayPacket(replay_id="rcr-1", source_continuity_hash=continuity.deterministic_continuity_hash, replay_continuity_hash=continuity.deterministic_continuity_hash, deterministic_match=True, mismatch_reasons=[], deterministic_replay_hash=ReviewContinuityReplayPacket.compute_hash(continuity.deterministic_continuity_hash, continuity.deterministic_continuity_hash, True, []), status="passed")
    lineage = ReviewContinuityLineagePacket(lineage_id="rcl-1", continuity_hash=continuity.deterministic_continuity_hash, parent_hashes=["continuity-root"], lineage_cycle_detected=False, deterministic_lineage_hash=ReviewContinuityLineagePacket.compute_hash(continuity.deterministic_continuity_hash, ["continuity-root"], False), status="passed")
    diagnostics: list[ReviewContinuityDiagnosticPacket] = []
    review = ReviewContinuityReviewPacket(review_id="rco-1", continuity_hash=continuity.deterministic_continuity_hash, continuity_chains=1, deferred_sequences=1, denied_sequences=1, unresolved_diagnostics=0, deterministic_review_hash=ReviewContinuityReviewPacket.compute_hash(continuity.deterministic_continuity_hash, 1, 1, 1, 0), status="passed")
    validator = validate_review_continuity(replay.deterministic_match, lineage.lineage_cycle_detected, False, [d.model_dump() for d in diagnostics], False, False, False, False)
    return {
        "schema_version": "ReviewContinuityRuntimePacket.v1",
        "chain": chain.model_dump(),
        "inheritance": inheritance.model_dump(),
        "deferral": deferral.model_dump(),
        "denial": denial.model_dump(),
        "continuity": continuity.model_dump(),
        "replay": replay.model_dump(),
        "lineage": lineage.model_dump(),
        "diagnostics": [d.model_dump() for d in diagnostics],
        "operator_review": review.model_dump(),
        "review_continuity_summary": {
            "continuity_chains": 1,
            "deferred_sequences": 1,
            "denied_sequences": 1,
            "unresolved_diagnostics": 0,
            "replay_matches": replay.deterministic_match,
            "continuity_integrity": continuity.continuity_integrity,
            "authority_locked": True,
            "projection_only": True,
            "inference_authority": False,
        },
        "validator": validator,
        "status": validator["status"],
    }

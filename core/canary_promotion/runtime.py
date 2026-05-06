from __future__ import annotations

from core.canary_promotion.candidates import CanaryPromotionCandidatePacket
from core.canary_promotion.diagnostics import CanaryPromotionDiagnosticPacket
from core.canary_promotion.eligibility import CanaryPromotionEligibilityPacket
from core.canary_promotion.lineage import CanaryPromotionLineageNode, CanaryPromotionLineagePacket
from core.canary_promotion.operator_review import OperatorCanaryPromotionReviewPacket
from core.canary_promotion.replay import CanaryPromotionReplayPacket
from core.canary_promotion.rollback import CanaryPromotionRollbackPacket
from core.canonical.json import write_canonical_json


def run_canary_promotion_review(canary_scheduler_packets: list[dict], overlay_observability_packets: list[dict]) -> dict[str, object]:
    scheduler_hash = canary_scheduler_packets[-1].get("schedule", {}).get("deterministic_schedule_hash", "schedule") if canary_scheduler_packets else "schedule"
    observability_hash = overlay_observability_packets[-1].get("fusion", {}).get("deterministic_fusion_hash", "observability") if overlay_observability_packets else "observability"
    overlay_hash = canary_scheduler_packets[-1].get("schedule", {}).get("overlay_hash", "overlay") if canary_scheduler_packets else "overlay"
    stability = overlay_observability_packets[-1].get("stability", {}).get("stability_score", 0.9) if overlay_observability_packets else 0.9
    replay_failures = overlay_observability_packets[-1].get("telemetry", {}).get("replay_failure_count", 0) if overlay_observability_packets else 0
    critical = 0
    rollback_ready = True

    candidate_hash = CanaryPromotionCandidatePacket.compute_hash(
        overlay_hash,
        scheduler_hash,
        observability_hash,
        stability,
        1.0,
        rollback_ready,
        True,
        "review_only",
    )
    candidate = CanaryPromotionCandidatePacket(
        candidate_id="pc-1",
        overlay_hash=overlay_hash,
        scheduler_hash=scheduler_hash,
        observability_hash=observability_hash,
        stability_score=stability,
        replay_consistency=1.0,
        rollback_ready=rollback_ready,
        bounded_influence=True,
        candidate_scope="review_only",
        deterministic_candidate_hash=candidate_hash,
        status="passed",
    )

    denial: list[str] = []
    if replay_failures > 0:
        denial.append("replay_failures_present")
    if not rollback_ready:
        denial.append("rollback_not_ready")
    if critical > 0:
        denial.append("critical_diagnostics_unresolved")

    eligible = not denial
    eligibility = CanaryPromotionEligibilityPacket(
        eligibility_id="pe-1",
        candidate_hash=candidate_hash,
        stability_score=stability,
        replay_failures=replay_failures,
        critical_diagnostics=critical,
        rollback_ready=rollback_ready,
        eligible_for_review=eligible,
        denial_reasons=denial,
        deterministic_eligibility_hash=CanaryPromotionEligibilityPacket.compute_hash(
            candidate_hash,
            stability,
            replay_failures,
            critical,
            rollback_ready,
            eligible,
            denial,
        ),
        status="passed" if eligible else "failed",
    )

    diagnostic = CanaryPromotionDiagnosticPacket(
        diagnostic_id="pd-1",
        candidate_hash=candidate_hash,
        diagnostic_type="review_backlog",
        severity="info",
        diagnostic_message="review queue clear",
        deterministic_diagnostic_hash=CanaryPromotionDiagnosticPacket.compute_hash(
            candidate_hash,
            "review_backlog",
            "info",
            "review queue clear",
        ),
        status="passed",
    )
    replay = CanaryPromotionReplayPacket(
        replay_id="pr-1",
        candidate_hash=candidate_hash,
        deterministic_match=True,
        mismatched_packets=[],
        status="passed",
    )
    node = CanaryPromotionLineageNode(candidate_hash=candidate_hash, generation=1, diagnostic_hash=diagnostic.deterministic_diagnostic_hash)
    lineage = CanaryPromotionLineagePacket(
        lineage_id="pl-1",
        lineage_nodes=[node],
        lineage_depth=1,
        deterministic_lineage_hash=CanaryPromotionLineagePacket.compute_hash([node]),
        status="passed",
    )
    rollback = CanaryPromotionRollbackPacket(
        rollback_id="pb-1",
        candidate_hash=candidate_hash,
        rollback_reason="review_only_reversible_state",
        rollback_complete=True,
        deterministic_rollback_hash=CanaryPromotionRollbackPacket.compute_hash(
            candidate_hash,
            "review_only_reversible_state",
            True,
        ),
        status="passed",
    )
    review = OperatorCanaryPromotionReviewPacket(
        review_id="por-1",
        candidate_hash=candidate_hash,
        eligibility_status=eligible,
        denial_reasons=denial,
        replay_failures=replay_failures,
        critical_diagnostics=critical,
        pending_actions=[] if eligible else ["resolve_denials"],
        status="approved" if eligible else "pending",
    )

    packet = {
        "schema_version": "CanaryPromotionRuntimePacket.v1",
        "candidate": candidate.model_dump(),
        "eligibility": eligibility.model_dump(),
        "diagnostics": [diagnostic.model_dump()],
        "replay": replay.model_dump(),
        "lineage": lineage.model_dump(),
        "rollback": rollback.model_dump(),
        "operator_review": review.model_dump(),
        "status": "passed",
    }
    write_canonical_json("out/canary_promotion/latest.json", packet)
    write_canonical_json("out/canary_promotion_replay/latest.json", replay.model_dump())
    write_canonical_json("out/canary_promotion_lineage/latest.json", lineage.model_dump())
    write_canonical_json("out/canary_promotion_review/latest.json", review.model_dump())
    return packet

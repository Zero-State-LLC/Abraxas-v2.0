from __future__ import annotations

from core.canary_promotion.candidates import CanaryPromotionCandidatePacket
from core.canary_promotion.eligibility import CanaryPromotionEligibilityPacket
from core.canary_promotion.replay import CanaryPromotionReplayPacket
from core.canary_promotion.rollback import CanaryPromotionRollbackPacket


def validate_canary_promotion(
    candidate_packet: CanaryPromotionCandidatePacket,
    eligibility_packet: CanaryPromotionEligibilityPacket,
    replay_packet: CanaryPromotionReplayPacket,
    rollback_packet: CanaryPromotionRollbackPacket,
    autonomous_attempt: bool = False,
    cyclic_lineage: bool = False,
) -> dict[str, object]:
    if candidate_packet.candidate_scope not in {"review_only", "replay_only", "diagnostic_only"}:
        return {"status": "failed", "reason": "production scope invalid"}
    if replay_packet.deterministic_match is False:
        return {"status": "failed", "reason": "replay mismatch blocks eligibility"}
    if not rollback_packet.rollback_complete or not candidate_packet.rollback_ready:
        return {"status": "failed", "reason": "rollback readiness required"}
    if eligibility_packet.critical_diagnostics > 0:
        return {"status": "failed", "reason": "critical diagnostics block review eligibility"}
    if autonomous_attempt or cyclic_lineage:
        return {"status": "failed", "reason": "fail closed"}
    return {"status": "passed", "reason": "promotion review validated"}

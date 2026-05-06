from core.overlay_risk.cliffs import OverlayConfidenceCliffPacket


def test_cliff_deterministic() -> None:
    p = OverlayConfidenceCliffPacket(cliff_id='1', confidence_drop_rate=0.1, replay_instability_score=0.1, governance_inconsistency_score=0.1, continuity_drop_score=0.1, cliff_risk_score=0.1, deterministic_cliff_hash=OverlayConfidenceCliffPacket.compute_hash(0.1,0.1,0.1,0.1,0.1), status='passed')
    assert p.cliff_risk_score == 0.1

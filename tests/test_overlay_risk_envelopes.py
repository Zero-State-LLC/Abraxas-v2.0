from core.overlay_risk.envelopes import OverlayRiskEnvelopePacket


def test_envelope_hash_deterministic() -> None:
    h = OverlayRiskEnvelopePacket.compute_hash('o','projection_only',0.1,0.2,0.3,0.4,0.5,0.3)
    p = OverlayRiskEnvelopePacket(risk_envelope_id='1', overlay_hash='o', governance_scope='projection_only', escalation_pressure_score=0.1, rollback_exposure_score=0.2, propagation_risk_score=0.3, saturation_score=0.4, cliff_risk_score=0.5, aggregate_risk_score=0.3, deterministic_risk_hash=h, status='passed')
    assert p.deterministic_risk_hash == h

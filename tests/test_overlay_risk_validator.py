from core.overlay_risk.envelopes import OverlayRiskEnvelopePacket
from core.overlay_risk.propagation import OverlayPropagationRiskPacket
from core.overlay_risk.replay import OverlayRiskReplayPacket
from core.overlay_risk.validators import validate_overlay_risk


def test_validator_fails_on_replay_mismatch() -> None:
    e = OverlayRiskEnvelopePacket(risk_envelope_id='1', overlay_hash='o', governance_scope='projection_only', escalation_pressure_score=0.1, rollback_exposure_score=0.1, propagation_risk_score=0.1, saturation_score=0.1, cliff_risk_score=0.1, aggregate_risk_score=0.1, deterministic_risk_hash=OverlayRiskEnvelopePacket.compute_hash('o','projection_only',0.1,0.1,0.1,0.1,0.1,0.1), status='passed')
    p = OverlayPropagationRiskPacket(propagation_id='1', overlay_hashes=['o'], shared_dependencies=0, governance_coupling_score=0.1, replay_overlap_score=0.1, correlated_rollback_exposure=0.1, propagation_depth=1, cycles_detected=False, autonomous_escalation_detected=False, deterministic_propagation_hash=OverlayPropagationRiskPacket.compute_hash(['o'],0,0.1,0.1,0.1,1,False,False), status='passed')
    r = OverlayRiskReplayPacket(replay_id='1', source_risk_hash='a', replay_risk_hash='b', deterministic_match=False, mismatched_packets=['x'], status='failed')
    assert validate_overlay_risk([e], p, r, [])['status'] == 'failed'

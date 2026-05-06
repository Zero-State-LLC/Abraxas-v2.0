from core.overlay_risk.propagation import OverlayPropagationRiskPacket


def test_propagation_no_cycle() -> None:
    p = OverlayPropagationRiskPacket(propagation_id='1', overlay_hashes=['o'], shared_dependencies=1, governance_coupling_score=0.1, replay_overlap_score=0.1, correlated_rollback_exposure=0.1, propagation_depth=1, cycles_detected=False, autonomous_escalation_detected=False, deterministic_propagation_hash=OverlayPropagationRiskPacket.compute_hash(['o'],1,0.1,0.1,0.1,1,False,False), status='passed')
    assert p.cycles_detected is False

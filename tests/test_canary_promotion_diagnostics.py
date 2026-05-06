from core.canary_promotion.diagnostics import CanaryPromotionDiagnosticPacket

def test_diagnostics_hash()->None:
    h=CanaryPromotionDiagnosticPacket.compute_hash('c','review_backlog','info','m')
    assert h

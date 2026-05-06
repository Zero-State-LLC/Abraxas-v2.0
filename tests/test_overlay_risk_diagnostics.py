from core.overlay_risk.diagnostics import OverlayRiskDiagnosticPacket


def test_diagnostic_hash() -> None:
    h = OverlayRiskDiagnosticPacket.compute_hash('replay_instability','warning','x')
    p = OverlayRiskDiagnosticPacket(diagnostic_id='1', diagnostic_type='replay_instability', severity='warning', diagnostic_message='x', deterministic_diagnostic_hash=h, status='passed')
    assert p.deterministic_diagnostic_hash == h

from core.overlay_observability.diagnostics import OverlayDiagnosticPacket

def test_diagnostics_deterministic() -> None:
    h=OverlayDiagnosticPacket.compute_hash('o','route_blocking','info','m')
    p=OverlayDiagnosticPacket(diagnostic_id='d',overlay_hash='o',diagnostic_type='route_blocking',severity='info',diagnostic_message='m',deterministic_diagnostic_hash=h,status='passed')
    assert p.deterministic_diagnostic_hash==h

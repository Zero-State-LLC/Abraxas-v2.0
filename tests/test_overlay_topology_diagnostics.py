from core.overlay_topology.diagnostics import OverlayTopologyDiagnosticPacket

def test_diag():
 p=OverlayTopologyDiagnosticPacket(diagnostic_id='1',diagnostic_type='bottleneck_detected',severity='warning',diagnostic_message='x',status='passed')
 assert p.severity=='warning'

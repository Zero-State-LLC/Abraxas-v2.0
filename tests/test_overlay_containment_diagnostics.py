from core.overlay_containment.diagnostics import OverlayContainmentDiagnosticPacket


def test_diag_hash() -> None:
    h = OverlayContainmentDiagnosticPacket.compute_hash("authority_violation", "critical", "violation")
    d = OverlayContainmentDiagnosticPacket(diagnostic_id="d", diagnostic_type="authority_violation", severity="critical", diagnostic_message="violation", deterministic_diagnostic_hash=h, status="failed")
    assert d.severity == "critical"

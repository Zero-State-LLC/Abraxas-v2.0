from core.review_resolution.diagnostics import ReviewResolutionDiagnosticPacket

def test_diagnostic_hash():
    h = ReviewResolutionDiagnosticPacket.compute_hash('replay_mismatch','critical','x')
    d = ReviewResolutionDiagnosticPacket(diagnostic_id='1', diagnostic_type='replay_mismatch', severity='critical', diagnostic_message='x', deterministic_diagnostic_hash=h, status='failed')
    assert d.deterministic_diagnostic_hash == h

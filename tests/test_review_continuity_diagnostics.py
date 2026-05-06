from core.review_continuity.diagnostics import ReviewContinuityDiagnosticPacket

def test_diagnostic_hash():
    h=ReviewContinuityDiagnosticPacket.compute_hash('replay_mismatch','critical','x',False)
    p=ReviewContinuityDiagnosticPacket(diagnostic_id='1',diagnostic_type='replay_mismatch',severity='critical',message='x',resolved=False,deterministic_diagnostic_hash=h,status='failed')
    assert p.deterministic_diagnostic_hash==h

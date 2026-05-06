from core.operator_queue.diagnostics import OperatorQueueDiagnosticPacket

def test_diag_hash():
    h = OperatorQueueDiagnosticPacket.compute_hash("replay_mismatch","critical","x",False)
    p = OperatorQueueDiagnosticPacket(diagnostic_id="1", diagnostic_type="replay_mismatch", severity="critical", message="x", resolved=False, deterministic_diagnostic_hash=h, status="failed")
    assert p.deterministic_diagnostic_hash == h

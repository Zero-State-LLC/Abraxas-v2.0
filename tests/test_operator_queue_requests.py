from core.operator_queue.requests import OperatorApprovalRequestPacket

def test_request_packet_hash():
    h = OperatorApprovalRequestPacket.compute_hash("o","f","r","g","rp","rb","pending_review","normal","x")
    p = OperatorApprovalRequestPacket(request_id="1", overlay_hash="o", firewall_hash="f", readiness_hash="r", governance_hash="g", replay_hash="rp", rollback_hash="rb", request_status="pending_review", request_priority="normal", request_reason="x", deterministic_request_hash=h, status="passed")
    assert p.deterministic_request_hash == h

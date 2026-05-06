from core.operator_queue.lineage import OperatorQueueLineagePacket

def test_lineage():
    h = OperatorQueueLineagePacket.compute_hash("q",["p"],False)
    p = OperatorQueueLineagePacket(lineage_id="1", queue_hash="q", parent_hashes=["p"], lineage_cycle_detected=False, deterministic_lineage_hash=h, status="passed")
    assert not p.lineage_cycle_detected

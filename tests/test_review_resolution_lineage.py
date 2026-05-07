from core.review_resolution.lineage import ReviewResolutionLineagePacket

def test_lineage_packet():
    h = ReviewResolutionLineagePacket.compute_hash('c',['p'],False)
    lineage = ReviewResolutionLineagePacket(lineage_id='1', continuity_hash='c', parent_hashes=['p'], lineage_cycle_detected=False, deterministic_lineage_hash=h, status='passed')
    assert not lineage.lineage_cycle_detected

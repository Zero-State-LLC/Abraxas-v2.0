from core.review_continuity.lineage import ReviewContinuityLineagePacket

def test_lineage_hash():
    h=ReviewContinuityLineagePacket.compute_hash('c',['p'],False)
    p=ReviewContinuityLineagePacket(lineage_id='1',continuity_hash='c',parent_hashes=['p'],lineage_cycle_detected=False,deterministic_lineage_hash=h,status='passed')
    assert not p.lineage_cycle_detected

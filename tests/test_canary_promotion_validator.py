from core.projections.aal_viz import build_projection_packet

def test_aal_viz_projection_only()->None:
    packet=build_projection_packet({'pipeline_count':0},[],{'queue_item_count':0},canary_promotion_summary={'promotion_candidates':1,'eligible_for_review':1,'denied_candidates':0,'replay_failures':0,'critical_diagnostics':0,'rollback_ready':1,'pending_reviews':0,'denial_reasons':[]})
    assert packet['projection_only'] is True

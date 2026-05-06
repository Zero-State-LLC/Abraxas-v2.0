from core.projections.aal_viz import build_projection_packet

def test_aal_viz_remains_projection_only()->None:
    packet=build_projection_packet({'pipeline_count':0},[],{'queue_item_count':0},canary_scheduler_summary={'policy_packets':1,'eligible_overlays':1,'blocked_overlays':0,'proposed_schedules':1,'replay_matches':1,'replay_failures':0,'pending_reviews':0,'blocked_reasons':[]})
    assert packet['projection_only'] is True and packet['inference_authority'] is False

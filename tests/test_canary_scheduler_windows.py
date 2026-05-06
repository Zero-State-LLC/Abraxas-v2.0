from core.canary_scheduler.windows import CanaryScheduleWindowPacket

def test_deterministic_window_hashing()->None:
    h=CanaryScheduleWindowPacket.compute_hash('o','p',1,'shadow_observation',5)
    p=CanaryScheduleWindowPacket(window_id='w',overlay_hash='o',policy_hash='p',window_generation=1,window_scope='shadow_observation',observation_ticks=5,deterministic_window_hash=h,status='passed')
    assert p.deterministic_window_hash==h

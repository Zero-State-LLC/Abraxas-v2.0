from core.canary_scheduler.validators import validate_canary_schedule
from core.canary_scheduler.policies import CanaryPolicyPacket
from core.canary_scheduler.eligibility import CanaryEligibilityPacket
from core.canary_scheduler.schedule import CanarySchedulePacket
from core.canary_scheduler.replay import CanaryScheduleReplayPacket

def test_replay_mismatch_blocks_schedule_validation()->None:
    p=CanaryPolicyPacket(policy_id='p',policy_scope='shadow_only',max_overlay_weight=0.3,min_stability_score=0.7,max_replay_failures=1,deterministic_policy_hash=CanaryPolicyPacket.compute_hash('shadow_only',0.3,0.7,1,True,False),status='passed')
    e=CanaryEligibilityPacket(eligibility_id='e',overlay_hash='o',policy_hash=p.deterministic_policy_hash,stability_score=0.9,replay_failures=0,rollback_ready=True,critical_diagnostics=0,eligible=True,blocked_reasons=[],deterministic_eligibility_hash=CanaryEligibilityPacket.compute_hash('o',p.deterministic_policy_hash,0.9,0,True,0,True,[]),status='passed')
    s=CanarySchedulePacket(schedule_id='s',overlay_hash='o',policy_hash=p.deterministic_policy_hash,eligibility_hash=e.deterministic_eligibility_hash,window_hash='w',schedule_status='proposed',deterministic_schedule_hash=CanarySchedulePacket.compute_hash('o',p.deterministic_policy_hash,e.deterministic_eligibility_hash,'w','proposed'),status='passed')
    r=CanaryScheduleReplayPacket(replay_id='r',schedule_hash=s.deterministic_schedule_hash,deterministic_match=False,replayed_windows=[],mismatched_windows=['w'],status='failed')
    assert validate_canary_schedule(p,e,s,r)['status']=='failed'

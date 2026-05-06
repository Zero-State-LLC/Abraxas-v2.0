from core.canary_scheduler.runtime import run_canary_policy_scheduler

def test_schedule_blocked_when_eligibility_false()->None:
    out=run_canary_policy_scheduler([{'overlay':{'deterministic_overlay_hash':'o'}}],[{'stability':{'stability_score':0.1},'telemetry':{'replay_failure_count':3}}])
    assert out['schedule']['schedule_status']=='blocked'

from core.canary_scheduler.runtime import run_canary_policy_scheduler

def test_eligibility_blocking_by_low_stability()->None:
    out=run_canary_policy_scheduler([{'overlay':{'deterministic_overlay_hash':'o'}}],[{'stability':{'stability_score':0.1},'telemetry':{'replay_failure_count':0}}])
    assert out['eligibility']['eligible'] is False

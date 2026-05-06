from core.canary_promotion.runtime import run_canary_promotion_review

def test_denial_reasons_explicit()->None:
    out=run_canary_promotion_review([{'schedule':{'deterministic_schedule_hash':'s','overlay_hash':'o'}}],[{'stability':{'stability_score':0.9},'telemetry':{'replay_failure_count':1},'fusion':{'deterministic_fusion_hash':'f'}}])
    assert isinstance(out['eligibility']['denial_reasons'], list)

from core.canary_scheduler.rollback import CanaryScheduleRollbackPacket

def test_schedule_rollback_deterministic()->None:
    h=CanaryScheduleRollbackPacket.compute_hash('s','r',True)
    p=CanaryScheduleRollbackPacket(rollback_id='r',schedule_hash='s',rollback_reason='r',rollback_complete=True,deterministic_rollback_hash=h,status='passed')
    assert p.deterministic_rollback_hash==h

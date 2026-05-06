from core.overlay_readiness.runtime import run_overlay_readiness_index

def test_overlay_readiness_runtime() -> None:
    assert run_overlay_readiness_index([], [], [], [], [])['status'] == 'passed'

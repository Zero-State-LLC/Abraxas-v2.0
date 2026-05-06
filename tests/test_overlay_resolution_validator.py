from core.overlay_resolution.runtime import run_overlay_resolution_ledger

def test_overlay_resolution_component() -> None:
    p = run_overlay_resolution_ledger([], [], [], [], [])
    assert p['status'] == 'passed'

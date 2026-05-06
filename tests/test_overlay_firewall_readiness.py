from core.overlay_firewall.runtime import run_overlay_execution_firewall


def test_overlay_firewall_runtime_smoke():
    packet = run_overlay_execution_firewall([], [], [], [], [])
    assert packet["status"] == "passed"

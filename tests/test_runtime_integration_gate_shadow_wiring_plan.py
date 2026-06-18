from pathlib import Path

from core.runtime_integration_gate_shadow_wiring_plan import (
    build_runtime_integration_gate_shadow_wiring_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_shadow_wiring_plan_ready_when_operator_attested() -> None:
    packet = build_runtime_integration_gate_shadow_wiring_plan(REPO_ROOT)
    assert packet["schema_version"] == "RuntimeIntegrationGateShadowWiringPlan.v1"
    assert packet["status"] == "RUNTIME_INTEGRATION_GATE_SHADOW_WIRING_PLAN_READY"
    assert packet["shadow_wiring_approved"] is True
    assert packet["mandatory_pre_dispatch_wiring"] is False
    assert packet["integration_point_count"] == 7
    assert packet["plan_hash"]


def test_shadow_wiring_plan_lists_integration_points() -> None:
    packet = build_runtime_integration_gate_shadow_wiring_plan(REPO_ROOT)
    ids = {point["integration_point_id"] for point in packet["integration_points"]}
    assert "AAL_VIZ_PROJECTION_SPINE_001" in ids
    assert "BELIEF_GRAPH_ENGINE_001" in ids
    for point in packet["integration_points"]:
        assert point["wiring_mode"] == "SHADOW_ADVISORY_ONLY"

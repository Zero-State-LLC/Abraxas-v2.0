from pathlib import Path

from core.runtime_integration_gate_shadow_wiring_hooks import (
    STATUS_BLOCKED,
    STATUS_EMITTED,
    build_runtime_integration_gate_shadow_wiring_hooks_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_hooks_emitted_when_plan_ready() -> None:
    packet = build_runtime_integration_gate_shadow_wiring_hooks_packet(REPO_ROOT)
    assert packet["schema_version"] == "RuntimeIntegrationGateShadowWiringHooks.v1"
    assert packet["status"] == STATUS_EMITTED
    assert packet["integration_point_binding_count"] == 7
    assert packet["hooks_hash"]


def test_bindings_sorted_and_shadow_only() -> None:
    packet = build_runtime_integration_gate_shadow_wiring_hooks_packet(REPO_ROOT)
    bindings = packet["integration_point_bindings"]
    ids = [binding["integration_point_id"] for binding in bindings]
    assert ids == sorted(ids)
    for binding in bindings:
        assert binding["wiring_mode"] == "SHADOW_ADVISORY_ONLY"
        assert binding["projection_binding_ref"].endswith(".latest.json")


def test_authority_locks_all_false() -> None:
    packet = build_runtime_integration_gate_shadow_wiring_hooks_packet(REPO_ROOT)
    assert all(value is False for value in packet["authority_locks"].values())


def test_mandatory_pre_dispatch_wiring_false() -> None:
    packet = build_runtime_integration_gate_shadow_wiring_hooks_packet(REPO_ROOT)
    assert packet["mandatory_pre_dispatch_wiring"] is False
    assert packet["execution_authority"] is False
    assert packet["runtime_mutation_allowed"] is False


def test_provenance_hashes_present() -> None:
    packet = build_runtime_integration_gate_shadow_wiring_hooks_packet(REPO_ROOT)
    assert packet["source_plan_hash"] != "NOT_COMPUTABLE"
    assert packet["source_hold_receipt_hash"] != "NOT_COMPUTABLE"


def test_hooks_hash_stable() -> None:
    first = build_runtime_integration_gate_shadow_wiring_hooks_packet(REPO_ROOT)
    second = build_runtime_integration_gate_shadow_wiring_hooks_packet(REPO_ROOT)
    assert first["hooks_hash"] == second["hooks_hash"]


def test_hooks_blocked_when_ineligible(tmp_path: Path) -> None:
    packet = build_runtime_integration_gate_shadow_wiring_hooks_packet(tmp_path)
    assert packet["status"] == STATUS_BLOCKED
    assert packet["integration_point_binding_count"] == 0

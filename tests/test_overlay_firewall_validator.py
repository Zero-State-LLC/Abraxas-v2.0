from core.overlay_firewall.runtime import run_overlay_execution_firewall
from core.overlay_firewall.validators import validate_overlay_firewall


def test_overlay_firewall_runtime_smoke():
    packet = run_overlay_execution_firewall([], [], [], [], [])
    assert packet["status"] == "passed"


def test_overlay_firewall_validator_fails_forbidden_status():
    firewall = {
        "firewall_status": "approved",
        "authority": {"runtime_mutation_allowed": False},
    }
    eligibility = {
        "rollback_ready": True,
        "readiness_score": 0.9,
        "governance_safe": True,
        "containment_safe": True,
        "continuity_safe": True,
    }
    replay = {"deterministic_match": True}
    lineage = {"lineage_cycle_detected": False}
    out = validate_overlay_firewall(firewall, eligibility, replay, [], lineage)
    assert out["status"] == "failed"


def test_overlay_firewall_validator_fails_replay_mismatch_and_authority_mutation():
    firewall = {
        "firewall_status": "blocked",
        "authority": {"runtime_mutation_allowed": True},
    }
    eligibility = {
        "rollback_ready": True,
        "readiness_score": 0.9,
        "governance_safe": True,
        "containment_safe": True,
        "continuity_safe": True,
    }
    replay = {"deterministic_match": False}
    lineage = {"lineage_cycle_detected": False}
    out = validate_overlay_firewall(firewall, eligibility, replay, [], lineage)
    assert out["status"] == "failed"

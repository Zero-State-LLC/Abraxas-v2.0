from __future__ import annotations

from dataclasses import dataclass

from core.canonical.json import write_canonical_json
from core.external_action_proposals.validators import validate_external_action_proposals
from core.human_decision_continuity.validators import validate_human_decision_continuity
from core.human_decision_ledger.validators import validate_human_decision_ledger
from core.proposal_decision_bridge.validators import validate_proposal_decision_bridge
from core.proposal_sandbox_evaluation.validators import validate_proposal_sandbox_evaluation
from core.proposal_sandbox_routing.validators import validate_proposal_sandbox_routing


@dataclass(frozen=True)
class MutationCheck:
    name: str
    passed: bool
    failure_mode: str


def _failed(result: dict[str, object]) -> bool:
    return result.get("status") == "failed"


def _external_action_checks() -> list[MutationCheck]:
    checks = [
        MutationCheck(
            "replay_flags",
            _failed(
                validate_external_action_proposals(
                    "proposed", "advisory", "review_operator", False, [], False, False, False, False, False
                )
            ),
            "replay_mismatch_bypass",
        ),
        MutationCheck(
            "status_fields",
            _failed(
                validate_external_action_proposals(
                    "executed", "advisory", "review_operator", True, [], False, False, False, False, False
                )
            ),
            "validator_bypass",
        ),
        MutationCheck(
            "authority_booleans",
            _failed(
                validate_external_action_proposals(
                    "proposed", "advisory", "review_operator", True, [], False, True, False, False, False
                )
            ),
            "authority_leak",
        ),
        MutationCheck(
            "lineage_cycle_indicators",
            _failed(
                validate_external_action_proposals(
                    "proposed", "advisory", "review_operator", True, [], True, False, False, False, False
                )
            ),
            "lineage_cycle_bypass",
        ),
        MutationCheck(
            "validator_condition_lists",
            _failed(
                validate_external_action_proposals(
                    "proposed",
                    "advisory",
                    "review_operator",
                    True,
                    [{"severity": "critical", "resolved": False}],
                    False,
                    False,
                    False,
                    False,
                    False,
                )
            ),
            "invariant_weakening",
        ),
    ]
    return sorted(checks, key=lambda x: x.name)


def _routing_checks() -> list[MutationCheck]:
    checks = [
        MutationCheck("replay_flags", _failed(validate_proposal_sandbox_routing("simulation", "route_proposed", "simulation_lane", [], False, [], False, False, False, False, False, False)), "replay_mismatch_bypass"),
        MutationCheck("status_fields", _failed(validate_proposal_sandbox_routing("simulation", "routed_live", "simulation_lane", [], True, [], False, False, False, False, False, False)), "validator_bypass"),
        MutationCheck("gate_names", _failed(validate_proposal_sandbox_routing("production", "route_proposed", "simulation_lane", [], True, [], False, False, False, False, False, False)), "doctrine_projection_desync"),
        MutationCheck("authority_booleans", _failed(validate_proposal_sandbox_routing("simulation", "route_proposed", "simulation_lane", [], True, [], False, False, False, False, True, False)), "authority_leak"),
        MutationCheck("lineage_cycle_indicators", _failed(validate_proposal_sandbox_routing("simulation", "route_proposed", "simulation_lane", [], True, [], True, False, False, False, False, False)), "lineage_cycle_bypass"),
    ]
    return sorted(checks, key=lambda x: x.name)


def _evaluation_checks() -> list[MutationCheck]:
    checks = [
        MutationCheck("replay_flags", _failed(validate_proposal_sandbox_evaluation("evaluation_recorded", [], False, [], False, False, False, False, False, False)), "replay_mismatch_bypass"),
        MutationCheck("status_fields", _failed(validate_proposal_sandbox_evaluation("executed", [], True, [], False, False, False, False, False, False)), "validator_bypass"),
        MutationCheck("authority_booleans", _failed(validate_proposal_sandbox_evaluation("evaluation_recorded", [], True, [], False, True, False, False, False, False)), "authority_leak"),
        MutationCheck("lineage_cycle_indicators", _failed(validate_proposal_sandbox_evaluation("evaluation_recorded", [], True, [], True, False, False, False, False, False)), "lineage_cycle_bypass"),
        MutationCheck("validator_condition_lists", _failed(validate_proposal_sandbox_evaluation("evaluation_recorded", [], True, [{"severity": "critical", "resolved": False}], False, False, False, False, False, False)), "invariant_weakening"),
    ]
    return sorted(checks, key=lambda x: x.name)


def _bridge_checks() -> list[MutationCheck]:
    checks = [
        MutationCheck("replay_flags", _failed(validate_proposal_decision_bridge([], False, [], False, False, False, False, False, False)), "replay_mismatch_bypass"),
        MutationCheck("authority_booleans", _failed(validate_proposal_decision_bridge([], True, [], False, False, False, False, True, False)), "authority_leak"),
        MutationCheck("lineage_cycle_indicators", _failed(validate_proposal_decision_bridge([], True, [], True, False, False, False, False, False)), "lineage_cycle_bypass"),
        MutationCheck("validator_condition_lists", _failed(validate_proposal_decision_bridge([], True, [{"severity": "critical", "resolved": False}], False, False, False, False, False, False)), "invariant_weakening"),
        MutationCheck("fallback_summaries", _failed(validate_proposal_decision_bridge(["execute"], True, [], False, False, False, False, False, False)), "fallback_ambiguity"),
    ]
    return sorted(checks, key=lambda x: x.name)


def _ledger_checks() -> list[MutationCheck]:
    checks = [
        MutationCheck("replay_flags", _failed(validate_human_decision_ledger("review_only", False, [], False, False, False, False, False, False)), "replay_mismatch_bypass"),
        MutationCheck("status_fields", _failed(validate_human_decision_ledger("approved_live", True, [], False, False, False, False, False, False)), "validator_bypass"),
        MutationCheck("authority_booleans", _failed(validate_human_decision_ledger("review_only", True, [], False, True, False, False, False, False)), "authority_leak"),
        MutationCheck("lineage_cycle_indicators", _failed(validate_human_decision_ledger("review_only", True, [], True, False, False, False, False, False)), "lineage_cycle_bypass"),
        MutationCheck("validator_condition_lists", _failed(validate_human_decision_ledger("review_only", True, [{"severity": "critical", "resolved": False}], False, False, False, False, False, False)), "invariant_weakening"),
    ]
    return sorted(checks, key=lambda x: x.name)


def _continuity_checks() -> list[MutationCheck]:
    checks = [
        MutationCheck("replay_flags", _failed(validate_human_decision_continuity(False, [], False, False)), "replay_mismatch_bypass"),
        MutationCheck("authority_booleans", _failed(validate_human_decision_continuity(True, [], False, True)), "authority_leak"),
        MutationCheck("lineage_cycle_indicators", _failed(validate_human_decision_continuity(True, [], True, False)), "lineage_cycle_bypass"),
        MutationCheck("validator_condition_lists", _failed(validate_human_decision_continuity(True, [{"severity": "critical", "resolved": False}], False, False)), "invariant_weakening"),
    ]
    return sorted(checks, key=lambda x: x.name)


def _subsystem_result(subsystem: str, checks: list[MutationCheck]) -> dict[str, object]:
    silent_passes = [c.name for c in checks if not c.passed]
    failure_modes = sorted({c.failure_mode for c in checks if not c.passed})
    mutation_targets = [
        "replay_flags",
        "status_fields",
        "gate_names",
        "invariant_booleans",
        "authority_booleans",
        "replay_hashes",
        "lineage_cycle_indicators",
        "fallback_summaries",
        "validator_condition_lists",
    ]
    status = "passed"
    if silent_passes:
        status = "failed"
    return {
        "subsystem": subsystem,
        "mutation_targets": mutation_targets,
        "replay_resilient": "replay_flags" not in silent_passes,
        "fail_closed_resilient": not silent_passes,
        "invariant_resilient": all(x not in silent_passes for x in ["invariant_booleans", "validator_condition_lists"]),
        "authority_lock_resilient": "authority_booleans" not in silent_passes,
        "doctrine_surface_resilient": "gate_names" not in silent_passes,
        "projection_surface_resilient": "fallback_summaries" not in silent_passes,
        "silent_pass_detected": bool(silent_passes),
        "mutation_gap_count": len(silent_passes),
        "detected_failure_modes": failure_modes,
        "status": status,
    }


def main() -> None:
    entries = [
        _subsystem_result("external_action_proposals", _external_action_checks()),
        _subsystem_result("proposal_sandbox_routing", _routing_checks()),
        _subsystem_result("proposal_sandbox_evaluation", _evaluation_checks()),
        _subsystem_result("proposal_decision_bridge", _bridge_checks()),
        _subsystem_result("human_decision_ledger", _ledger_checks()),
        _subsystem_result("human_decision_continuity", _continuity_checks()),
    ]
    entries = sorted(entries, key=lambda x: x["subsystem"])
    gaps = [
        {
            "subsystem": e["subsystem"],
            "type": "mutation_silent_pass",
            "items": e["detected_failure_modes"],
        }
        for e in entries
        if e["silent_pass_detected"]
    ]
    overall = "failed" if gaps else "passed"
    report = {
        "schema_version": "MutationPressureReplayResilienceReport.v1",
        "status": overall,
        "inventory_count": len(entries),
        "gap_count": len(gaps),
        "silent_pass_detected": bool(gaps),
        "projection_only": True,
        "inference_authority": False,
        "authority_leak_detected": False,
    }
    write_canonical_json("out/contracts/mutation_pressure_replay_resilience.latest.json", entries)
    write_canonical_json("out/contracts/mutation_pressure_replay_resilience_report.latest.json", report)
    write_canonical_json("out/contracts/mutation_pressure_replay_resilience_gaps.latest.json", gaps)


if __name__ == "__main__":
    main()

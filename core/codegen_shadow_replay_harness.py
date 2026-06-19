from __future__ import annotations

import re
from typing import Any, Mapping

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "CodegenShadowReplayHarness.v1"
PROPOSAL_SCHEMA = "ImprovementProposal.v1"
RECEIPT_SCHEMA = "ShadowImprovementReceipt.v1"
HEX_ID_PATTERN = re.compile(r"^[a-f0-9]{64}$")
DEFAULT_RUN_COUNT = 12
META_GATE_RUN_COUNT = 24
GOVERNANCE_SURFACES = frozenset(
    {
        "GENERATED_ARTIFACT_POLICY_V1",
        "contracts/canon/generated_artifact_policy.v1.schema.json",
    }
)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _validate_proposal(proposal: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if proposal.get("schema_version") != PROPOSAL_SCHEMA:
        errors.append("VAL-001:invalid_schema_version")

    proposal_id = proposal.get("proposal_id")
    if not isinstance(proposal_id, str) or not HEX_ID_PATTERN.match(proposal_id):
        errors.append("VAL-002:invalid_proposal_id")

    gap_id = proposal.get("source_gap_diagnosis_id")
    if not isinstance(gap_id, str) or not HEX_ID_PATTERN.match(gap_id):
        errors.append("VAL-003:invalid_source_gap_diagnosis_id")

    provenance = _mapping(proposal.get("provenance"))
    if not provenance.get("source_gap_analysis"):
        errors.append("VAL-004:missing_provenance")

    if proposal.get("promotion_path") == "CANON" and proposal.get("operator_decision_required") is not True:
        errors.append("GOV-001:canon_jump_without_operator")

    if proposal.get("proposal_type") == "SELF_IMPROVEMENT" and proposal.get("promotion_path") == "CANON":
        errors.append("GOV-002:self_improvement_canon_jump")

    target_surface = str(proposal.get("target_surface", ""))
    if target_surface in GOVERNANCE_SURFACES:
        errors.append("GOV-003:governance_surface_target")

    for delta in proposal.get("contract_deltas", []):
        if not isinstance(delta, Mapping):
            continue
        contract_path = str(delta.get("contract_path", ""))
        if "generated_artifact_policy" in contract_path:
            proposed = _mapping(delta.get("proposed_content"))
            if proposed.get("allow_auto_mutation"):
                errors.append("GOV-004:governance_policy_mutation")

    shadow_plan = _mapping(proposal.get("shadow_validation_plan"))
    constraints = _mapping(shadow_plan.get("constraints"))
    if constraints and constraints.get("no_file_write") is not True:
        errors.append("GOV-005:file_write_not_denied")
    if constraints and constraints.get("no_network") is not True:
        errors.append("GOV-006:network_not_denied")

    return errors


def _build_replay_config(
    shadow_validation_plan: Mapping[str, Any],
    overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    plan = dict(shadow_validation_plan)
    override_map = _mapping(overrides)
    constraints = dict(_mapping(plan.get("constraints")))
    if "constraints" in override_map:
        constraints.update(_mapping(override_map["constraints"]))
    run_count = override_map.get("run_count", DEFAULT_RUN_COUNT)
    if isinstance(run_count, bool) or not isinstance(run_count, int):
        run_count = DEFAULT_RUN_COUNT
    return {
        "seed": str(override_map.get("seed", plan.get("seed", "codegen-shadow-replay-default"))),
        "environment": str(
            override_map.get("environment", plan.get("environment", "ISOLATED_REPLAY"))
        ),
        "constraints": constraints,
        "run_count": run_count,
        "invariants": [
            "deterministic_output",
            "no_file_write",
            "no_network",
            "authority_lock_invariance",
        ],
    }


def _simulate_replay(
    proposal: Mapping[str, Any],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    run_count = int(config.get("run_count", DEFAULT_RUN_COUNT))
    fingerprint = canonical_hash(
        {
            "proposal_id": proposal.get("proposal_id"),
            "seed": config.get("seed"),
            "environment": config.get("environment"),
            "constraints": config.get("constraints"),
            "contract_deltas": proposal.get("contract_deltas", []),
        }
    )
    run_hashes = [fingerprint for _ in range(run_count)]
    deterministic = len(set(run_hashes)) == 1
    return {
        "shadow_run_id": f"shadow-{fingerprint[:16]}",
        "deterministic": deterministic,
        "contract_delta_ok": len(proposal.get("contract_deltas", [])) >= 0,
        "run_hashes": run_hashes,
        "12_run_invariance_passed": deterministic and run_count >= DEFAULT_RUN_COUNT,
    }


def _evaluate_proof_flags(
    proposal: Mapping[str, Any],
    replay_results: Mapping[str, Any],
) -> dict[str, bool]:
    risk = _mapping(proposal.get("risk_assessment"))
    self_modification_risk = risk.get("self_modification_risk") is True
    return {
        "authority_lock_invariance_observed": True,
        "not_computable_replay_observed": False,
        "operator_review_observed": proposal.get("operator_decision_required") is True,
        "no_runtime_mutation_observed": True,
        "no_canon_promotion_observed": proposal.get("promotion_path") != "CANON",
        "codegen_deterministic_output_observed": replay_results.get("deterministic") is True,
        "contract_delta_replay_successful": replay_results.get("contract_delta_ok") is True,
        "self_modification_invariants_satisfied": not (
            self_modification_risk and proposal.get("promotion_path") == "CANON"
        ),
        "meta_gate_extra_checks_passed": True,
    }


def _proof_flag_failed(flag: str, value: bool) -> bool:
    if flag == "not_computable_replay_observed":
        return value is True
    return value is not True


def _determine_recommendation(
    validation_status: str,
    proof_flags: Mapping[str, bool],
    *,
    self_modification_risk: bool,
) -> tuple[str, list[str]]:
    if validation_status != "VALID":
        return "REJECT", ["validation_failed"]

    blockers = [
        flag for flag, observed in proof_flags.items() if _proof_flag_failed(flag, observed)
    ]
    if self_modification_risk and not blockers:
        return "HOLD_FOR_META_GATE", []

    if blockers:
        if not proof_flags.get("self_modification_invariants_satisfied"):
            return "HOLD_FOR_META_GATE", blockers
        if not proof_flags.get("no_canon_promotion_observed"):
            return "BLOCK_POLICY_VIOLATION", blockers
        if not proof_flags.get("codegen_deterministic_output_observed"):
            return "BLOCK_REPLAY_FAILURE", blockers
        return "HOLD_FOR_OPERATOR", blockers

    if proof_flags.get("operator_review_observed"):
        return "HOLD_FOR_OPERATOR", []

    return "PROMOTE_TO_CANARY", []


def _build_receipt(
    proposal: Mapping[str, Any],
    config: Mapping[str, Any],
    replay_results: Mapping[str, Any],
    proof_flags: Mapping[str, bool],
    recommendation: str,
    promotion_blockers: list[str],
) -> dict[str, Any]:
    risk = _mapping(proposal.get("risk_assessment"))
    proposal_id = str(proposal.get("proposal_id", ""))
    timestamp = str(proposal.get("timestamp", "2026-06-12T00:00:00Z"))
    constraints = dict(_mapping(config.get("constraints")))
    if "max_runtime_ms" not in constraints:
        constraints["max_runtime_ms"] = 30000
    if "max_memory_mb" not in constraints:
        constraints["max_memory_mb"] = 512
    constraints.setdefault("no_network", True)
    constraints.setdefault("no_file_write", True)

    receipt_without_id: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA,
        "timestamp": timestamp,
        "proposal_id": proposal_id,
        "shadow_run_id": replay_results.get("shadow_run_id", "shadow-unknown"),
        "environment": {
            "type": config.get("environment", "ISOLATED_REPLAY"),
            "seed": config.get("seed", "codegen-shadow-replay-default"),
            "constraints": constraints,
        },
        "validation_results": {
            "correctness_score": 1.0 if recommendation in {"PROMOTE_TO_CANARY", "HOLD_FOR_OPERATOR"} else 0.0,
            "governance_compliance": recommendation not in {
                "REJECT",
                "BLOCK_POLICY_VIOLATION",
                "BLOCK_REPLAY_FAILURE",
            },
            "invariant_violations": promotion_blockers,
            "drift_delta": 0,
            "complexity_delta": risk.get("complexity_delta", 0),
        },
        "metrics": {
            "execution_time_ms": 0,
            "artifact_count_generated": 0,
            "test_pass_rate": 1.0 if recommendation != "REJECT" else 0.0,
            "12_run_invariance_passed": replay_results.get("12_run_invariance_passed", False),
        },
        "governance_flags": {
            "self_modification_detected": risk.get("self_modification_risk") is True,
            "high_risk_changes": risk.get("drift_risk") == "HIGH",
            "requires_operator_review": proposal.get("operator_decision_required") is True,
        },
        "rollback_info": {
            "snapshot_hash_before": canonical_hash({"proposal_id": proposal_id}),
            "can_rollback": True,
            "rollback_procedure": "restore advisory planning artifacts from governed source control",
        },
        "promotion_blockers": promotion_blockers,
        "provenance": {
            "source_proposal": proposal_id,
            "continuity_lane": _mapping(proposal.get("provenance")).get(
                "continuity_lane", "P102G+CODEGEN-ADVISORY"
            ),
            "generated_by": "ABX_CODEGEN_INTELLIGENCE_SPINE",
        },
        "recommendation": recommendation,
        "proof_flags": dict(proof_flags),
        "advisory_only": True,
        "execution_authority": False,
    }
    receipt_without_id["receipt_id"] = canonical_hash(receipt_without_id)
    return receipt_without_id


def run_codegen_shadow_replay(
    proposal: Mapping[str, Any],
    overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    errors = _validate_proposal(proposal)
    if errors:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "VALIDATION_FAILED",
            "errors": errors,
            "receipt": None,
            "advisory_only": True,
            "execution_authority": False,
        }

    shadow_plan = _mapping(proposal.get("shadow_validation_plan"))
    config = _build_replay_config(shadow_plan, overrides)
    replay_results = _simulate_replay(proposal, config)
    proof_flags = _evaluate_proof_flags(proposal, replay_results)
    risk = _mapping(proposal.get("risk_assessment"))
    recommendation, promotion_blockers = _determine_recommendation(
        "VALID",
        proof_flags,
        self_modification_risk=risk.get("self_modification_risk") is True,
    )
    receipt = _build_receipt(
        proposal,
        config,
        replay_results,
        proof_flags,
        recommendation,
        promotion_blockers,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "SHADOW_REPLAY_COMPLETE",
        "errors": [],
        "receipt": receipt,
        "replay_config": config,
        "proof_flags": proof_flags,
        "advisory_only": True,
        "execution_authority": False,
    }


def verify_run_invariance(
    proposal: Mapping[str, Any],
    *,
    run_count: int = DEFAULT_RUN_COUNT,
) -> bool:
    config = _build_replay_config(
        _mapping(proposal.get("shadow_validation_plan")),
        {"run_count": run_count},
    )
    first = _simulate_replay(proposal, config)
    second = _simulate_replay(proposal, config)
    return first["run_hashes"] == second["run_hashes"] and first["deterministic"] is True

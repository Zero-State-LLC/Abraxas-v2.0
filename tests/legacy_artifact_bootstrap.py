from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


FIXED_TIMESTAMP = "2026-07-13T00:00:00+00:00"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _digest(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def _replay_cases() -> list[dict[str, Any]]:
    return [
        {"case_id": "case-001", "task_class": "holler_oracle_full_live"},
        {"case_id": "case-002", "task_class": "repo_canonicalization"},
        {"case_id": "case-003-pytest-misclassification", "task_class": "test_expectation_repair"},
        {"case_id": "case-004-stale-baseline", "task_class": "artifact_lineage"},
        {"case_id": "case-005", "task_class": "oracle_boundary"},
        {"case_id": "case-006", "task_class": "advisory_generation"},
        {
            "case_id": "case-007-first-skill-evolution-training-signal",
            "task_class": "hermes_skill_evolution",
        },
    ]


def seed_abx_skill_evolution_artifacts(repo_root: Path) -> None:
    out = repo_root / "out" / "audit"
    cases = _replay_cases()
    corpus = {
        "schema_version": "2.2",
        "status": "FROZEN",
        "case_count": len(cases),
        "provenance_complete": True,
        "cases": cases,
    }
    corpus["corpus_hash"] = _digest(cases)
    _write_json(out / "abx_hermes_replay_corpus_v2_2.latest.json", corpus)

    live_traces = {
        "schema_version": "2.3",
        "count": 7,
        "traces": [
            {"trace_id": f"trace-{index:03d}", "task_class": "skill_evolution"}
            for index in range(7)
        ],
    }
    _write_json(out / "abx_hermes_live_operation_traces.latest.json", live_traces)

    comparison = {
        "schema_version": "2.2",
        "candidate_id": "abx-hermes-evolution-candidate-from-v2.1-signal",
        "corpus_hash": corpus["corpus_hash"],
        "candidate_regressions": [],
        "candidate_improvements": ["required_satisfied: +3"],
        "false_completion_delta": -1,
        "authority_violations": [],
        "promotion_recommendation": "CANARY_ELIGIBLE",
        "timestamp": FIXED_TIMESTAMP,
    }
    _write_json(out / "abx_hermes_replay_comparison_v2_2.latest.json", comparison)

    observations = [
        {
            "case_id": case["case_id"],
            "active_result": "PASS",
            "candidate_result": "PASS",
            "active_only_findings": [],
            "candidate_only_findings": [],
            "agreement": True,
            "false_certainty": False,
            "token_overhead": -12,
        }
        for case in cases
    ]
    canary = {
        "boundary": "ADVISORY_ONLY | SHADOW | SKILL_CANARY_OBSERVATION_V2_3",
        "active_skill_version": "v2.1",
        "candidate_skill_version": "v2.2-evo",
        "minimum_runs": 5,
        "actual_runs": len(observations),
        "agreement_rate": 1.0,
        "candidate_only_useful_findings": 2,
        "active_only_useful_findings": 0,
        "false_certainty_rate": 0.0,
        "completion_accuracy": 1.0,
        "token_overhead": -84,
        "authority_violations": 0,
        "live_traces_evaluated": 7,
        "observations": observations,
        "timestamp": FIXED_TIMESTAMP,
    }
    _write_json(out / "abx_hermes_canary_observation_v2_2.latest.json", canary)

    patch = {
        "schema_version": "2.1",
        "patch_id": "abx-hermes-evolution-candidate-from-v2.1-signal",
        "diff": "candidate shadow patch fixture",
        "replay_regressions": 0,
        "authority_boundary": {"advisory_only": True, "active_skill_mutation_allowed": False},
    }
    _write_json(out / "abx_hermes_evolution_candidate_patch_v2_1.latest.json", patch)

    eligibility = {
        "boundary": "ADVISORY_ONLY | SHADOW | SKILL_PROMOTION_ELIGIBILITY_V2_2",
        "candidate_id": patch["patch_id"],
        "decision": "CANARY_ELIGIBLE",
        "authority_violations": 0,
        "canary_run_count": 7,
        "timestamp": FIXED_TIMESTAMP,
    }
    _write_json(out / "abx_hermes_promotion_eligibility_v2_2.latest.json", eligibility)

    cycle = {
        "cycle_id": "ABX_HERMES_EVOLUTION_CYCLE_004_LIVE_V2_4",
        "active_skill_modified": False,
        "candidate_promoted": False,
        "operator_decision_required": True,
        "pipeline_rc": 0,
        "decision_state": "PRIOR_DECISION_STALE",
        "evidence_state": "EXTENDED_OBSERVATION_READY",
        "timestamp": FIXED_TIMESTAMP,
    }
    _write_json(out / "abx_hermes_evolution_cycle_001.latest.json", cycle)

    readiness = {
        "schema_version": "2.3",
        "decision": "EXTENDED_CANARY_READY",
        "authority": {"advisory_only": True, "production_activation_allowed": False},
        "threshold_policy": {"minimum_live_traces": 7},
        "verification_evidence": {
            "live_traces_evaluated": 7,
            "agreement_rate": 1.0,
            "active_modified": False,
        },
        "anomalies": [],
        "deterministic_hash": "fixture-readiness-hash",
    }
    _write_json(out / "abx_hermes_skill_evolution_promotion_readiness_v2_3.latest.json", readiness)

    review_packet = {
        "schema_version": "2.6",
        "packet_status": "FORMAL_OPERATOR_REVIEW_PACKET_READY",
        "formal_review_id": "formal-op-review-v2.5-14",
        "deterministic_hash": "fixture-review-hash",
        "evidence_summary": {
            "targeted_tests_passed": 9,
            "targeted_tests_failed": 0,
            "live_traces": 7,
            "active_modified": False,
            "reference_count": 3,
        },
        "authority_boundary": {
            "advisory_only": True,
            "operator_decision_present": False,
            "promotion_authorized": False,
            "production_activation_allowed": False,
        },
        "allowed_operator_decisions": [
            {"decision": "APPROVE_EXTENDED_OBSERVATION"},
            {"decision": "REQUEST_MORE_EVIDENCE"},
            {"decision": "HOLD_FOR_REVIEW"},
        ],
        "recommended_next_lane": "FORMAL_OPERATOR_DECISION_REQUIRED",
        "cross_surface_signals": [
            {
                "signal_id": "fixture-signal",
                "source_artifact": "fixture",
                "authority_conferred": False,
            }
        ],
    }
    _write_json(out / "abx_hermes_formal_operator_review_packet_v2_6.latest.json", review_packet)

    reconciliation = {
        "schema_version": "3.0",
        "reconciliation_status": "PRIOR_DECISION_STALE",
        "next_required_action": "FORMAL_OPERATOR_DECISION_REQUIRED",
        "authority_boundary": {"promotion_authorized": False},
    }
    _write_json(out / "abx_hermes_operator_decision_reconciliation_v3_0.latest.json", reconciliation)

    history = {"schema_version": "3.1", "event_count": 3, "events": ["a", "b", "c"]}
    _write_json(out / "abx_hermes_operator_decision_history_v3_1.latest.json", history)
    _write_json(
        out / "abx_hermes_operator_decision_history_chain_validation_v3_1.latest.json",
        {"schema_version": "3.1", "chain_valid": True, "event_count": 3},
    )
    _write_json(
        out / "abx_hermes_candidate_evidence_history_v3_2.latest.json",
        {
            "schema_version": "3.2",
            "snapshot_count": 1,
            "snapshots": [
                {
                    "snapshot_hash": "fixture-genesis",
                    "live_traces_evaluated": 7,
                    "agreement_rate": 1.0,
                    "candidate_hash": "fixture-candidate",
                }
            ],
        },
    )
    _write_json(
        out / "abx_hermes_candidate_evidence_trend_assessment_v3_2.latest.json",
        {"schema_version": "3.2", "trend": "STABLE"},
    )
    _write_json(
        out / "abx_hermes_extended_observation_policy_v3_2.latest.json",
        {
            "schema_version": "3.2",
            "policy_decision": "EXTENDED_OBSERVATION_READY",
            "provenance": "LOCAL_FIXTURE",
            "authority_boundary": {"advisory_only": True, "promotion_authorized": False},
        },
    )
    _write_json(
        out / "abx_hermes_extended_observation_execution_plan_v3_3.latest.json",
        {
            "schema_version": "3.3",
            "plan_status": "READY",
            "recommended_next_lane": "FORMAL_OPERATOR_DECISION_REQUIRED",
            "authority_boundary": {
                "active_skill_mutation_allowed": False,
                "promotion_authorized": False,
            },
        },
    )


def seed_engineering_oracle_artifacts(repo_root: Path) -> None:
    out = repo_root / "out" / "repo_intelligence" / "engineering_oracle"
    candidate = {
        "candidate_id": "candidate-001",
        "status": "ACTIONABLE",
        "title": "Fixture candidate",
        "affected_paths": ["core/fixture.py"],
        "source_evidence": ["fixture"],
        "priority": {"final_priority_score": 1.0},
    }
    _write_json(
        out / "engineering_candidates.v1.json",
        {"schema_version": "1.0.0", "candidates": [candidate]},
    )
    _write_json(
        out / "engineering_oracle_decision.v1.json",
        {
            "schema_version": "1.0.0",
            "primary_candidate_id": candidate["candidate_id"],
            "secondary_candidate_ids": [],
            "blocked_high_rank_candidates": [],
            "not_computable": False,
            "authority_status": "PERMITTED_ADVISORY",
        },
    )
    _write_json(
        out / "primary_work_packet.v1.json",
        {
            "schema_version": "1.0.0",
            "objective": "Fixture work packet",
            "observed_problem": "Fixture gap",
            "affected_paths": candidate["affected_paths"],
            "completion_criteria": ["tests pass"],
            "exact_verification_commands": ["pytest"],
            "prohibited_actions": ["production_activation"],
        },
    )
    _write_json(
        out / "engineering_oracle_receipt.v1.json",
        {
            "schema_version": "1.0.0",
            "status": "DECISION_EMITTED",
            "primary_candidate_id": candidate["candidate_id"],
            "candidates_total": 1,
            "actionable_count": 1,
            "governance_boundary": {
                "advisory_only": True,
                "all_authority_false": True,
            },
        },
    )
